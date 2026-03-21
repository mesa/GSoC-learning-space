# Model 02: Needs-Driven Wolf-Sheep

## Behavior-Tuning Log (Priority Friction)

This section tracks behavior-parameter tuning for the Sheep priority policy and documents:

1. what parameters were used
2. what happened
3. why the next change is needed

### Baseline Status (Before Fear-Tuning Changes)

The Sheep priority logic currently uses:

- flee if fear > 8
- forage if energy < 3
- rest if fatigue > 15
- otherwise wander

Fear dynamics currently use:

- fear increase when wolves are nearby: +4
- fear decay each step: -2
- wolf detection neighborhood: radius 1 (immediate neighborhood)

Current run parameters (latest stable coexistence run):

- initial_sheep = 180
- initial_wolves = 8
- sheep_reproduce = 0.08
- wolf_reproduce = 0.015
- wolf_gain_from_food = 12.0
- sheep_gain_from_food = 6.0
- grass_regrowth_time = 12
- steps = 80

Observed result:

- Sheep and wolves coexist for the run horizon (no immediate sheep extinction).
- Sheep action diversity is visible (forage/rest/wander all active).
- AvgSheepFear stays relatively low (roughly ~0.5 to ~1.4 in the shown tail window).
- Flee behavior is still weak/rare because fear rarely reaches the current flee threshold (>8).

Interpretation:

- The model now exposes priority-based behavior friction better than the earlier collapse regime.
- But fear-driven branch activation is underrepresented, so panic/escape dynamics are not yet clearly visible in action counts.
- Averages likely hide occasional fear spikes; max fear should be tracked too.

### Why We Changed Parameters Next

We tuned fear-related parameters to make the flee branch observable:

- reduced flee threshold (example: fear > 8 to fear > 4)
- increased fear rise per threat event (example: +4 to +6)
- slowed fear decay (example: -2 to -1)
- optionally expanded wolf sensing to radius 2
- added MaxSheepFear reporter in the model to capture spikes hidden by averages

Goal of change:

- made fear-vs-hunger-vs-fatigue arbitration visibly active in collected metrics
- produced clearer evidence for behavior-selection limitations in step-coupled logic

### Change Record 01 (After Fear-Tuning + MaxSheepFear)

Changes made:

- fear trigger threshold in select_action: `fear > 8` -> `fear > 4`
- fear increase near wolves in update_drives: `+4` -> `+6`
- fear decay in step: `-2` -> `-1`
- added `MaxSheepFear` reporter in model datacollection

Run parameters:

- initial_sheep = 180
- initial_wolves = 8
- sheep_reproduce = 0.08
- wolf_reproduce = 0.015
- wolf_gain_from_food = 12.0
- sheep_gain_from_food = 6.0
- grass_regrowth_time = 12
- steps = 80

Observed result:

- Flee behavior became visible and frequent (FleeCount regularly > 0, up to 10 in the shown tail).
- Action arbitration is now explicit in metrics: flee/forage/rest/wander all appear in the same time window.
- AvgSheepFear remains moderate while MaxSheepFear shows high spikes (up to 30), confirming panic episodes were previously hidden by averages.
- Sheep population declines over the late window but does not collapse immediately, preserving an analyzable coexistence period.

Comparison vs baseline:

- Baseline had low average fear and near-invisible flee branch activity.
- Tuned version activates fear-driven behavior and reveals stronger competition between internal drives.

Conclusion:

- The tuning successfully exposes action-priority friction in the current step-coupled policy.
- MaxSheepFear is necessary alongside AvgSheepFear to detect episodic threat responses.
- Further tuning or policy changes may be needed to sustain coexistence longer while keeping fear dynamics active.
