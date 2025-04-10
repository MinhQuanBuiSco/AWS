#!/usr/bin/env python3
import os

import aws_cdk as cdk

from mlops_pipeline.mlops_pipeline_stack import MLopsPipelineStack


app = cdk.App()
MLopsPipelineStack(app, "MlopsPipelineStack")

app.synth()
