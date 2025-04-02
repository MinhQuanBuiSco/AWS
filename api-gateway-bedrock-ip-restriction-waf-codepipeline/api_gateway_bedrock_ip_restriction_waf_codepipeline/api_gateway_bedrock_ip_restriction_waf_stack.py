from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_wafv2 as wafv2,
    CfnOutput,
)
from dotenv import load_dotenv
from constructs import Construct
import os

load_dotenv()

class ApiGatewayBedrockIpRestrictionWafStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # allowed_ip_v6 = os.getenv("YOUR_IP_ADDRESS") + "/128"  # e.g. 2001:db8::/128
        allowed_ip_v6 = self.node.try_get_context("allowed_ip") + "/128"

        # Lambda function to call Bedrock
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

        # IAM permissions for Lambda to invoke Bedrock
        sonnet_fn.role.add_to_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"]
        ))

        # API Gateway
        api = apigw.RestApi(
            self, "SonnetRestApi",
            rest_api_name="Sonnet LLM API",
            deploy_options=apigw.StageOptions(stage_name="prod")
        )

        # /invoke endpoint
        invoke_resource = api.root.add_resource("invoke")
        invoke_resource.add_method(
            "POST",
            apigw.LambdaIntegration(sonnet_fn),
            authorization_type=apigw.AuthorizationType.NONE
        )   
        # Create a low-level CfnStage from the API Gateway stage
        cfn_stage = api.deployment_stage.node.default_child

        # Ensure it's of type CfnStage
        assert isinstance(cfn_stage, apigw.CfnStage)

        # Create an IPSet for WAF with allowed IP
        ip_set = wafv2.CfnIPSet(
            self, "AllowedIPv6Set",
            addresses=[allowed_ip_v6],
            ip_address_version="IPV6",
            scope="REGIONAL",
            name="AllowedIPv6Set"
        )

        # WAF WebACL with allow rule for the IPSet
        web_acl = wafv2.CfnWebACL(
            self, "WebAcl",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            scope="REGIONAL",
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=True,
                metric_name="WebAcl",
                sampled_requests_enabled=True
            ),
            rules=[
                wafv2.CfnWebACL.RuleProperty(
                    name="AllowFromMyIPv6",
                    priority=1,
                    action=wafv2.CfnWebACL.RuleActionProperty(allow={}),
                    statement=wafv2.CfnWebACL.StatementProperty(
                        ip_set_reference_statement=wafv2.CfnWebACL.IPSetReferenceStatementProperty(
                            arn=ip_set.attr_arn
                        )
                    ),
                    visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                        cloud_watch_metrics_enabled=True,
                        metric_name="AllowFromMyIPv6",
                        sampled_requests_enabled=True
                    )
                )
            ]
        )

        # Associate WAF WebACL with API Gateway stage
        wafv2.CfnWebACLAssociation(
            self, "WebAclAssociation",
            resource_arn=f"arn:aws:apigateway:{self.region}::/restapis/{api.rest_api_id}/stages/{cfn_stage.stage_name}",
            web_acl_arn=web_acl.attr_arn
        ).add_dependency(cfn_stage)

        CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway endpoint URL",
            export_name="OpenAIProxyUrl"
        )
