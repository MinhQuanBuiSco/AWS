import aws_cdk as core
import aws_cdk.assertions as assertions

from api_gateway_bedrock_ip_registration_waf.api_gateway_bedrock_ip_registration_waf_stack import ApiGatewayBedrockIpRegistrationWafStack

# example tests. To run these tests, uncomment this file along with the example
# resource in api_gateway_bedrock_ip_registration_waf/api_gateway_bedrock_ip_registration_waf_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ApiGatewayBedrockIpRegistrationWafStack(app, "api-gateway-bedrock-ip-registration-waf")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
