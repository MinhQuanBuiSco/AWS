# AWS CDK API Gateway with Bedrock IP Restriction WAF

This project sets up an AWS infrastructure using AWS CDK to create an API Gateway that integrates with AWS Bedrock, restricts access via IP filtering using WAF (Web Application Firewall), and deploys the infrastructure through a CI/CD pipeline.

## 📦 Architecture Overview

- 🔐 **Amazon API Gateway**: Hosts the `POST /invoke` endpoint.  
- 🧠 **AWS Lambda**: Handles requests and invokes Amazon Bedrock with Claude 3.5 Sonnet.  
- ⚙️ **Amazon Bedrock**: Runs Anthropic Claude 3.5 Sonnet (June 2024 release).  
- 🌐 **AWS WAF**: Restricts API access to your IPv6 address using a Web ACL.  
- 🚀 **AWS CodePipeline**: Provides CI/CD functionality using AWS CodePipeline.

---

## 🌱 Prerequisites

Before deploying, ensure you have:

- ✅ [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/home.html)
- ✅ AWS CLI configured
- ✅ Python 3.10 or newer
- ✅ `.env` file with your IPv6 address

### 📄 `.env` example:
```bash
YOUR_IP_ADDRESS=2001:db8:abcd:0012::1/128
GITHUB_TOKEN=ghp...
```
---


## 🚀 Deploy the Stack

1. Install dependencies:
Ensure you have the required Python packages and CDK. Run:

```bash
  pip install -r requirements.txt
```

2. Generate Secret and Parmeter Store:

```bash
  bash generate_github_secret.sh
```

## Deployment

```bash
  cdk deploy
```

---

## 🌍 Environment Variables for Lambda

These are injected into the Lambda during deployment:

| Variable        | Description                                      |
|----------------|--------------------------------------------------|
| `MODEL_ID`      | Bedrock model ID (e.g. `anthropic.claude-3-5-sonnet-20240620-v1:0`) |
| `BEDROCK_REGION` | AWS region where Bedrock is available (e.g. `ap-northeast-1`) |

---

# 🧪 Test the API

Once deployed, you’ll get an output like:
```bash
https://xxxxxxxxxx.execute-api.region.amazonaws.com/prod/
```
To call your Lambda via API Gateway:

```bash
curl -X POST https://your-api-id.execute-api.your-region.amazonaws.com/prod/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "What is the capital of France?",
    "system_prompt": "You are a geography expert."
}'
```