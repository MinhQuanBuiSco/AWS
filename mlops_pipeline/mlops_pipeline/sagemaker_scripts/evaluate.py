# sagemaker_scripts/evaluate.py
import json
from random import random

# Simulate an evaluation accuracy
accuracy = round(random() * 0.5 + 0.5, 2)

with open("/opt/ml/processing/output/eval.json", "w") as f:
    json.dump({"accuracy": accuracy}, f)
