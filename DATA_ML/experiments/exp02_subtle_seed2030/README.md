# Experiment 02 Robustness Run - Seed 2030

This folder contains one independent rerun of Experiment 02 using random seed 2030.

The purpose is to test whether the performance of the subtle-anomaly experiment is stable across different randomly generated datasets.

Important: the trained ML models and calibrated thresholds are NOT changed between robustness runs. Only the synthetic test data changes.

## Files

- raw_logs.csv - generated raw employee activity logs.
- features.csv - user-day behavioural features.
- ground_truth.csv - known true labels used only for evaluation.
- predictions.csv - ML predictions.
- evaluation_results.csv - prediction results merged with ground truth.

## Why this run exists

A single synthetic test dataset may produce results that are partly influenced by random data generation.

Repeating the same experiment with multiple random seeds allows us to check whether the ML performance remains reasonably consistent.

The combined robustness results are stored in:

- DATA_ML/experiments/exp02_robustness_runs.csv
- DATA_ML/experiments/exp02_robustness_summary.csv
