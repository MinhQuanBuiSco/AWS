from aws_cdk import (
    Stack,
    pipelines,
    SecretValue,
    Stage,
    aws_iam as iam
)
from constructs import Construct
from api_gateway_bedrock_ip_restriction_waf_codepipeline.api_gateway_bedrock_ip_restriction_waf_stack import ApiGatewayBedrockIpRestrictionWafStack
class PipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Source: GitHub (change to your repo)
        source = pipelines.CodePipelineSource.git_hub(
            "MinhQuanBuiSco/AWS",  # Replace with your repo
            "main",  # Branch
            authentication=SecretValue.secrets_manager("github-token"),  # Store your token in Secrets Manager
        )
        

        synth_step = pipelines.ShellStep(
            "Synth",
            input=source,
            commands=[
                "cd api-gateway-bedrock-ip-restriction-waf-codepipeline",
                "pip install -r requirements.txt",
                "npm install -g aws-cdk",
                "cdk synth",
            ],
            primary_output_directory="api-gateway-bedrock-ip-restriction-waf-codepipeline/cdk.out",
        )

        # Pipeline
        pipeline = pipelines.CodePipeline(self, "Pipeline", synth=synth_step)

        # Add the application stage
        deploy_stage = ApiGatewayDeploymentStage(self, "Deploy")

        # Add manual approval before deploying
        pipeline.add_stage(
            deploy_stage,
            pre=[
                pipelines.ManualApprovalStep("ManualApprovalBeforeDeploy")
            ]
        )


class ApiGatewayDeploymentStage(Stage):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Add your main application stack
        ApiGatewayBedrockIpRestrictionWafStack(self, "ApiStack")