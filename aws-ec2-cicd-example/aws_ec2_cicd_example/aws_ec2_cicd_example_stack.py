from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
    aws_codebuild as codebuild,
    RemovalPolicy,
    CfnOutput,
    Stack
)
from constructs import Construct

class AwsEc2CicdExampleStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with a single public subnet
        vpc = ec2.Vpc(self, "WebsiteVPC", max_azs=1, nat_gateways=0)

        # Security Group for EC2
        security_group = ec2.SecurityGroup(
            self,
            "WebsiteSG",
            vpc=vpc,
            allow_all_outbound=True,
            description="Security group for website EC2",
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP access"
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH access"
        )

        # User data script to install Nginx and SSM agent
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "#!/bin/bash",
            "yum update -y",
            "yum install -y nginx amazon-ssm-agent",
            "systemctl start nginx",
            "systemctl enable nginx",
            "systemctl start amazon-ssm-agent",
            "systemctl enable amazon-ssm-agent",
        )

        # IAM role for EC2
        ec2_role = iam.Role(
            self,
            "EC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3ReadOnlyAccess"
                ),
            ],
        )

        # EC2 instance
        instance = ec2.Instance(
            self,
            "WebsiteInstance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),  # Use Amazon Linux 2
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=security_group,
            role=ec2_role,
            user_data=user_data,
        )

        # S3 bucket for website files
        website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # S3 bucket for pipeline artifacts
        artifact_bucket = s3.Bucket(
            self,
            "ArtifactBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # IAM role for CodeBuild
        codebuild_role = iam.Role(
            self,
            "CodeBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMFullAccess"
                ),
            ],
        )

        # CodeBuild project
        build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
            build_spec=codebuild.BuildSpec.from_source_filename(
                "frontend/buildspec.yml"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
            ),
            environment_variables={
                "WEBSITE_BUCKET": codebuild.BuildEnvironmentVariable(
                    value=website_bucket.bucket_name
                ),
                "EC2_INSTANCE_ID": codebuild.BuildEnvironmentVariable(
                    value=instance.instance_id
                ),
                "AWS_REGION": codebuild.BuildEnvironmentVariable(
                    value=self.region
                ),
            },
            role=codebuild_role,
        )

        # Output the EC2 public IP
        CfnOutput(
            self,
            "InstancePublicIP",
            value=instance.instance_public_ip,
            description="Public IP of the EC2 instance",
        )