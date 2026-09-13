import pandas as pd
from src.ML.feature_engineering import create_user_day_features

df = pd.read_csv("DATA_ML/normal_train.csv")

features = create_user_day_features(df)

print(features.head())
print(features.columns)
print(features.shape)