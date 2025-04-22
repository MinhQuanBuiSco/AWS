from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct


class ArtifactBucketStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create S3 bucket for pipeline artifacts
        self.artifact_bucket = s3.Bucket(
            self,
            "ArtifactBucket",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Output the bucket name for reference
        CfnOutput(
            self,
            "ArtifactBucketName",
            value=self.artifact_bucket.bucket_name,
            description="S3 Bucket for Pipeline Artifacts",
        )
