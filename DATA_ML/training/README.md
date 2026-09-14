# Training Data

This folder contains the datasets used to train the role-specific Isolation Forest models.

The training data represents NORMAL synthetic employee behaviour only.

Main files include:

- `normal_train_large.csv` — generated raw normal employee activity logs.
- `normal_train_features.csv` — user-day behavioural features derived from the raw logs.
- `role_specific_training_results.csv` — training results for Teller, Customer Service, and Manager models.
- `training_results.csv` — earlier training output retained for reference.
- `normal_train.csv` — small initial dataset used during early pipeline testing.

The ML models learn what normal behaviour looks like from this data. No injected malicious/anomalous cases are required for the unsupervised Isolation Forest training stage.
