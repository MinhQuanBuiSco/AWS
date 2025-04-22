#!/usr/bin/env python3
import os

import aws_cdk as cdk
from api_gateway_bedrock_ip_restriction_waf_codepipeline.api_gateway_bedrock_ip_restriction_waf_stack import (
    ApiGatewayBedrockIpRestrictionWafStack,
)
from api_gateway_bedrock_ip_restriction_waf_codepipeline.pipeline_stack import (
    PipelineStack,
)

app = cdk.App()

PipelineStack(
    app,
    "BedrockApiPipelineStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
    ),
)

app.synth()
