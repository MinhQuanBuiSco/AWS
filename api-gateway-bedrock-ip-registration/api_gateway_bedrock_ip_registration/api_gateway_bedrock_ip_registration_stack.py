from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    CfnOutput
)
from dotenv import load_dotenv
from constructs import Construct

import os

load_dotenv()

class ApiGatewayBedrockIpRegistrationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

       # ✅ Replace with your IPv6 address (check https://whatismyipaddress.com)
        allowed_ip_v6 = f"{os.getenv("YOUR_IP_ADDRESS")}/128"  # example

        # 🔹 Lambda function to call Bedrock
        sonnet_fn = _lambda.Function(
            self, "SonnetFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(30),
            environment={
                "MODEL_ID": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "BEDROCK_REGION": "ap-northeast-1"
            }
        )

        # 🔹 IAM permissions for Lambda to invoke Bedrock
        sonnet_fn.role.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"]  # Restrict this to specific model ARN if needed
        ))

        # 🔹 API Gateway
        api = apigw.RestApi(
            self, "SonnetRestApi",
            rest_api_name="Sonnet LLM API",
            deploy_options=apigw.StageOptions(stage_name="prod")
        )

        # 🔹 /invoke endpoint
        invoke_resource = api.root.add_resource("invoke")
        invoke_resource.add_method(
            "POST",
            apigw.LambdaIntegration(sonnet_fn),
            authorization_type=apigw.AuthorizationType.NONE
        )

        # 🔹 Resource Policy for IPv6 restriction
        api_policy = iam.PolicyStatement(
            actions=["execute-api:Invoke"],
            effect=iam.Effect.ALLOW,
            resources=["*"],
            principals=[iam.AnyPrincipal()],
            conditions={"IpAddress": {"aws:SourceIp": allowed_ip_v6}}
        )

        api_policy_deny = iam.PolicyStatement(
            actions=["execute-api:Invoke"],
            effect=iam.Effect.DENY,
            resources=["*"],
            principals=[iam.AnyPrincipal()],
            conditions={"NotIpAddress": {"aws:SourceIp": allowed_ip_v6}}
        )
        
        api.policy = iam.PolicyDocument(statements=[api_policy, api_policy_deny])
        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway endpoint URL",
            export_name="OpenAIProxyUrl"
        )