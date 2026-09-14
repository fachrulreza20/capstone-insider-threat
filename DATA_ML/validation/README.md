# Validation Data

This folder contains unseen NORMAL employee behaviour used after model training.

The validation dataset is not used to train the Isolation Forest models.

Its purpose is to observe how the trained models score new but known-normal behaviour and to determine role-specific anomaly thresholds.

Current calibration uses the lower 5th percentile of normal validation anomaly scores.

This produced separate thresholds for:

- Teller
- Customer Service
- Manager

The resulting thresholds are stored under:

`MODELS/calibration/role_thresholds.json`
