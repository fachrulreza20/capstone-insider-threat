# Anomaly Threshold Calibration

This folder contains the role-specific thresholds used to convert ML anomaly scores into Normal or Anomaly predictions.

Current file:

- role_thresholds.json

The thresholds were calculated using a separate validation dataset containing unseen but known-normal employee behaviour.

The initial threshold for each role was selected using the lower 5th percentile of normal validation anomaly scores.

The threshold value is an internal model-score boundary. It is not a time value, percentage, transaction amount, or other physical measurement.
