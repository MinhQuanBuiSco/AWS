from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks
from constructs import Construct


class StepFunctionWorkflowStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda functions
        validate_input = self.create_lambda("ValidateInput", "validate_input.py")
        check_credit = self.create_lambda("CheckCredit", "check_credit.py")
        evaluate_risk = self.create_lambda("EvaluateRisk", "evaluate_risk.py")
        finalize_decision = self.create_lambda(
            "FinalizeDecision", "finalize_decision.py"
        )

        # Step Functions Tasks
        validate_task = tasks.LambdaInvoke(
            self,
            "Validate Input",
            lambda_function=validate_input,
            output_path="$.Payload",
        )

        credit_task = tasks.LambdaInvoke(
            self,
            "Check Credit Score",
            lambda_function=check_credit,
            output_path="$.Payload",
        )

        risk_task = tasks.LambdaInvoke(
            self,
            "Evaluate Risk",
            lambda_function=evaluate_risk,
            output_path="$.Payload",
        )

        # Choice state
        is_high_risk = sfn.Choice(self, "High Risk?")

        wait_for_approval = sfn.Wait(
            self,
            "Wait for Manual Approval",
            time=sfn.WaitTime.duration(Duration.seconds(15)),
        )

        finalize_task = tasks.LambdaInvoke(
            self,
            "Finalize Decision",
            lambda_function=finalize_decision,
            output_path="$.Payload",
        )

        # Definition
        definition = (
            sfn.Chain.start(validate_task)
            .next(credit_task)
            .next(risk_task)
            .next(
                is_high_risk.when(
                    sfn.Condition.string_equals("$.risk", "high"),
                    wait_for_approval.next(finalize_task),
                ).otherwise(finalize_task)
            )
        )

        # State machine
        state_machine = sfn.StateMachine(
            self,
            "LoanApplicationStateMachine",
            definition=definition,
            timeout=Duration.minutes(30),
        )

        # Output the state machine ARN
        CfnOutput(self, "StateMachineArn", value=state_machine.state_machine_arn)

    def create_lambda(self, id: str, filename: str) -> _lambda.Function:
        return _lambda.Function(
            self,
            id,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler=filename.replace(".py", ".handler"),
            code=_lambda.Code.from_asset("lambdas"),
        )
