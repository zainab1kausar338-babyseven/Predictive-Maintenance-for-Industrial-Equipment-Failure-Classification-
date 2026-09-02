# === DATA CLEANING: KAGGLE DATASET ===
import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings('ignore')

print("=== 1. LOAD DATA ===")
df = pd.read_csv("predictive_maintenance_dataset.csv")
print("Original Shape:", df.shape)

print("\n=== 2. CLEAN COLUMN NAMES ===")
df.columns = df.columns.str.strip().str.lower()
df.columns = [re.sub(r'[^a-z0-9_]', '_', col) for col in df.columns]
print("Columns:", df.columns.tolist())

print("\n=== 3. CLEAN DATES ===")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.sort_values('date').reset_index(drop=True)

print("\n=== 4. MISSING VALUES ===")
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

print("\n=== 5. REMOVE DUPLICATES ===")
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicates")


print("\n=== 7. FINAL ===")
print("Cleaned Shape:", df.shape)
print("Missing:", df.isnull().sum().sum())
print(df.head())
df.to_csv("cleaned_predictive_maintenance_dataset.csv", index=False)
print("\n✅ Saved as: cleaned_predictive_maintenance_dataset.csv")
