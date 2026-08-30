import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error


df= pd.read_csv("predictive_maintenance_dataset.csv")
print("Loaded:",df.shape)
df.head()