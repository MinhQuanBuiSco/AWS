from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_s3_assets as s3_assets,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_sagemaker as sagemaker,
    Duration,
)
from constructs import Construct

class LlmPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # SageMaker role
        sagemaker_role = iam.Role(self, "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ]
        )

        # Upload training and evaluation scripts
        script_asset = s3_assets.Asset(self, "ScriptAsset", path="mlops_pipeline/sagemaker_scripts")
        script_s3_uri = script_asset.s3_object_url

        # Step: SageMaker Training
        training_job = tasks.SageMakerCreateTrainingJob(self, "TrainLLM",
            training_job_name=sfn.JsonPath.string_at("$$.Execution.Name"),
            algorithm_specification=tasks.AlgorithmSpecification(
                training_input_mode=tasks.InputMode.FILE,
                training_image_uri="763104351884.dkr.ecr.ap-northeast-1.amazonaws.com/huggingface-pytorch-training:1.13.1-transformers4.26.0-gpu-py39-cu117-ubuntu20.04"
            ),
            input_data_config=[
                tasks.Channel(
                    channel_name="code",
                    data_source=tasks.DataSource(
                        s3_data_source=tasks.S3DataSource(
                            s3_uri=script_s3_uri,
                            s3_data_type=tasks.S3DataType.S3_PREFIX,
                            s3_location_type=tasks.S3LocationType.INPUT
                        )
                    ),
                    input_mode=tasks.InputMode.FILE
                )
            ],
            output_data_config=tasks.OutputDataConfig(
                s3_output_location=script_s3_uri
            ),
            resource_config=tasks.ResourceConfig(
                instance_count=1,
                instance_type="ml.g5.xlarge",
                volume_size=tasks.Size.gibibytes(30)
            ),
            stopping_condition=tasks.StoppingCondition(
                max_runtime=Duration.hours(1)
            ),
            role=sagemaker_role,
            environment={
                "SAGEMAKER_PROGRAM": "train.py"
            }
        )

        # Step: SageMaker Processing for evaluation
        evaluation_job = tasks.SageMakerCreateProcessingJob(self, "EvaluateLLM",
            processing_job_name=sfn.JsonPath.string_at("$$.Execution.Name"),
            processing_resources=tasks.ProcessingResources(
                cluster_config=tasks.ProcessingClusterConfig(
                    instance_count=1,
                    instance_type="ml.m5.large",
                    volume_size=tasks.Size.gibibytes(20)
                )
            ),
            stopping_condition=tasks.StoppingCondition(
                max_runtime=Duration.minutes(30)
            ),
            app_specification=tasks.AppSpecification(
                image_uri="763104351884.dkr.ecr.ap-northeast-1.amazonaws.com/huggingface-pytorch-training:1.13.1-transformers4.26.0-gpu-py39-cu117-ubuntu20.04",
                container_entrypoint=["python3", "/opt/ml/processing/input/evaluate.py"]
            ),
            role=sagemaker_role,
            inputs=[
                tasks.ProcessingInput(
                    input_name="code",
                    source=script_s3_uri,
                    destination="/opt/ml/processing/input"
                )
            ],
            outputs=[
                tasks.ProcessingOutput(
                    output_name="evaluation",
                    source="/opt/ml/processing/output"
                )
            ]
        )

        # Step Function Definition
        definition = training_job.next(evaluation_job)

        # State Machine
        sfn.StateMachine(self, "LLMPipelineStateMachine",
            definition=definition,
            state_machine_name="LLMMLOpsPipeline"
        )
