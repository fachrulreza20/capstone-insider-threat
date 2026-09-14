# ML Model Artifacts

This directory stores trained machine-learning artifacts used by the behavioural anomaly-detection pipeline.

The active architecture uses separate behavioural models for each employee role.

## Subfolders

- role_specific/ - trained Isolation Forest models and fitted scalers for Teller, Customer Service, and Manager.
- calibration/ - calibrated anomaly-score thresholds.

The role-specific approach allows employees to be evaluated against normal behaviour for their own business role.

Some older model files may remain in this root folder from earlier development stages. The current role-specific pipeline uses the artifacts inside role_specific/ and calibration/.
