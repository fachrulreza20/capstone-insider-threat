# ML-Based Behavioural Anomaly Detection

This module implements the machine-learning baseline for the Insider Threat Detection project.

The objective is to learn normal employee behaviour from synthetic banking audit logs and identify behavioural deviations without relying directly on predefined detection rules.

## 1. Overview

The ML pipeline uses role-specific Isolation Forest models for three employee roles:

- Teller
- Customer Service
- Manager

Instead of training one model for all employees, a separate behavioural baseline is learned for each role because normal activity differs between employee roles.

The overall pipeline is:

Raw Audit Logs  
→ Behavioural Feature Engineering  
→ Role-Specific Isolation Forest  
→ Threshold Calibration  
→ Anomaly Prediction  
→ Evaluation

## 2. Training Data

The models are trained using synthetic NORMAL employee activity only.

The training dataset contains:

- 100 synthetic users
- 1,500 user-day observations
- Three employee roles: Teller, Customer Service, and Manager

Raw activity logs are converted into user-day behavioural features such as:

- event count
- failed login count
- total downloads
- records accessed
- VIP access count
- unknown IP count
- outside-hours activity count
- unique IP count
- first activity hour
- last activity hour

## 3. Role-Specific Models

Separate Isolation Forest models are trained for:

- Teller
- Customer Service
- Manager

This allows the system to learn different normal behavioural patterns for each employee role.

The trained models and scalers are stored under:

`MODELS/role_specific/`

## 4. Threshold Calibration

A separate normal validation dataset is used to calibrate anomaly thresholds.

The threshold is set at the 5th percentile of anomaly scores from unseen normal validation data.

Current calibrated thresholds:

| Role | Threshold |
|---|---:|
| Teller | -0.0783 |
| Customer Service | -0.0720 |
| Manager | -0.0616 |

This calibration intentionally allows approximately 5% of unseen normal validation observations to fall below the anomaly threshold.

## 5. Experiment 01 — Obvious Anomalies

The first experiment evaluates the ML baseline against relatively obvious synthetic anomalies.

Example scenarios include:

- After-hours data exfiltration
- Credential compromise
- VIP mass download

### Results

| Metric | Result |
|---|---:|
| Accuracy | 93.33% |
| Precision | 57.69% |
| Recall | 100.00% |
| F1-score | 73.17% |
| False Negatives | 0 |

The model detected all 15 obvious anomaly cases.

This demonstrates that the role-specific Isolation Forest is effective when behavioural deviations are strong and clearly separated from the normal baseline.

## 6. Experiment 02 — Subtle / Less-Obvious Anomalies

The second experiment introduces less-obvious behavioural anomalies.

Scenarios include:

- Gradual download increase
- Repeated VIP access
- Role deviation
- Slow behavioural drift
- Unusual volume during normal working hours

### Initial Result

| Metric | Result |
|---|---:|
| Accuracy | 87.11% |
| Precision | 71.05% |
| Recall | 60.00% |
| F1-score | 65.06% |
| False Negatives | 18 |

Unlike Experiment 01, the model missed a significant number of less-obvious anomalies.

In particular, gradual and slowly developing behavioural changes were more difficult for the single-day ML baseline to detect.

## 7. Experiment 02 Robustness Check

To determine whether the Experiment 02 result was caused by one particular randomly generated dataset, the experiment was repeated using five random seeds:

- 2027
- 2028
- 2029
- 2030
- 2031

The ML model and calibrated thresholds remained unchanged. Only the synthetic test data generation changed.

### Results Across Five Runs

| Seed | Accuracy | Precision | Recall | F1-score |
|---|---:|---:|---:|---:|
| 2027 | 87.11% | 71.05% | 60.00% | 65.06% |
| 2028 | 90.22% | 81.08% | 66.67% | 73.17% |
| 2029 | 90.67% | 83.33% | 66.67% | 74.07% |
| 2030 | 89.33% | 76.92% | 66.67% | 71.43% |
| 2031 | 88.00% | 72.50% | 64.44% | 68.24% |

### Mean Performance

| Metric | Mean | Standard Deviation |
|---|---:|---:|
| Accuracy | 89.07% | 1.49% |
| Precision | 76.98% | 5.30% |
| Recall | 64.89% | 2.90% |
| F1-score | 70.39% | 3.72% |

The relatively small variation in recall indicates that the reduced ability to detect less-obvious anomalies is consistent across independently generated synthetic test sets.

The ML baseline detects approximately 65% of these anomalies, meaning that approximately one-third remain undetected.

## 8. Key Finding

The experiments demonstrate an important limitation of the current ML baseline:

> The role-specific Isolation Forest performs strongly on obvious behavioural anomalies but is less effective at detecting gradual and multi-day behavioural changes.

This limitation is particularly relevant for insider-threat detection because suspicious employee behaviour may develop gradually rather than appearing as one extreme event.

## 9. Next Step — LLM-Based Temporal Analysis

The next stage of the project will investigate whether an LLM can identify behavioural patterns that are missed by the single-day ML baseline.

The planned comparison is:

Raw Multi-Day Employee Activity  
→ LLM Pattern Analysis  
→ Anomaly Prediction  
→ Comparison with Ground Truth

The LLM experiment will specifically investigate whether contextual and temporal reasoning can improve detection of patterns such as:

- gradual behavioural changes
- slow behavioural drift
- repeated suspicious activity across multiple days

The objective is not simply to replace the ML model, but to evaluate whether LLM reasoning provides additional detection capability for behavioural patterns that the ML baseline misses.