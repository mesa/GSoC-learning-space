# Model 03: Opinion Diffusion Network

## Goal

Expose communication friction in Mesa signals and pub-sub workflows for networked multi-agent interaction.

## Model Setup

- Each agent has an opinion in the interval [0.0, 1.0].
- Agents are placed on an Erdos-Renyi graph in Network discrete space.
- Each step, every agent broadcasts its current opinion.
- Neighbors update opinion by attraction or contrarian repulsion.
- Signaling uses Observable and ObservableList from mesa_signals.

## Reproducible Run

Parameters used:

- num_agents = 20
- avg_degree = 5
- learning_rate = 0.1
- contrarian_probability = 0.2
- rng = 42
- steps = 40

Run snippet:

~~~python
from model import OpinionDiffusionModel

m = OpinionDiffusionModel(
    num_agents=20,
    avg_degree=5,
    learning_rate=0.1,
    contrarian_probability=0.2,
    rng=42,
)

for _ in range(40):
    m.step()

print(m.history[-1])
~~~

## Results Snapshot

Observed final-row output:

- round = 40
- mean_opinion = 0.6046532054660158
- min_opinion = 0.593236592275645
- max_opinion = 0.6303230501768959

Interpretation:

- Opinions cluster tightly by step 40 under the selected parameters.
- Mean shifts upward from randomized initialization due to local interaction dynamics.
- Sequential activation plus event-driven callbacks can influence within-round update order.

## Mesa Friction Point

The signaling workflow is functional, but communication protocols require manual wiring:

- subscriptions are emitter-specific and added neighbor by neighbor
- there is no topic-level routing abstraction
- ordering semantics are implicit rather than declared

This increases complexity for larger communication designs.

## Minimal API Idea

An opt-in channel abstraction could provide:

- publish(topic, payload)
- subscribe(topic, filter, handler)
- wildcard topics for grouped subscriptions
- selectable delivery policy (for example fifo or timestamp-ordered)

These primitives would reduce repetitive subscription code and make protocol intent explicit.

## What I Learned

- Reactive signals are powerful for local events but verbose for protocol-style communication.
- Ordering assumptions should be explicit when model behavior depends on message timing.
- Reproducible network runs help turn qualitative friction into concrete evidence.

## Next Experiment

- Add per-round buffering to compare synchronous versus immediate-delivery updates.
- Measure message volume and handler cost as graph density increases.
- Evaluate a topic-based wrapper over current signals without modifying core Mesa APIs.
