from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_sagemaker as sagemaker,
    aws_sns as sns, 
    aws_sns_subscriptions as subs
)
from constructs import Construct

class HuggingfaceSagemakerRealtimeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # IAM role for SageMaker
        sagemaker_role = iam.Role(
            self, "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ]
        )

        # Hugging Face DLC image
        huggingface_image_uri = sagemaker.CfnModel.ContainerDefinitionProperty(
            image="763104351884.dkr.ecr.ap-northeast-1.amazonaws.com/huggingface-pytorch-inference:2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04",
            model_data_url="s3://sagemaker-s3-bucket-hf/model.tar.gz",
        )

        model = sagemaker.CfnModel(
            self, "HuggingFaceModel",
            execution_role_arn=sagemaker_role.role_arn,
            primary_container=huggingface_image_uri
        )

        # Realtime Inference Config (no async block)
        endpoint_config = sagemaker.CfnEndpointConfig(
            self, "RealtimeEndpointConfig",
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    initial_variant_weight=1.0,
                    model_name=model.attr_model_name,
                    variant_name="AllTraffic",
                    initial_instance_count=1,
                    instance_type="ml.g4dn.xlarge"
                )
            ]
        )

        sagemaker.CfnEndpoint(
            self, "RealtimeEndpoint",
            endpoint_name="huggingface-realtime-endpoint",
            endpoint_config_name=endpoint_config.attr_endpoint_config_name
        )
