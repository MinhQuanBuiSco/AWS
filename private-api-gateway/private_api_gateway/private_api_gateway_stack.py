from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct

class PrivateApiGatewayStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1️⃣ Create a new VPC
        vpc = ec2.Vpc(
            self, "PrivateApiVpc",
            max_azs=1,  
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

        # 2️⃣ Create Lambda function in the VPC
        func = _lambda.Function(
            self, "PrivateLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_inline(
                "def handler(event, context):\n    return {'statusCode': 200, 'body': 'Hello from Lambda in private API!'}"
            ),
            vpc=vpc,
        )

        # 3️⃣ Create VPC endpoint for API Gateway
        vpc_endpoint = ec2.InterfaceVpcEndpoint(
            self, "ApiGwVpcEndpoint",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointAwsService.APIGATEWAY,
        )

        # 4️⃣ Create Private API Gateway
        api = apigateway.RestApi(
            self, "PrivateApi",
            rest_api_name="PrivateApiGateway",
            endpoint_configuration=apigateway.EndpointConfiguration(
                types=[apigateway.EndpointType.PRIVATE],
                vpc_endpoints=[vpc_endpoint],
            ),
            policy=iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=["execute-api:Invoke"],
                        principals=[iam.AnyPrincipal()],
                        resources=["*"],
                        conditions={
                            "StringEquals": {
                                "aws:SourceVpce": vpc_endpoint.vpc_endpoint_id
                            }
                        }
                    )
                ]
            )
        )

        # 5️⃣ Attach Lambda integration
        integration = apigateway.LambdaIntegration(func)
        api.root.add_method("GET", integration)

        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway endpoint URL",
            export_name="OpenAIProxyUrl"
        )