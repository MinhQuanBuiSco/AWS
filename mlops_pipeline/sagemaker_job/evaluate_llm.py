import boto3
import os
import json

bucket = os.environ["S3_BUCKET"]
key = "llm-training-output/model/eval_results.json"
local_path = "/tmp/eval_results.json"

s3 = boto3.client("s3")
s3.download_file(bucket, key, local_path)

with open(local_path, "r") as f:
    results = json.load(f)

print(f"Evaluation Results: {json.dumps(results, indent=2)}")
print(f"Perplexity: {results.get('perplexity', 'N/A')}")

output_key = "llm-eval-metrics/eval_results_latest.json"
s3.upload_file(local_path, bucket, output_key)
print(f"Uploaded eval results for manual review: s3://{bucket}/{output_key}")
