from __future__ import annotations

import sys
from pathlib import Path


# Allow running this test directly from the model folder without installing Mesa.
REPO_ROOT = Path(__file__).resolve().parents[3]
MESA_SOURCE_ROOT = REPO_ROOT / "mesa"
if str(MESA_SOURCE_ROOT) not in sys.path:
	sys.path.insert(0, str(MESA_SOURCE_ROOT))


def _build_model(seed: int = 42):
	from model import OpinionDiffusionModel

	return OpinionDiffusionModel(
		num_agents=20,
		avg_degree=5,
		learning_rate=0.1,
		contrarian_probability=0.2,
		rng=seed,
	)


def test_model_initializes():
	m = _build_model(seed=42)
	assert m.round == 0
	assert m.time == 0
	assert len(m.agents) == 20
	assert len(m.history) == 1

	first = m.history[0]
	for key in ("round", "mean_opinion", "min_opinion", "max_opinion"):
		assert key in first


def test_model_runs_10_steps():
	m = _build_model(seed=42)
	for _ in range(10):
		m.step()

	assert m.round == 10
	assert m.time == 10
	assert len(m.history) == 11
	assert m.history[-1]["round"] == 10


def test_opinions_stay_in_unit_interval():
	from agents import OpinionAgent

	m = _build_model(seed=42)
	for _ in range(15):
		m.step()

	for agent in m.agents_by_type[OpinionAgent]:
		assert 0.0 <= agent.opinion <= 1.0


def test_agents_receive_neighbor_messages():
	from agents import OpinionAgent

	m = _build_model(seed=42)
	m.step()

	received_total = sum(
		agent.messages_received for agent in m.agents_by_type[OpinionAgent]
	)
	assert received_total > 0


def test_seeded_runs_advance_consistently():
	m1 = _build_model(seed=42)
	m2 = _build_model(seed=123)

	m1.step()
	m2.step()

	assert m1.round == m2.round == 1
	assert m1.time == m2.time == 1
	assert len(m1.history) == len(m2.history) == 2


if __name__ == "__main__":
	test_model_initializes()
	test_model_runs_10_steps()
	test_opinions_stay_in_unit_interval()
	test_agents_receive_neighbor_messages()
	test_seeded_runs_advance_consistently()
	print("All tests passed!")
