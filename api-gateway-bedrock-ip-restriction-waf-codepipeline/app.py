#!/usr/bin/env python3
import os

import aws_cdk as cdk

from api_gateway_bedrock_ip_restriction_waf_codepipeline.api_gateway_bedrock_ip_restriction_waf_stack import ApiGatewayBedrockIpRestrictionWafStack
from api_gateway_bedrock_ip_restriction_waf_codepipeline.pipeline_stack import PipelineStack

app = cdk.App()
app_stack = ApiGatewayBedrockIpRestrictionWafStack(app, "ApiGatewayBedrockIpRestrictionWafStack")


PipelineStack(app, "BedrockApiPipelineStack", cdk_app_stack=app_stack)

app.synth()
