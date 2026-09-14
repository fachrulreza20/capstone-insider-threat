# ML Data

This directory contains all datasets and experiment outputs used by the machine-learning anomaly detection pipeline.

The data is separated into three main stages:

- `training/` — normal employee behaviour used to train the ML models.
- `validation/` — unseen normal behaviour used to calibrate anomaly thresholds.
- `experiments/` — test datasets, predictions, ground truth, and evaluation results.

The separation is intentional to prevent data leakage between training, validation, and testing.
