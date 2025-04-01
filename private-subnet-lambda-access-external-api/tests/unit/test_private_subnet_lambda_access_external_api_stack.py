import aws_cdk as core
import aws_cdk.assertions as assertions

from private_subnet_lambda_access_external_api.private_subnet_lambda_access_external_api_stack import PrivateSubnetLambdaAccessExternalApiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in private_subnet_lambda_access_external_api/private_subnet_lambda_access_external_api_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PrivateSubnetLambdaAccessExternalApiStack(app, "private-subnet-lambda-access-external-api")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
