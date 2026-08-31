

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore') # Hides all pandas warnings

# ============ 1. LOAD DATA ============
df = pd.read_csv("predictive_maintenance_dataset.csv")
print("Loaded:", df.shape)
print("\nColumns:", df.columns.tolist())

# ============ 2. DATA CLEANING ============
print("\n=== 2. DATA CLEANING ===")

df.drop(columns=['UDI', 'Product ID'], errors='ignore', inplace=True)

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values('date').reset_index(drop=True)

# SAFE FILLING - No errors possible
for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col] = df[col].fillna(df[col].mean())
    else:
        df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')

print("Missing values after cleaning:", df.isnull().sum().sum())

before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows")
print("Cleaned Data Shape:", df.shape)


# ============ 3. FORECASTING ============
print("\n=== 3. FORECASTING ===")

target_col = 'failure' # Your screenshot shows it's called 'failure'
print("Using target column:", target_col)

window = 100
df['Failure_RollingAvg'] = df[target_col].rolling(window=window, min_periods=1).mean()
last_avg = df[target_col].tail(window).mean()
forecast = [last_avg] * 10

print(f"\nLast {window} rows average failure rate: {last_avg:.4f}")
print(f"Forecast for next 10 time steps: {np.round(forecast, 4)}")

# PLOT
plt.figure(figsize=(12,6))
plt.plot(df['date'], df[target_col], label='Actual Failures', alpha=0.3)
plt.plot(df['date'], df['Failure_RollingAvg'], label=f'Rolling Avg {window}', linewidth=2)
plt.axhline(y=last_avg, color='r', linestyle='--', label=f'Forecast: {last_avg:.3f}')
plt.title('Predictive Maintenance - Failure Forecasting')
plt.xlabel('Date')
plt.ylabel('Failure 0 or 1')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('forecast_plot.png', dpi=150)
print("\n✅ Saved plot as: forecast_plot.png")
print("\n=== ALL DONE ===")