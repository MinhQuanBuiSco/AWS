from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy
)
from constructs import Construct

class SagemakerS3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(self, "MySampleBucket",
            bucket_name="sagemaker-s3-bucket-hf",
            public_read_access=False,
            removal_policy=RemovalPolicy.DESTROY,  # Deletes the bucket itself
            auto_delete_objects=True               # Deletes all objects in the bucket
        )