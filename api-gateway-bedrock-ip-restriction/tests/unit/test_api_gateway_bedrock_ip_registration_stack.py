import aws_cdk as core
import aws_cdk.assertions as assertions
from api_gateway_bedrock_ip_registration.api_gateway_bedrock_ip_registration_stack import (
    ApiGatewayBedrockIpRegistrationStack,
)


# example tests. To run these tests, uncomment this file along with the example
# resource in api_gateway_bedrock_ip_registration/api_gateway_bedrock_ip_registration_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ApiGatewayBedrockIpRegistrationStack(
        app, "api-gateway-bedrock-ip-registration"
    )
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
