from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    RemovalPolicy, 
    aws_codepipeline_actions as cpactions,
    SecretValue,
    aws_iam as iam,
    Duration,
)
from constructs import Construct

class MLopsPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for model artifacts
        bucket = s3.Bucket(self, "LLMArtifactsBucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        s3_bucket = bucket.bucket_name
        # Create SageMaker execution role
        sagemaker_role = iam.Role(self, "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ]
        )

        source_output = codepipeline.Artifact()

        github_source = cpactions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="MinhQuanBuiSco",
            repo="AWS",
            branch="main",
            oauth_token=SecretValue.secrets_manager("github-token"),
            output=source_output
        )

        build_project = codebuild.PipelineProject(
            self, "LLMTrainEval",
            build_spec=codebuild.BuildSpec.from_source_filename("buildspecs/buildspec-train-eval.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                privileged=True
            ),
            environment_variables={
                "S3_BUCKET": codebuild.BuildEnvironmentVariable(value=s3_bucket),
                "SAGEMAKER_ROLE": codebuild.BuildEnvironmentVariable(value=sagemaker_role.role_arn),
            }
        )

        deploy_project = codebuild.PipelineProject(
            self, "LLMDeploy",
            build_spec=codebuild.BuildSpec.from_source_filename("buildspecs/buildspec-deploy.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                privileged=True
            ),
            environment_variables={
                "S3_BUCKET": codebuild.BuildEnvironmentVariable(value=s3_bucket),
                "SAGEMAKER_ROLE": codebuild.BuildEnvironmentVariable(value=sagemaker_role.role_arn),
            }
        )

        bucket.grant_read_write(build_project)
        bucket.grant_read_write(deploy_project)

        pipeline = codepipeline.Pipeline(self, "LLMPipeline")

        pipeline.add_stage(
            stage_name="Source",
            actions=[github_source]
        )

        pipeline.add_stage(
            stage_name="TrainAndEvaluate",
            actions=[
                cpactions.CodeBuildAction(
                    action_name="TrainEvalLLM",
                    project=build_project,
                    input=source_output,
                    outputs=[codepipeline.Artifact()]
                )
            ]
        )

        pipeline.add_stage(
            stage_name="ManualApproval",
            actions=[
                cpactions.ManualApprovalAction(
                    action_name="ApproveDeploy",
                    additional_information="Check S3 or CloudWatch Logs for eval results."
                )
            ]
        )

        pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                cpactions.CodeBuildAction(
                    action_name="DeployLLM",
                    project=deploy_project,
                    input=source_output,
                )
            ]
        )