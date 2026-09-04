"""
predict.py

Reusable prediction module for the Predictive Maintenance ML component.

Loads the trained sklearn Pipeline (preprocessing + model, saved together so
training and inference always use identical preprocessing) and exposes a
single function, predict_failure(), that other parts of the group's
application (e.g. a dashboard or API) can import and call directly.

Usage:
    from src.predict import predict_failure

    result = predict_failure(
        Air_Temp_K=302.5,
        Process_Temp_K=312.1,
        Rotational_Speed=2600,
        Torque=62,
        Tool_Wear=180,
        Pressure=114,
        Vibration=5.2,
        Voltage=218,
        Current=25,
    )
    # -> {"prediction": 1, "label": "Failure",
    #     "failure_probability": 0.83, "no_failure_probability": 0.17}
"""

from pathlib import Path
from typing import Dict, Union

import joblib
import pandas as pd

# Path is relative to this file so predict.py works regardless of the
# caller's current working directory.
_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "predictive_maintenance_model.pkl"

_model_bundle = None  # lazy-loaded on first prediction call


def _load_model():
    """Load and cache the trained pipeline bundle (pipeline + feature order)."""
    global _model_bundle
    if _model_bundle is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found at {_MODEL_PATH}. "
                "Run notebooks/model_training.ipynb first to train and save the model."
            )
        _model_bundle = joblib.load(_MODEL_PATH)
    return _model_bundle


def predict_failure(
    Air_Temp_K: float,
    Process_Temp_K: float,
    Rotational_Speed: float,
    Torque: float,
    Tool_Wear: float,
    Pressure: float,
    Vibration: float,
    Voltage: float,
    Current: float,
) -> Dict[str, Union[int, str, float]]:
    """
    Predict whether an industrial machine is likely to experience a failure,
    given its current sensor readings.

    All arguments are the raw sensor values for a single observation.

    Returns a dict:
        {
            "prediction": 0 or 1,
            "label": "No Failure" or "Failure",
            "failure_probability": float in [0, 1],
            "no_failure_probability": float in [0, 1],
        }
    """
    bundle = _load_model()
    pipeline = bundle["pipeline"]
    feature_cols = bundle["feature_cols"]

    input_values = {
        "Air_Temp_K": Air_Temp_K,
        "Process_Temp_K": Process_Temp_K,
        "Rotational_Speed": Rotational_Speed,
        "Torque": Torque,
        "Tool_Wear": Tool_Wear,
        "Pressure": Pressure,
        "Vibration": Vibration,
        "Voltage": Voltage,
        "Current": Current,
    }

    # Build a single-row DataFrame in the exact column order used at training time.
    row = pd.DataFrame([{col: input_values[col] for col in feature_cols}])

    prediction = int(pipeline.predict(row)[0])
    probabilities = pipeline.predict_proba(row)[0]  # [P(no failure), P(failure)]

    return {
        "prediction": prediction,
        "label": "Failure" if prediction == 1 else "No Failure",
        "failure_probability": round(float(probabilities[1]), 4),
        "no_failure_probability": round(float(probabilities[0]), 4),
    }
