# Mesa First Model

This project recreates the **basic visualization tutorial** from the official Mesa documentation using the **Boltzmann Wealth Model**.

## What it does

- creates agents with initial wealth
- places them on a grid
- moves them randomly each step
- transfers wealth between agents that land in the same cell
- visualizes the model in a browser with:
  - a grid view of agents
  - a Gini coefficient plot
  - a slider for changing the number of agents

## Files

- `app.py` — the full runnable Mesa + Solara app

## Requirements

Use Python 3.10+ and install Mesa with visualization support:

```bash
pip install -U mesa solara matplotlib
```

## Run locally

From this folder, run:

```bash
solara run app.py
```

Then open the local URL shown in the terminal.

## Model summary

The model is based on the Boltzmann wealth exchange example from the Mesa tutorial:

1. Each agent starts with wealth = 1.
2. On each step, an agent moves to a random neighboring cell.
3. If the agent has wealth and shares a cell with another agent, it gives 1 unit of wealth to one random cellmate.
4. After every step, the model records the **Gini coefficient** to track inequality.

## Notes

- The model constructor uses **keyword-only arguments**, which is the recommended pattern for `SolaraViz`.
- The visualization uses `SpaceRenderer` with the `matplotlib` backend.
- The Gini plot is placed on a second page in the dashboard.

