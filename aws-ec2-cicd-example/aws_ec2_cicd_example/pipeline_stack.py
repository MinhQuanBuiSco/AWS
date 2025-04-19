from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codecommit as aws_codecommit,
    aws_codepipeline_actions as actions,
    aws_iam as iam,
    aws_secretsmanager as secrets,
    aws_iam as iam,
    aws_s3 as s3,
)
from constructs import Construct

class PipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, infra_stack: Stack, artifact_bucket: s3.IBucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Reference CodeDeploy deployment group from InfraStack
        deployment_group = infra_stack.deployment_group

        # Create artifact buckets
        source_artifact = codepipeline.Artifact("SourceArtifact")
        build_artifact = codepipeline.Artifact("BuildArtifact")

        # CodeCommit source action
        github_secret = secrets.Secret.from_secret_name_v2(
            self, "GitHubToken",
            secret_name="github-token"
        )
        
        source_action = actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="MinhQuanBuiSco",
            repo="AWS",
            branch="main",
            oauth_token=github_secret.secret_value,
            output=source_artifact
        )

        # CodeBuild project for building React app
        build_project = codebuild.PipelineProject(self, "BuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0
            ),
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "runtime-versions": {"nodejs": "20"},
                        "commands": [
                            "cd aws-ec2-cicd-example/frontend",
                            "npm install"
                        ]
                    },
                    "build": {
                        "commands": [
                            "npm run build"
                        ]
                    }
                },
                "artifacts": {
                    "base-directory": "aws-ec2-cicd-example/frontend",
                    "files": [
                        "**/*",
                        "../../appspec.yml",
                        "../../nginx.conf",
                        "../../scripts/**"
                    ]
                }
            })
        )

        # Build action
        build_action = actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_artifact,
            outputs=[build_artifact]
        )

        # CodeDeploy action
        deploy_action = actions.CodeDeployServerDeployAction(
            action_name="Deploy",
            deployment_group=deployment_group,
            input=build_artifact
        )

        # Define the pipeline
        pipeline = codepipeline.Pipeline(self, "Pipeline",
            pipeline_name="ReactAppPipeline",
            artifact_bucket=artifact_bucket,
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action]
                ),
                codepipeline.StageProps(
                    stage_name="Deploy",
                    actions=[deploy_action]
                )
            ]
        )

        # Grant permissions for CodeBuild to access the artifact bucket
        artifact_bucket.grant_read_write(build_project)

        # Grant permissions for CodeDeploy
        build_project.add_to_role_policy(iam.PolicyStatement(
            actions=["codedeploy:*", "s3:GetObject", "s3:PutObject", "s3:ListBucket"],
            resources=["*"]  # Scope to specific resources in production
        ))