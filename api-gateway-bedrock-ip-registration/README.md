# 🚀 Amazon API Gateway + Lambda + Bedrock (Claude 3.5 Sonnet) — CDK Deployment

This AWS CDK project deploys a REST API using **Amazon API Gateway** that invokes **Amazon Bedrock’s Claude 3.5 Sonnet** via an **AWS Lambda** function. The API is securely restricted to your own **IPv6 address** using API Gateway resource policies.

---

## 📐 Architecture Overview

This stack creates the following resources:

- 🟦 **API Gateway** with a `/invoke` POST endpoint
- 🟨 **Lambda Function** (Python 3.12) that calls Amazon Bedrock
- 🛡️ **IAM Role** with permissions to invoke Bedrock models
- 🔐 **Resource Policy** to restrict API access to a specific IPv6 address

---

## 🧾 Requirements

- Python 3.12+
- AWS CDK v2
- AWS CLI (with configured credentials)
- A valid IPv6 address (you can find yours here: https://whatismyipaddress.com)
- A `.env` file in your project root

### .env_example (remove _example for deploying)
YOUR_IP_ADDRESS=2001:0db8:85a3:0000:0000:8a2e:0370:7334

---

## ⚙️ CDK Stack Highlights (`api_gateway_bedrock_ip_registration_stack.py`)

- **Lambda Function** (Python 3.12) configured with model ID and region via environment variables.
- **IAM Policy** allows Bedrock model invocation.
- **API Gateway** endpoint `/invoke` integrates the Lambda.
- **Resource Policy**:
  - ✅ Allow: Your IPv6 only
  - ❌ Deny: Everyone else

---

## 🌍 Environment Variables for Lambda

These are injected into the Lambda during deployment:

| Variable        | Description                                      |
|----------------|--------------------------------------------------|
| `MODEL_ID`      | Bedrock model ID (e.g. `anthropic.claude-3-5-sonnet-20240620-v1:0`) |
| `BEDROCK_REGION` | AWS region where Bedrock is available (e.g. `ap-northeast-1`) |

---

## 📦 Install & Deploy

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Bootstrap CDK (if first time)**
```bash
cdk bootstrap
```

2. **Deploy the stack**:
```bash
cdk deploy
```

## 🛡️ IP Restriction with API Gateway

To protect your API Gateway endpoint from unauthorized access, this stack uses **resource-based policies** to restrict access to a specific **IPv6 address**.

### ✅ Allow: Your IP Address
Only the IPv6 address you provide in your `.env` file (e.g. `YOUR_IP_ADDRESS=2001:db8::1234`) is allowed to invoke the API:

```json
{
  "Effect": "Allow",
  "Principal": "*",
  "Action": "execute-api:Invoke",
  "Resource": "*",
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": "YOUR_IPV6/128"
    }
  }
}
```

### ❌Deny: Everyone Else
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "execute-api:Invoke",
  "Resource": "*",
  "Condition": {
    "NotIpAddress": {
      "aws:SourceIp": "YOUR_IPV6/128"
    }
  }
}
```

This two-policy combination ensures that only your network can access the API.