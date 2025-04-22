#!/usr/bin/env python3
import os

import aws_cdk as cdk
from huggingface_sagemaker.auto_scaling_stack import AutoScalingStack
from huggingface_sagemaker.huggingface_sagemaker_stack import (
    HuggingfaceSagemakerRealtimeStack,
)
from huggingface_sagemaker.s3bucket import SagemakerS3Stack

app = cdk.App()

SagemakerS3Stack(app, "SagemakerS3Stack")

HuggingfaceSagemakerRealtimeStack(
    app,
    "HuggingfaceSagemakerRealtimeStack",
)

AutoScalingStack(app, "AutoScalingStack")

app.synth()
