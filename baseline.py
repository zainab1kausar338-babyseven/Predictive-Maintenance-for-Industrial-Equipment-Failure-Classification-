# Predictive Maintenance - Machine Failure Prediction

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# 1. Load dataset
data = pd.read_csv("cleaned_predictive_maintenance_dataset.csv")
print("Columns:", data.columns.tolist())


# 2. Separate features and target
X = data.drop("failure", axis=1)
y = data["failure"]

# 3. Convert categorical columns into numerical values
X = pd.get_dummies(X, drop_first=True)


# 4. Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# 5. Scale the features
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# 6. Train baseline model
model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# 7. Make predictions
y_pred = model.predict(X_test)


# 8. Evaluate the baseline model
accuracy = accuracy_score(y_test, y_pred)

print("Baseline Model: Logistic Regression")
print("Accuracy:", accuracy)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))