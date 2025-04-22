import aws_cdk as core
import aws_cdk.assertions as assertions
from aws_ec2_cicd_example.aws_ec2_cicd_example_stack import AwsEc2CicdExampleStack


# example tests. To run these tests, uncomment this file along with the example
# resource in aws_ec2_cicd_example/aws_ec2_cicd_example_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsEc2CicdExampleStack(app, "aws-ec2-cicd-example")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
