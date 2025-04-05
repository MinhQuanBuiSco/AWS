from aws_cdk import (
    Stack,
    Stage,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    aws_codebuild as codebuild,
    aws_secretsmanager as secretsmanager,
    pipelines as pipelines_,
    SecretValue,
)
from constructs import Construct
from mlops_pipeline.sagemaker_stack import LlmPipelineStack

class MlopsPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # GitHub token from Secrets Manager
        oauth_token = secretsmanager.Secret.from_secret_name_v2(self, "GitHubToken", "github-token")

        # GitHub source
        source = pipelines_.CodePipelineSource.git_hub(
            "MinhQuanBuiSco/AWS",  # <-- replace this
            "main",
            authentication=SecretValue.secrets_manager("github-token"),  # Store your token in Secrets Manager

        )

        # Synth step
        synth = pipelines_.ShellStep("Synth",
            input=source,
            commands=[
                "cd mlops_pipeline",
                "npm install -g aws-cdk",
                "pip install -r requirements.txt",
                "cdk synth"
            ],
            primary_output_directory="mlops_pipeline/cdk.out",
        )

        # Pipeline
        pipeline = pipelines_.CodePipeline(self, "Pipeline", synth=synth)

        # ✅ Add manual approval before training stack is deployed
        approve_step = pipelines_.ManualApprovalStep("ManualApprovalBeforeTrain")

        # ✅ Add stage to deploy ML training pipeline stack
        pipeline.add_stage(
            LlmPipelineStage(self, "DeployLLMPipeline"),
            pre=[approve_step]  # ← 👈 pre-hook: this adds the manual gate
        )

class LlmPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        LlmPipelineStack(self, "LlmPipelineStack")