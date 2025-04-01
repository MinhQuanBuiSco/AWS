from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    Duration,
    BundlingOptions,
    CfnOutput
)
import os
from dotenv import load_dotenv
from constructs import Construct

load_dotenv()

class PrivateSubnetLambdaAccessExternalApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC with private and public subnets, NAT Gateway
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

        # Lambda Security Group
        lambda_sg = ec2.SecurityGroup(
            self, "LambdaSG",
            vpc=vpc,
            description="Allow HTTPS",
            allow_all_outbound=True
        )

        # Lambda function in private subnet
        lambda_fn = _lambda.Function(
            self, "OpenAILambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset(
                path="lambda",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install --platform manylinux2014_x86_64 --only-binary=:all: --upgrade -r requirements.txt -t /asset-output && cp -au . /asset-output"
                    ]
                )
            ),
            vpc=vpc,
            security_groups=[lambda_sg],
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            timeout=Duration.seconds(30),
            environment={
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
            }
        )

        # REST API Gateway (no IP restriction)
        api = apigw.RestApi(
            self, "OpenAIApi",
            rest_api_name="OpenAIProxy",
            description="Public API to call OpenAI via Lambda"
        )

        invoke_resource = api.root.add_resource("invoke")
        invoke_resource.add_method(
            "POST",
            apigw.LambdaIntegration(lambda_fn),
            authorization_type=apigw.AuthorizationType.NONE
        )
        # Output the URL
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway endpoint URL",
            export_name="OpenAIProxyUrl"
        )