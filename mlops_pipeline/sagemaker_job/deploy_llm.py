import sagemaker
from sagemaker.huggingface import HuggingFaceModel
import os
import time

role = os.environ["SAGEMAKER_ROLE"]
bucket = os.environ["S3_BUCKET"]
model_data = f"s3://{bucket}/llm-training-output/model.tar.gz"

model = HuggingFaceModel(
    model_data=model_data,
    role=role,
    transformers_version="4.38.0",
    pytorch_version="2.1.1",
    py_version="py310",
    entry_point="inference.py",
    source_dir="./src"
)

endpoint_name = f"llm-endpoint-{int(time.time())}"

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.g4dn.xlarge",
    endpoint_name=endpoint_name
)

print(f"Deployed at endpoint: {endpoint_name}")
