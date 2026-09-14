# Experiment 01 — Obvious Anomalies

This experiment evaluates the role-specific Isolation Forest baseline against relatively obvious synthetic anomalies.

Test scenarios include:

- after-hours data exfiltration
- credential compromise
- VIP mass download

Files:

- `raw_logs.csv` — synthetic raw audit activity.
- `features.csv` — user-day behavioural features.
- `ground_truth.csv` — known true labels used only for evaluation.
- `predictions.csv` — ML anomaly predictions.
- `evaluation_results.csv` — predictions merged with ground truth.
- `experiment_config.json` — experiment configuration and summary metrics.

Initial result:

- Accuracy: 93.33%
- Precision: 57.69%
- Recall: 100%
- F1-score: 73.17%

The main finding is that strong and obvious behavioural anomalies are detected reliably by the current ML baseline.
