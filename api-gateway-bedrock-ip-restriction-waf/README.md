# 🚀 Secure Bedrock API with AWS CDK (Python)

This project deploys a secure **REST API** on **Amazon API Gateway** integrated with **AWS Lambda** that invokes a **Claude 3.5 Sonnet model on Amazon Bedrock**. Access is restricted to your own IP address using **AWS WAF (Web Application Firewall)** with IPv6 support.

## 📦 Architecture Overview

- 🔐 **Amazon API Gateway**: Hosts a `POST /invoke` endpoint.
- 🧠 **AWS Lambda**: Handles requests and calls Amazon Bedrock with Sonnet 3.5.
- ⚙️ **Amazon Bedrock**: Anthropic Claude 3.5 Sonnet (June 2024 release).
- 🌐 **AWS WAF**: Restricts API access to your IPv6 address using a Web ACL.

![Architecture Diagram](https://user-images.githubusercontent.com/your_image_placeholder.png)
> *Diagram optional — you can add one for clarity*

---

## 🌱 Prerequisites

Before deploying, ensure you have:

- ✅ [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/home.html)
- ✅ AWS CLI configured
- ✅ Python 3.10 or newer
- ✅ `.env` file with your IPv6 address

### 📄 `.env` example:
```bash
YOUR_IP_ADDRESS=2001:db8:abcd:0012::1
```
---

## 🚀 Deploy the Stack

```bash
# Install dependencies
pip install -r requirements.txt

# Bootstrap your environment (if first time)
cdk bootstrap

# Deploy the stack
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