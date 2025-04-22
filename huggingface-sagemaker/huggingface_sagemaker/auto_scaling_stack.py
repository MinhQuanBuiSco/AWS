from aws_cdk import Stack, TimeZone
from aws_cdk import aws_applicationautoscaling as appscaling
from constructs import Construct


class AutoScalingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        scalable_target = appscaling.ScalableTarget(
            self,
            "SageMakerEndpointVariantScaling",
            service_namespace=appscaling.ServiceNamespace.SAGEMAKER,
            max_capacity=3,
            min_capacity=1,
            resource_id=f"endpoint/huggingface-realtime-endpoint/variant/AllTraffic",
            scalable_dimension="sagemaker:variant:DesiredInstanceCount",
        )

        # Schedule to scale up at 8 AM JST
        scalable_target.scale_on_schedule(
            "ScaleOutInMorning",
            schedule=appscaling.Schedule.cron(
                minute="0",
                hour="8",
            ),
            min_capacity=1,
            max_capacity=1,
            time_zone=TimeZone.ASIA_TOKYO,
        )

        # Schedule to scale down at 8 PM JST
        scalable_target.scale_on_schedule(
            "ScaleInAtNight",
            schedule=appscaling.Schedule.cron(
                minute="00",
                hour="20",
            ),
            min_capacity=3,
            max_capacity=3,
            time_zone=TimeZone.ASIA_TOKYO,
        )
