from mesa.discrete_space import CellAgent, FixedAgent


class Animal(CellAgent):
    """Base class for animal."""

    def __init__(self, model, energy=8, p_reproduce=0.04, energy_from_food=4, cell=None):
        super().__init__(model)
        self.energy = energy
        self.p_reproduce = p_reproduce
        self.energy_from_food = energy_from_food
        self.cell = cell

    def spawn_offspring(self):
        self.energy /= 2
        self.__class__(
            self.model,
            self.energy,
            self.p_reproduce,
            self.energy_from_food,
            self.cell
        )

    def feed(self):
        """Implemented in subclasses."""

    def move(self):
        """Implemented in subclasses."""


class Sheep(Animal):
    """
    Needs-driven sheep with internal drives:
    - Hunger (tracked separately from energy for observation purposes)
    - fear (rises near wolves, drops when wolves are far away)
    - fatigue (rises with effort, rests when resting)
    """

    def __init__(
        self,
        model,
        energy=8,
        p_reproduce=0.04,
        energy_from_food=4,
        cell=None,
        hunger=0,
        fear=0,
        fatigue=0,
    ):
        super().__init__(model, energy, p_reproduce, energy_from_food, cell)
        self.hunger = hunger
        self.fear = fear
        self.fatigue = fatigue
        self.last_action = "wander"

    def _neighbor_wolves(self):
        wolves = []
        for cell in self.cell.neighborhood:
            for agent in cell.agents:
                if isinstance(agent, Wolf):
                    wolves.append(agent)
        return wolves
    
    def update_drives(self):
        wolves_near = self._neighbor_wolves()

        # Fear rises when wolves are near.
        if wolves_near:
            self.fear += 6
        
        # Hunger rises when energy is low.
        self.hunger = max(0, 10 - self.energy)

    def select_action(self):
        """Choose the highest-priority action based on current drives."""
        if self.fear > 4:
            return "flee"
        elif self.energy < 3:
            return "forage"
        elif self.fatigue > 15:
            return "rest"
        else:
            return "wander"
        
    def feed(self):
        grass_patch = next(
            (obj for obj in self.cell.agents if isinstance(obj, GrassPatch)),
            None
        )
        if grass_patch is not None and grass_patch.fully_grown:
            self.energy += self.energy_from_food
            grass_patch.get_eaten()
            self.hunger = max(0, self.hunger - self.energy_from_food)
    
    def move(self):
        """
        Move to safe cell, preferring grass among safe cells.
        If no safe cells exist, stay put.
        """
        cells_without_wolves = []
        cells_with_grass = []

        for cell in self.cell.neighborhood:
            has_wolf = False
            has_grass = False

            for obj in cell.agents:
                if isinstance(obj, Wolf):
                    has_wolf = True
                if isinstance(obj, GrassPatch) and obj.fully_grown:
                    has_grass = True
            
            if not has_wolf:
                cells_without_wolves.append(cell)
                if has_grass:
                    cells_with_grass.append(cell)

        if len(cells_without_wolves) == 0:
            return
        
        target_cells = (
            cells_with_grass if len(cells_with_grass) > 0 else cells_without_wolves
        )
        self.cell = self.random.choice(target_cells)

    def flee_from_wolves(self):
        """
        Move to the neighboring cell that maximizes distance from wolves.
        If no wolves are nearby, fallback to normal movement.
        """
        wolves = self._neighbor_wolves()
        if not wolves:
            self.move()
            return

        wolf_positions = [wolf.cell.coordinate for wolf in wolves]
        candidate_cells = list(self.cell.neighborhood)

        if not candidate_cells:
            return
        
        def min_manhattan_distance_to_wolves(cell):
            cx, cy = cell.coordinate
            return min(abs(cx - wx) + abs(cy - wy) for wx, wy in wolf_positions)
        
        best_score = max(min_manhattan_distance_to_wolves(cell) for cell in candidate_cells)
        best_cells = [cell for cell in candidate_cells if min_manhattan_distance_to_wolves(cell) == best_score]
        self.cell = self.random.choice(best_cells)

    def step(self):
        self.update_drives()
        action = self.select_action()
        self.last_action = action

        rested = False

        if action == "flee":
            self.flee_from_wolves()
        elif action == "forage":
            self.move()
            self.feed()
        elif action == "rest":
            self.fatigue = 0
            rested = True
        else:
            self.move()
        
        self.energy -= 1
        if not rested:
            self.fatigue += 1

        # Global fear decay; if wolves were nearby this tick, net fear can still rise.
        self.fear = max(0, self.fear - 1)

        if self.energy < 0:
            self.remove()
        elif self.random.random() < self.p_reproduce:
            self.spawn_offspring()


class Wolf(Animal):
    """Wolf behavior is kept close to mesa baseline"""
    
    def feed(self):
        sheep = [obj for obj in self.cell.agents if isinstance(obj, Sheep)]
        if sheep:
            sheep_to_eat = self.random.choice(sheep)
            self.energy += self.energy_from_food
            sheep_to_eat.remove()
    
    def move(self):
        cells_with_sheep = self.cell.neighborhood.select(
            lambda cell: any(isinstance(obj, Sheep) for obj in cell.agents)
        )
        target_cells = (
            cells_with_sheep if len(cells_with_sheep) > 0 else self.cell.neighborhood
        )
        self.cell = target_cells.select_random_cell()

    def step(self):
        self.move()
        self.energy -= 1
        self.feed()

        if self.energy < 0:
            self.remove()
        elif self.random.random() < self.p_reproduce:
            self.spawn_offspring()


class GrassPatch(FixedAgent):
    """A patch of grass that regrows after being eaten."""

    def __init__(self, model, countdown, grass_regrowth_time, cell):
        super().__init__(model)
        self.fully_grown = countdown == 0
        self.grass_regrowth_time = grass_regrowth_time
        self.cell = cell

        if not self.fully_grown:
            self.model.schedule_event(self.regrow, after=countdown)

    def regrow(self):
        self.fully_grown = True

    def get_eaten(self):
        self.fully_grown = False
        self.model.schedule_event(self.regrow, after=self.grass_regrowth_time)