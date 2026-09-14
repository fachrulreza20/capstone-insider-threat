# Behavioural Feature Engineering

This folder converts raw employee audit logs into numerical behavioural features that can be processed by the ML models.

Raw activity may contain many individual events for one employee during one day.

Feature engineering summarizes those events into one user-day behavioural observation.

Current features include:

- event count
- failed login count
- total downloads
- total records accessed
- VIP access count
- unknown IP count
- outside-hours activity count
- unique IP count
- first activity hour
- last activity hour

This folder also contains reusable scripts for generating feature datasets for training, validation, and experiments.
