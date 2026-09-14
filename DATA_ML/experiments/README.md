# ML Experiments

This folder contains independent evaluation experiments for the anomaly-detection system.

The trained ML models and calibrated thresholds remain fixed while different test datasets are evaluated.

Current experiments:

## exp01_obvious

Tests relatively obvious behavioural anomalies such as:

- after-hours data exfiltration
- credential compromise
- VIP mass download

This experiment achieved 100% recall on the injected anomalies, but also produced false positives.

## exp02_subtle

Tests less-obvious behavioural anomalies such as:

- gradual download increase
- repeated VIP access
- role deviation
- slow behavioural drift
- unusual activity volume during normal working hours

This experiment showed that the single-day Isolation Forest baseline has more difficulty detecting gradual and subtle behavioural changes.

## Robustness Runs

The subtle-anomaly experiment is repeated using multiple random seeds:

- 2027
- 2028
- 2029
- 2030
- 2031

The model and thresholds remain unchanged. Only the generated test data changes.

The purpose is to confirm that the reduced subtle-anomaly recall is not caused by one particular randomly generated dataset.

Summary files:

- `experiment_comparison.csv`
- `exp02_robustness_runs.csv`
- `exp02_robustness_summary.csv`
