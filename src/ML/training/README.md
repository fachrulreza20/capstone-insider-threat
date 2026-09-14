# ML Training and Threshold Calibration

This folder contains the scripts used to train the anomaly-detection models and calibrate their alert thresholds.

## Training

Separate Isolation Forest models are trained for:

- Teller
- Customer Service
- Manager

Training uses synthetic normal employee behaviour only.

## Calibration

A separate unseen normal validation dataset is used to determine a role-specific anomaly threshold.

Trained model artifacts are stored in:

MODELS/role_specific/

Calibrated thresholds are stored in:

MODELS/calibration/
