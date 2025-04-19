import aws_cdk as cdk
from aws_ec2_cicd_example.aws_ec2_cicd_example_stack import AwsEc2CicdExampleStack
from aws_ec2_cicd_example.pipeline_stack import PipelineStack
from aws_ec2_cicd_example.artifacts_stack import ArtifactBucketStack

app = cdk.App()

artifact_bucket_stack = ArtifactBucketStack(app, "ArtifactBucketStack")

infra_stack = AwsEc2CicdExampleStack(app, "AwsEc2CicdExampleStack")

pipeline_stack = PipelineStack(app, "PipelineStack",infra_stack=infra_stack, artifact_bucket=artifact_bucket_stack.artifact_bucket)
pipeline_stack.add_dependency(infra_stack)
app.synth()
