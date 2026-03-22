# Model 02: Needs-Driven Wolf-Sheep

## Goal

Show friction in behavior selection when internal drives compete in a step-coupled policy.

## Model Setup

- Baseline wolf-sheep model is extended with sheep internal drives.
- Sheep track hunger, fear, and fatigue.
- Sheep select one action per step using priority rules:
  - flee if fear > 4
  - forage if energy < 3
  - rest if fatigue > 15
  - otherwise wander
- Wolves and grass remain close to baseline behavior.

## Reproducible Run

Parameters used:

- initial_sheep = 180
- initial_wolves = 8
- sheep_reproduce = 0.08
- wolf_reproduce = 0.015
- wolf_gain_from_food = 12.0
- sheep_gain_from_food = 6.0
- grass_regrowth_time = 12
- steps = 80

Run snippet:

~~~python
from model import NeedsDrivenWolfSheepModel, NeedsDrivenWolfSheepScenario

s = NeedsDrivenWolfSheepScenario(
  initial_sheep=180,
  initial_wolves=8,
  sheep_reproduce=0.08,
  wolf_reproduce=0.015,
  wolf_gain_from_food=12.0,
  sheep_gain_from_food=6.0,
  grass_regrowth_time=12,
)

m = NeedsDrivenWolfSheepModel(scenario=s)
for _ in range(80):
  m.step()

df = m.datacollector.get_model_vars_dataframe()
print(df.tail(1).to_dict("records")[0])
~~~

## Results Snapshot

Observed final-row output:

- Wolves = 10
- Sheep = 106
- Grass = 167
- AvgSheepFear = 0.6792452830188679
- MaxSheepFear = 14
- AvgSheepFatigue = 5.669811320754717
- AvgSheepHunger = 4.010300300250699
- FleeCount = 10
- ForageCount = 29
- RestCount = 4
- WanderCount = 63

Interpretation:

- Coexistence remains stable enough for analysis at step 80.
- Fear spikes occur (MaxSheepFear = 14) while average fear stays modest.
- All action branches are active, so priority arbitration is visible in collected metrics.

## Mesa Friction Point

Behavior selection logic is embedded directly inside the step method.

- action priorities are hard-coded per model
- transitions are not reusable across agent types
- one-step arbitration and action execution are tightly coupled

This makes behavior policies harder to compare, test, and reuse.

## Minimal API Idea

An opt-in behavior layer could separate policy from execution:

- register_behavior(name, condition, priority)
- choose_behavior() for arbitration
- start_action() integration for duration and interruption
- behavior telemetry hooks for analysis

This would preserve current Mesa patterns while reducing policy boilerplate.

## What I Learned

- Priority thresholds strongly control branch activation and emergent dynamics.
- Avg metrics alone can hide episodic dynamics; max and action counts are essential.
- A reusable behavior-selection abstraction would improve readability and experimentation speed.

## Next Experiment

- Add radius-2 threat sensing and compare panic propagation.
- Track per-agent action transitions to quantify policy stability.
- Compare step-coupled policy against an Action-based interruptible policy prototype.
