from aws_cdk import (
    Stack,
    pipelines,
    SecretValue,
    Stage,
    aws_iam as iam
)
from constructs import Construct
from aws_ec2_cicd_example.aws_ec2_cicd_example_stack import AwsEc2CicdExampleStack

class PipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Source: GitHub
        source = pipelines.CodePipelineSource.git_hub(
            "MinhQuanBuiSco/AWS",  # Replace with your repo
            "main",
            authentication=SecretValue.secrets_manager("github-token"),
        )

        synth_step = pipelines.ShellStep(
            "Synth",
            input=source,
            commands=[
                "cd aws-ec2-cicd-example",
                "pip install -r requirements.txt",
                "npm install -g aws-cdk",
                "cdk synth",
            ],
            primary_output_directory="aws-ec2-cicd-example/cdk.out",
        )

        # Pipeline
        pipeline = pipelines.CodePipeline(self, "Pipeline", synth=synth_step)

        # Add the application stage
        deploy_stage = Ec2WebsiteDeploymentStage(self, "Deploy")

        # Add manual approval before deploying
        pipeline.add_stage(
            deploy_stage,
            pre=[
                pipelines.ManualApprovalStep("ManualApprovalBeforeDeploy")
            ]
        )

class Ec2WebsiteDeploymentStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Add the EC2 website stack
        AwsEc2CicdExampleStack(self, "Ec2WebsiteStack")