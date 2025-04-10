import sagemaker
from sagemaker.huggingface import HuggingFace
import argparse
import os

def train_model(bucket_name):
    # SageMaker session and role
    role = sagemaker.get_execution_role()
    sagemaker_session = sagemaker.Session()

    # Define training job parameters
    hyperparameters = {
        'model_name_or_path': 'facebook/opt-125m',
        'dataset_name': 'wikitext',
        'dataset_config_name': 'wikitext-103-raw-v1',
        'output_dir': '/opt/ml/model',
        'num_train_epochs': 3,
        'per_device_train_batch_size': 4,
        'save_strategy': 'epoch',
        'push_to_hub': False,
        'max_seq_length': 128,
    }

    # Define the estimator
    hugginface_estimator = HuggingFace(
        entry_point='train_script.py',
        role=role,
        instance_count=1,
        instance_type='ml.p3.2xlarge',
        transformers_version='4.26',
        pytorch_version='1.13',
        py_version='py39',
        hyperparameters=hyperparameters,
        output_path=f's3://{bucket_name}/output',  # Ensure this matches the desired S3 path
    )

    # Start training
    hugginface_estimator.fit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train LLM model')
    parser.add_argument('--bucket-name', type=str, required=True, help='S3 bucket name')
    args = parser.parse_args()
    train_model(args.bucket_name)