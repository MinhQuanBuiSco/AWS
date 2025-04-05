import aws_cdk as core
import aws_cdk.assertions as assertions

from step_function_workflow.step_function_workflow_stack import StepFunctionWorkflowStack

# example tests. To run these tests, uncomment this file along with the example
# resource in step_function_workflow/step_function_workflow_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = StepFunctionWorkflowStack(app, "step-function-workflow")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
