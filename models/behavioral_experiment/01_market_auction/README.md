# Model 01: Market Auction

## Goal

Expose friction in Mesa when implementing request-reply interactions between agents.

## Model Setup

- One Seller agent posts a reserve price every round.
- Eight Buyer agents with random budgets submit bids.
- Seller selects the highest valid bid and executes one sale per round.
- Communication is implemented using a shared inbox workaround.

## Reproducible Run

Parameters used:

- num_buyers = 8
- seller_price = 40.0
- rng = 42
- steps = 30

Run snippet:

~~~python
from model import MarketAuctionModel

m = MarketAuctionModel(num_buyers=8, seller_price=40.0, rng=42)
for _ in range(30):
    m.step()

total_rounds = len(m.round_log)
wins = sum(1 for r in m.round_log if r["winning_bid"] is not None)
mean_win = (
    sum(r["winning_bid"] for r in m.round_log if r["winning_bid"] is not None)
    / max(1, wins)
)
print(total_rounds, wins, round(mean_win, 2), round(m.seller.total_revenue, 2))
~~~

## Results Snapshot

Observed output:

- total_rounds = 30
- winning_rounds = 8
- mean_winning_bid = 74.70
- seller_total_revenue = 597.58

Interpretation:

- Market clears in a minority of rounds under the selected reserve-price setup.
- High mean winning bid compared to reserve shows selective winning behavior.
- The core auction logic works, but messaging is model-specific plumbing.

## Mesa Friction Point

The model requires custom communication scaffolding:

- shared mutable inbox on Seller
- custom Bid data object per protocol
- manual read-process-clear lifecycle every round

Mesa does not provide built-in request-reply primitives with acknowledgement or timeout semantics for this workflow.

## Minimal API Idea

An opt-in interaction layer could support:

- send(to=..., msg=...)
- broadcast(to=AgentType or filter, msg=...)
- request(to=..., msg=..., timeout=...)
- on(MessageType, handler=...)
- await_ack(message_id)

This would let model code focus on protocol behavior rather than mailbox mechanics.

## What I Learned

- Auction-style interactions are easy to express conceptually but verbose in current Mesa code.
- Missing protocol primitives increase repeated boilerplate across models.
- Reproducible runs make interaction claims stronger for proposal evaluation.

## Next Experiment

- Add typed message envelopes and explicit round timestamps.
- Compare FIFO inbox processing versus priority-based bid resolution.
- Evaluate whether interaction abstraction can be added without touching stable Agent APIs.
