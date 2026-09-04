"""
test_prediction.py

Small demonstration/smoke-test script showing how a new machine observation
is passed through the trained model via predict_failure().

Run from the repository root with:
    python -m src.test_prediction
or from inside src/ with:
    python test_prediction.py
"""

import sys
from pathlib import Path

# Allow running this file directly (python src/test_prediction.py) as well
# as via -m from the repo root.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.predict import predict_failure

# Example input values only -- these are NOT guaranteed to trigger a failure
# prediction; the model decides based on what it actually learned.
sample_machine = {
    "Air_Temp_K": 302.5,
    "Process_Temp_K": 312.1,
    "Rotational_Speed": 2600,
    "Torque": 62,
    "Tool_Wear": 180,
    "Pressure": 114,
    "Vibration": 5.2,
    "Voltage": 218,
    "Current": 25,
}

if __name__ == "__main__":
    result = predict_failure(**sample_machine)

    print("Sample sensor input:")
    for key, value in sample_machine.items():
        print(f"  {key}: {value}")

    print("\nPredicted class:")
    print(f"  {result['label']}")

    print("\nFailure probability:")
    print(f"  {result['failure_probability'] * 100:.1f}%")

    print("\nFull result dict:")
    print(result)
