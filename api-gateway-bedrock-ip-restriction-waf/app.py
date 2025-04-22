#!/usr/bin/env python3
import os

import aws_cdk as cdk
from api_gateway_bedrock_ip_restriction_waf.api_gateway_bedrock_ip_restriction_waf_stack import (
    ApiGatewayBedrockIpRestrictionWafStack,
)

app = cdk.App()
ApiGatewayBedrockIpRestrictionWafStack(app, "ApiGatewayBedrockIpRestrictionWafStack")

app.synth()
