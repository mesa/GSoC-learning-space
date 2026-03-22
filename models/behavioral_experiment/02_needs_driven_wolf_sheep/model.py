"""
Needs-Driven Wolf-Sheep Predation Model.

Adds sheep internal drives (fear, fatigue, hunger) and priority-based action selection to expose behavior-selection friction.
"""

import math

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalVonNeumannGrid
from mesa.experimental.scenarios import Scenario

try:
    from .agents import GrassPatch, Sheep, Wolf
except ImportError:
    from agents import GrassPatch, Sheep, Wolf


class NeedsDrivenWolfSheepScenario(Scenario):
    width: int = 20
    height: int = 20
    initial_sheep: int = 100
    initial_wolves: int = 50
    sheep_reproduce: float = 0.04
    wolf_reproduce: float = 0.05
    wolf_gain_from_food: float = 20.0
    grass: bool = True
    grass_regrowth_time: int = 30
    sheep_gain_from_food: float = 4.0


class NeedsDrivenWolfSheepModel(Model):
    description = "Needs-Driven wolf-sheep model with priority-based sheep actions."

    def __init__(
        self,
        scenario: NeedsDrivenWolfSheepScenario = NeedsDrivenWolfSheepScenario,
    ):
        super().__init__(scenario=scenario)

        self.height = scenario.height
        self.width = scenario.width
        self.grass = scenario.grass

        self.grid = OrthogonalVonNeumannGrid(
            [self.height, self.width],
            torus=True,
            capacity=math.inf,
            random=self.random,
        )

        self.datacollector = DataCollector(
            model_reporters={
                "Wolves": lambda m: len(m.agents_by_type[Wolf]),
                "Sheep": lambda m: len(m.agents_by_type[Sheep]),
                "Grass": lambda m: (
                    len(m.agents_by_type[GrassPatch].select(lambda a: a.fully_grown))
                    if m.grass
                    else 0
                ),
                "AvgSheepFear": lambda m: m._avg_sheep_attr("fear"),
                "MaxSheepFear": lambda m: m._max_sheep_attr("fear"),
                "AvgSheepFatigue": lambda m: m._avg_sheep_attr("fatigue"),
                "AvgSheepHunger": lambda m: m._avg_sheep_attr("hunger"),
                "FleeCount": lambda m: m._count_sheep_action("flee"),
                "ForageCount": lambda m: m._count_sheep_action("forage"),
                "RestCount": lambda m: m._count_sheep_action("rest"),
                "WanderCount": lambda m: m._count_sheep_action("wander"),
            }
        )

        Sheep.create_agents(
            self,
            scenario.initial_sheep,
            energy=self.rng.random((scenario.initial_sheep,))
            * 2
            * scenario.sheep_gain_from_food,
            p_reproduce=scenario.sheep_reproduce,
            energy_from_food=scenario.sheep_gain_from_food,
            cell=self.random.choices(
                self.grid.all_cells.cells,
                k=scenario.initial_sheep,
            ),
            hunger=0,
            fear=0,
            fatigue=0,
        )

        Wolf.create_agents(
            self,
            scenario.initial_wolves,
            energy=self.rng.random((scenario.initial_wolves,))
            * 2
            * scenario.wolf_gain_from_food,
            p_reproduce=scenario.wolf_reproduce,
            energy_from_food=scenario.wolf_gain_from_food,
            cell=self.random.choices(
                self.grid.all_cells.cells,
                k=scenario.initial_wolves,
            ),
        )

        if self.grass:
            possibly_fully_grown = [True, False]
            for cell in self.grid:
                fully_grown = self.random.choice(possibly_fully_grown)
                countdown = (
                    0
                    if fully_grown
                    else self.random.randrange(0, scenario.grass_regrowth_time)
                )
                GrassPatch(self, countdown, scenario.grass_regrowth_time, cell)

        self.running = True
        self.datacollector.collect(self)

    def _avg_sheep_attr(self, attr):
        sheep = list(self.agents_by_type[Sheep])
        if not sheep:
            return 0.0
        return sum(getattr(s, attr, 0.0) for s in sheep) / len(sheep)

    def _max_sheep_attr(self, attr):
        sheep = list(self.agents_by_type[Sheep])
        if not sheep:
            return 0.0
        return max(getattr(s, attr, 0.0) for s in sheep)

    def _count_sheep_action(self, action_name):
        return sum(
            1 for s in self.agents_by_type[Sheep] if s.last_action == action_name
        )

    def step(self):
        self.agents_by_type[Sheep].shuffle_do("step")
        self.agents_by_type[Wolf].shuffle_do("step")
        self.datacollector.collect(self)
