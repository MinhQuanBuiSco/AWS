from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_codedeploy as codedeploy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class AwsEc2CicdExampleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "VPC", max_azs=2)

        # Security group for ALB
        alb_sg = ec2.SecurityGroup(
            self,
            "ALBSecurityGroup",
            vpc=vpc,
            description="Allow HTTP/HTTPS traffic to ALB",
        )
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP")
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "Allow HTTPS")

        # Security group for EC2
        ec2_sg = ec2.SecurityGroup(
            self, "EC2SecurityGroup", vpc=vpc, description="Allow HTTP from ALB and SSH"
        )
        ec2_sg.add_ingress_rule(alb_sg, ec2.Port.tcp(80), "Allow HTTP from ALB")
        ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "Allow SSH")

        # User data script to install Nginx and CodeDeploy agent
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "#!/bin/bash",
            "dnf update -y",
            "dnf install -y nginx ruby wget",
            "systemctl enable nginx",
            "systemctl start nginx",
            "cd /tmp",
            "wget https://aws-codedeploy-us-east-1.s3.amazonaws.com/latest/install",
            "chmod +x ./install",
            "./install auto",
            "systemctl enable codedeploy-agent",
            "systemctl start codedeploy-agent",
        )

        # IAM role for EC2
        ec2_role = iam.Role(
            self, "EC2Role", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )
        ec2_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Launch template for EC2
        launch_template = ec2.LaunchTemplate(
            self,
            "LaunchTemplate",
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            instance_type=ec2.InstanceType("t3.micro"),
            security_group=ec2_sg,
            role=ec2_role,
            user_data=user_data,
        )

        # Auto Scaling Group
        asg = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            launch_template=launch_template,
            min_capacity=1,
            max_capacity=3,
            desired_capacity=1,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        # Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self,
            "ALB",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_sg,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        # Listener for HTTP
        listener = alb.add_listener("Listener", port=80, open=True)
        listener.add_targets(
            "Target",
            port=80,
            targets=[asg],
            health_check=elbv2.HealthCheck(path="/", interval=Duration.seconds(30)),
        )

        # CodeDeploy application and deployment group
        codedeploy_app = codedeploy.ServerApplication(
            self, "CodeDeployApp", application_name="ReactApp"
        )
        self.deployment_group = codedeploy.ServerDeploymentGroup(
            self,
            "DeploymentGroup",
            application=codedeploy_app,
            auto_scaling_groups=[asg],
            install_agent=True,
        )

        # Store ALB DNS name in SSM Parameter Store
        ssm.StringParameter(
            self,
            "ALBDNSName",
            parameter_name="/react-app/alb-dns",
            string_value=alb.load_balancer_dns_name,
        )

        # Output ALB DNS
        CfnOutput(
            self,
            "ALBDNSOutput",
            value=alb.load_balancer_dns_name,
            description="ALB DNS Name",
        )
