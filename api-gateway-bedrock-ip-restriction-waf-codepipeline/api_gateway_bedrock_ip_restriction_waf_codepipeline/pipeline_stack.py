from aws_cdk import (
    Stack,
    pipelines,
    SecretValue
)
from constructs import Construct

class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, *, env, cdk_app_stack: Stack, **kwargs) -> None:
        super().__init__(scope, id, env=env, **kwargs)

        # Source: GitHub (change to your repo)
        source = pipelines.CodePipelineSource.git_hub(
            "your-username/your-repo-name",  # Replace with your repo
            "main",  # Branch
            authentication=SecretValue.secrets_manager("github-token"),  # Store your token in Secrets Manager
        )

        # Synth step
        synth = pipelines.CodeBuildStep(
            "Synth",
            input=source,
            install_commands=[
                "npm install -g aws-cdk",
                "pip install -r requirements.txt"
            ],
            commands=[
                "cdk synth"
            ],
        )

        # Pipeline
        pipeline = pipelines.CodePipeline(self, "Pipeline", synth=synth)

        # Add manual approval stage
        preprod_stage = pipeline.add_stage(cdk_app_stack)

        preprod_stage.add_pre(
            pipelines.ManualApprovalStep("ManualApproval")
        )
