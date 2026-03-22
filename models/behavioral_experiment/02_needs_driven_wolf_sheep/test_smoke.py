from __future__ import annotations

import sys
from pathlib import Path


# Allow running this test directly from the model folder without installing Mesa.
REPO_ROOT = Path(__file__).resolve().parents[3]
MESA_SOURCE_ROOT = REPO_ROOT / "mesa"
if str(MESA_SOURCE_ROOT) not in sys.path:
	sys.path.insert(0, str(MESA_SOURCE_ROOT))


def _small_scenario(seed: int = 42):
	from model import NeedsDrivenWolfSheepScenario

	return NeedsDrivenWolfSheepScenario(
		rng=seed,
		width=10,
		height=10,
		initial_sheep=30,
		initial_wolves=8,
		sheep_reproduce=0.04,
		wolf_reproduce=0.03,
		wolf_gain_from_food=16.0,
		sheep_gain_from_food=4.0,
		grass=True,
		grass_regrowth_time=12,
	)


def test_model_initializes():
	from model import NeedsDrivenWolfSheepModel

	m = NeedsDrivenWolfSheepModel(scenario=_small_scenario())
	assert m.time == 0
	assert m.running is True
	assert len(m.agents) > 0

	df = m.datacollector.get_model_vars_dataframe()
	assert len(df) == 1


def test_model_runs_10_steps_and_collects_data():
	from model import NeedsDrivenWolfSheepModel

	m = NeedsDrivenWolfSheepModel(scenario=_small_scenario())
	for _ in range(10):
		m.step()

	assert m.time == 10
	df = m.datacollector.get_model_vars_dataframe()
	assert len(df) == 11


def test_datacollector_has_expected_columns():
	from model import NeedsDrivenWolfSheepModel

	m = NeedsDrivenWolfSheepModel(scenario=_small_scenario())
	m.step()

	df = m.datacollector.get_model_vars_dataframe()
	expected = {
		"Wolves",
		"Sheep",
		"Grass",
		"AvgSheepFear",
		"MaxSheepFear",
		"AvgSheepFatigue",
		"AvgSheepHunger",
		"FleeCount",
		"ForageCount",
		"RestCount",
		"WanderCount",
	}
	assert expected.issubset(set(df.columns))


def test_action_counts_are_non_negative():
	from model import NeedsDrivenWolfSheepModel

	m = NeedsDrivenWolfSheepModel(scenario=_small_scenario())
	m.step()
	row = m.datacollector.get_model_vars_dataframe().iloc[-1]

	for key in ("FleeCount", "ForageCount", "RestCount", "WanderCount"):
		assert row[key] >= 0


def test_grass_metric_zero_when_grass_disabled():
	from model import NeedsDrivenWolfSheepModel, NeedsDrivenWolfSheepScenario

	scenario = NeedsDrivenWolfSheepScenario(
		rng=42,
		width=10,
		height=10,
		initial_sheep=20,
		initial_wolves=5,
		grass=False,
	)
	m = NeedsDrivenWolfSheepModel(scenario=scenario)
	m.step()

	row = m.datacollector.get_model_vars_dataframe().iloc[-1]
	assert row["Grass"] == 0


def test_seeded_run_advances_time_consistently():
	from model import NeedsDrivenWolfSheepModel

	m1 = NeedsDrivenWolfSheepModel(scenario=_small_scenario(seed=42))
	m2 = NeedsDrivenWolfSheepModel(scenario=_small_scenario(seed=123))

	m1.step()
	m2.step()
	assert m1.time == m2.time == 1


if __name__ == "__main__":
	test_model_initializes()
	test_model_runs_10_steps_and_collects_data()
	test_datacollector_has_expected_columns()
	test_action_counts_are_non_negative()
	test_grass_metric_zero_when_grass_disabled()
	test_seeded_run_advances_time_consistently()
	print("All tests passed!")
