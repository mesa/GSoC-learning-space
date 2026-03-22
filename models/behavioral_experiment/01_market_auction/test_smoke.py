from __future__ import annotations

import sys
from pathlib import Path


# Allow running this test directly from the model folder without installing Mesa.
REPO_ROOT = Path(__file__).resolve().parents[3]
MESA_SOURCE_ROOT = REPO_ROOT / "mesa"
if str(MESA_SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(MESA_SOURCE_ROOT))


def test_model_runs_10_steps():
    from model import MarketAuctionModel

    m = MarketAuctionModel(rng=42)
    for _ in range(10):
        m.step()
    assert len(m.round_log) == 10
    assert m.time == 10
    assert len(m.agents) > 0


def test_model_initialization():
    from model import MarketAuctionModel

    m = MarketAuctionModel(rng=42)
    assert m.time == 0
    assert len(m.round_log) == 0


def test_model_with_different_seed():
    from model import MarketAuctionModel

    m1 = MarketAuctionModel(rng=42)
    m2 = MarketAuctionModel(rng=123)
    m1.step()
    m2.step()
    assert m1.time == m2.time == 1


def test_model_agents_exist():
    from model import MarketAuctionModel

    m = MarketAuctionModel(rng=42)
    assert len(m.agents) > 0


def test_round_log_increments():
    from model import MarketAuctionModel

    m = MarketAuctionModel(rng=42)
    m.step()
    assert len(m.round_log) == 1
    m.step()
    assert len(m.round_log) == 2


def test_round_log_has_expected_fields():
    from model import MarketAuctionModel

    m = MarketAuctionModel(rng=42)
    m.step()
    entry = m.round_log[-1]
    for key in (
        "round",
        "seller_price",
        "winning_bid",
        "winner_id",
        "items_sold_total",
        "revenue_total",
    ):
        assert key in entry


if __name__ == "__main__":
    test_model_runs_10_steps()
    test_model_initialization()
    test_model_with_different_seed()
    test_model_agents_exist()
    test_round_log_increments()
    test_round_log_has_expected_fields()
    print("All tests passed!")