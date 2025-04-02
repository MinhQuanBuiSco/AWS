cdk deploy SagemakerS3Stack

aws s3 cp model.tar.gz s3://sagemaker-s3-bucket-hf/model.tar.gz

rm model.tar.gz

cdk deploy HuggingfaceSagemakerRealtimeStack

cdk deploy AutoScalingStack