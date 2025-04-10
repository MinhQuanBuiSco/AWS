from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy, 
    SecretValue,
    aws_iam as iam,
    pipelines,
    SecretValue
)

from aws_cdk.aws_codepipeline import Artifact
from aws_cdk.aws_codepipeline_actions import GitHubSourceAction
from aws_cdk.aws_codebuild import BuildSpec, LinuxBuildImage, Project
from constructs import Construct

class MLopsPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for model artifacts
        model_bucket = s3.Bucket(self, "LLMArtifactsBucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # Create SageMaker execution role
        sagemaker_role = iam.Role(self, "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ]
        )

        # Source artifact (from GitHub)
        source_artifact = Artifact()

        # Source action (pull from GitHub)
        source = pipelines.CodePipelineSource.git_hub(
            "MinhQuanBuiSco/AWS",  # Replace with your repo
            "main",  # Branch
            authentication=SecretValue.secrets_manager("github-token"),  # Store your token in Secrets Manager
        )

        # Synth action (build the CDK app)
        synth_step = pipelines.ShellStep(
            "Synth",
            input=source,
            commands=[
                "cd mlops_pipeline",
                "pip install -r requirements.txt",
                "npm install -g aws-cdk",
                "cdk synth",
            ],
            primary_output_directory="mlops_pipeline/cdk.out",
        )

        # Define the pipeline
        pipeline = pipelines.CodePipeline(self, "Pipeline", synth=synth_step)

        # Grant SageMaker role access to the S3 bucket
        model_bucket.grant_read_write(sagemaker_role)

        # Training Stage
        train_stage = pipeline.add_stage("TrainModel",
            actions=[
                Project(self, "TrainProject",
                    build_spec=BuildSpec.from_object({
                        "version": "0.2",
                        "phases": {
                            "install": {
                                "commands": [
                                    "pip install torch transformers sagemaker datasets"
                                ]
                            },
                            "build": {
                                "commands": [
                                    f"python training/train_llm.py --bucket-name {model_bucket.bucket_name}"  # Pass bucket name as argument
                                ]
                            }
                        },
                        "artifacts": {
                            "files": ["**/*"]
                        }
                    }),
                    environment={
                        "build_image": LinuxBuildImage.STANDARD_5_0,
                        "compute_type": "BUILD_GENERAL1_LARGE"
                    },
                    role=sagemaker_role
                ),
            ]
        )

        # Evaluation Stage
        eval_stage = pipeline.add_stage("EvaluateModel",
            actions=[
                Project(self, "EvalProject",
                    build_spec=BuildSpec.from_object({
                        "version": "0.2",
                        "phases": {
                            "install": {
                                "commands": [
                                    "pip install torch transformers datasets boto3"
                                ]
                            },
                            "build": {
                                "commands": [
                                    f"python evaluation/evaluate_llm.py --bucket-name {model_bucket.bucket_name}"  # Pass bucket name as argument
                                ]
                            }
                        },
                        "artifacts": {
                            "files": ["eval_results.txt"]
                        }
                    }),
                    environment={
                        "build_image": LinuxBuildImage.STANDARD_5_0,
                        "compute_type": "BUILD_GENERAL1_LARGE"
                    },
                    role=sagemaker_role
                ),
            ]
        )

        # Deployment Stage (to SageMaker)
        deploy_stage = pipeline.add_stage("DeployModel",
            actions=[
                Project(self, "DeployProject",
                    build_spec=BuildSpec.from_object({
                        "version": "0.2",
                        "phases": {
                            "install": {
                                "commands": [
                                    "pip install awscli boto3 sagemaker"
                                ]
                            },
                            "build": {
                                "commands": [
                                    f"python deployment/deploy_to_sagemaker.py --model-path s3://{model_bucket.bucket_name}/output/model/ --endpoint-name opt-125m-endpoint --bucket-name {model_bucket.bucket_name}"  # Pass bucket name as argument
                                ]
                            }
                        }
                    }),
                    environment={
                        "build_image": LinuxBuildImage.STANDARD_5_0,
                        "compute_type": "BUILD_GENERAL1_LARGE"
                    },
                    role=sagemaker_role
                ),
            ]
        )