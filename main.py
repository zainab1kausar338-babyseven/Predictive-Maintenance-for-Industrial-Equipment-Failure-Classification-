import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os
warnings.filterwarnings('ignore')

os.makedirs("data_output", exist_ok=True)

# ============ 1. READ RAW DATA ============
df = pd.read_csv("predictive_maintenance_dataset.csv") 

# ============ 2. CLEAN DATA ============
df.drop(columns=['UDI', 'Product ID'], errors='ignore', inplace=True)

if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values('date').reset_index(drop=True)

for col in df.columns:
    if pd.api.types.is_numeric_dtype(df[col]):
        df[col] = df[col].fillna(df[col].mean())
    else:
        df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')

df = df.drop_duplicates()

# SAVE CLEAN DATA
df.to_csv("data_output/cleaned_data.csv", index=False)

# ============ 3. FORECASTING ============
target_col = 'failure'
window = 100

df['Failure_RollingAvg'] = df[target_col].rolling(window=window, min_periods=1).mean()
last_avg = df[target_col].tail(window).mean()
forecast = [last_avg] * 10

forecast_df = pd.DataFrame({
    'time_step': range(1, 11),
    'forecasted_failure_rate': forecast
})
forecast_df.to_csv("data_output/forecast_results.csv", index=False)

plt.figure(figsize=(12,6))
plt.plot(df['date'], df['Failure_RollingAvg'], label=f'Rolling Avg {window}', linewidth=2)
plt.axhline(y=last_avg, color='r', linestyle='--', label=f'Forecast: {last_avg:.3f}')
plt.title('Predictive Maintenance - Failure Forecasting')
plt.xlabel('Date')
plt.ylabel('Failure Rate')
plt.legend()
plt.savefig('forecast_plot.png', dpi=150)
print("Done")
