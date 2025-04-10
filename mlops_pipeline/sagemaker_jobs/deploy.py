import sagemaker
from sagemaker.huggingface.model import HuggingFaceModel
import argparse

def deploy_model(model_data, endpoint_name, bucket_name):
    role = sagemaker.get_execution_role()
    sagemaker_session = sagemaker.Session()

    huggingface_model = HuggingFaceModel(
        model_data=f's3://{bucket_name}/output/model/model.tar.gz',
        role=role,
        transformers_version='4.26',
        pytorch_version='1.13',
        py_version='py39',
        entry_point='inference.py',
    )

    predictor = huggingface_model.deploy(
        initial_instance_count=1,
        instance_type='ml.g4dn.xlarge',
        endpoint_name=endpoint_name,
    )

    print(f"Endpoint deployed: {endpoint_name}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy LLM model to SageMaker')
    parser.add_argument('--model-path', type=str, required=True, help='S3 path to model')
    parser.add_argument('--endpoint-name', type=str, required=True, help='SageMaker endpoint name')
    parser.add_argument('--bucket-name', type=str, required=True, help='S3 bucket name')
    args = parser.parse_args()
    deploy_model(args.model_path, args.endpoint_name, args.bucket_name)