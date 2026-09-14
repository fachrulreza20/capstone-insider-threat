# Experiment 02 — Subtle / Less-Obvious Anomalies

This experiment evaluates the same trained ML models against more difficult behavioural anomalies.

The models are NOT retrained for this experiment.

Scenarios include:

- gradual download increase
- repeated VIP access
- role deviation
- slow behavioural drift
- unusual activity volume during normal working hours

Files:

- `raw_logs.csv` — raw synthetic employee activity.
- `features.csv` — generated user-day behavioural features.
- `ground_truth.csv` — known labels for evaluation.
- `predictions.csv` — ML predictions.
- `evaluation_results.csv` — detailed evaluation results.
- `experiment_config.json` — configuration and metrics.

Initial result:

- Accuracy: 87.11%
- Precision: 71.05%
- Recall: 60%
- F1-score: 65.06%

The main finding is that the current single-day ML baseline struggles more with gradual and less-obvious behavioural deviations.
