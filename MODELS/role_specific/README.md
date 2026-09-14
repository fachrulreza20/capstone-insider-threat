# Role-Specific ML Models

This folder contains the active Isolation Forest models used by the ML anomaly-detection baseline.

Separate models are trained for:

- Teller
- Customer Service
- Manager

Each role has two files:

- <Role>_isolation_forest.pkl - the trained Isolation Forest model.
- <Role>_scaler.pkl - the fitted StandardScaler used to transform behavioural features.

The purpose of separating models by role is to incorporate business context.

For example, normal Manager behaviour may include more downloads or VIP account access than normal Teller behaviour. A Teller is therefore evaluated primarily against the Teller behavioural baseline.
