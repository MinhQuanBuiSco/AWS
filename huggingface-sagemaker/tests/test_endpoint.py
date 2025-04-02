import boto3
import json

# Replace with your actual endpoint name
ENDPOINT_NAME = "huggingface-realtime-endpoint"

# Your test input (format depends on your model)
payload = {
    "text": "My name is Wolfgang and I live in Berlin"
}

# Convert to JSON string
input_data = json.dumps(payload)

# Create SageMaker runtime client
runtime = boto3.client("sagemaker-runtime", region_name="ap-northeast-1")

# Invoke endpoint
response = runtime.invoke_endpoint(
    EndpointName=ENDPOINT_NAME,
    ContentType="application/json",
    Body=input_data
)

# Read response
result = response["Body"].read().decode("utf-8")
print("Response from SageMaker endpoint:")
print(result)
