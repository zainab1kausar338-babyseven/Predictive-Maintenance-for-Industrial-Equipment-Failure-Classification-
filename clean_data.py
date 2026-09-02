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

print("\n=== 6. RENAME METRICS + CONVERT TO KELVIN ===")

# RENAME METRICS TO REAL NAMES
df = df.rename(columns={
    'metric1': 'Air_Temp_C',      
    'metric2': 'Process_Temp_C',  
    'metric3': 'Rotational_Speed', 
    'metric4': 'Torque',
    'metric5': 'Tool_Wear',
    'metric6': 'Pressure',
    'metric7': 'Vibration',
    'metric8': 'Voltage',
    'metric9': 'Current' })
print("New Columns:", df.columns.tolist())

     # CONVERT C TO KELVIN: K = C + 273.15
df['Air_Temp_K'] = df['Air_Temp_C'] + 273.15
df['Process_Temp_K'] = df['Process_Temp_C'] + 273.15

     # ADD ENGINEERING LIMIT FLAGS
df['Air_Temp_Alert'] = np.where(df['Air_Temp_K'] > 320, 1, 0)      # > 47C
df['Process_Temp_Alert'] = np.where(df['Process_Temp_K'] > 350, 1, 0) # > 77C
df['Critical_Temp_Flag'] = np.where(df['Process_Temp_K'] > 373, 1, 0) # > 100C = 373K
df['RPM_Alert'] = np.where(df['Rotational_Speed'] > 4000, 1, 0)
df['Tool_Wear_Alert'] = np.where(df['Tool_Wear'] > 200, 1, 0)

print("Added Kelvin columns and Alert flags")

print("\n=== 7. FINAL ===")
print("Cleaned Shape:", df.shape)
print("Missing:", df.isnull().sum().sum())
print(df.head())
df.to_csv("cleaned_predictive_maintenance_dataset.csv", index=False)
print("\n✅ Saved as: cleaned_predictive_maintenance_dataset.csv")
