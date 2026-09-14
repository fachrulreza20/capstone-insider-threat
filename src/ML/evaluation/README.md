# ML Evaluation

This folder contains reusable scripts for prediction, evaluation, experiment comparison, and robustness analysis.

Main responsibilities include:

- apply trained role-specific models to unseen experiment data;
- generate anomaly predictions;
- compare predictions against ground truth;
- calculate confusion matrices;
- calculate accuracy, precision, recall, and F1-score;
- compare Experiment 01 and Experiment 02;
- aggregate repeated subtle-anomaly runs across multiple random seeds.

Ground truth is used only during evaluation. It is not supplied to the ML model during prediction.
