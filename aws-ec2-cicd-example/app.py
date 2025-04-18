#!/usr/bin/env python3
import os

import aws_cdk as cdk

from aws_ec2_cicd_example.pipeline_stack import PipelineStack


app = cdk.App()
PipelineStack(app, "AwsEc2CicdExampleStack")

app.synth()
