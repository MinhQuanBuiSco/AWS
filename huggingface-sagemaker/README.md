# 🤗 Hugging Face on Amazon SageMaker (CDK)

This project provisions a real-time Hugging Face model inference endpoint using AWS CDK. It integrates with Amazon SageMaker, S3, and Auto Scaling to deliver efficient and cost-effective model deployment.

---

## 📦 Stack Overview

### 1. `SagemakerS3Stack`
- Creates an S3 bucket (`sagemaker-s3-bucket-hf`)
- Enables automatic deletion of bucket objects upon stack deletion
- Private bucket access (no public access)

### 2. `HuggingfaceSagemakerRealtimeStack`
- Provisions a SageMaker endpoint with:
  - A Hugging Face model container (PyTorch, Transformers)
  - IAM role with S3 read-only and SageMaker full access
- Container Image:
  - `huggingface-pytorch-inference:2.0.0-transformers4.28.1-gpu-py310-cu118-ubuntu20.04`
- Loads model artifact from S3:  
  `s3://sagemaker-s3-bucket-hf/model.tar.gz`
- Endpoint name:  
  `huggingface-realtime-endpoint`

### 3. `AutoScalingStack`
- Applies scheduled auto-scaling on the deployed SageMaker endpoint variant
- Schedules defined in JST (Japan Standard Time):
  - 🕗 **Scale Up**: 8:00 AM (1 instance)
  - 🌙 **Scale Down**: 8:00 PM (3 instances)

---

## 🛠️ Prerequisites

- AWS CLI configured
- Python 3.9+
- AWS CDK v2
- Docker (for building custom models if needed)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Deployment
- Download and prepare artifacts

```bash
bash prepare-artifacts.sh
```

- Deploy all the stacks

```bash
bash deploy.sh
```

## 📌 Notes
Ensure your model.tar.gz is uploaded to the specified S3 bucket before deploying the HuggingfaceSagemakerRealtimeStack.

You can monitor endpoint performance and scaling behavior from the SageMaker Console and CloudWatch Metrics.

## Test

```bash
python tests/test_endpoint.py
```

The result should look like:

```json
[{'entity': 'B-PER', 'score': np.float32(0.9990139), 'index': 4, 'word': 'Wolfgang', 'start': 11, 'end': 19}, {'entity': 'B-LOC', 'score': np.float32(0.999645), 'index': 9, 'word': 'Berlin', 'start': 34, 'end': 40}]
```