import sagemaker
from sagemaker.huggingface import HuggingFace
import os
import time

role = os.environ["SAGEMAKER_ROLE"]
bucket = os.environ["S3_BUCKET"]

job_name = f"llm-train-job-{int(time.time())}"
output_path = f"s3://{bucket}/llm-training-output/"

estimator = HuggingFace(
    entry_point="train_script.py",
    source_dir="./src",
    instance_type="ml.g4dn.xlarge",
    instance_count=1,
    role=role,
    transformers_version="4.38.0",
    pytorch_version="2.1.1",
    py_version="py310",
    hyperparameters={
        "model_name_or_path": "facebook/opt-125m",
        "dataset_name": "wikitext",
        "dataset_config_name": "wikitext-2-raw-v1",
        "do_train": True,
        "do_eval": True,
        "num_train_epochs": 1,
        "per_device_train_batch_size": 2,
        "per_device_eval_batch_size": 2,
        "output_dir": "/opt/ml/model"
    },
    output_path=output_path
)

estimator.fit(job_name=job_name)
