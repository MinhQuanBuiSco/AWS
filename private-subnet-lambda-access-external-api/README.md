# 🛠️ Private Subnet Lambda to External API via API Gateway

This AWS CDK project deploys a Lambda function inside a **private subnet** that securely accesses external APIs (e.g., OpenAI) via a **NAT Gateway**. It exposes the Lambda via a **public REST API Gateway** with no authorization (can be 
restricted further).

![private-subnet-lambda-access-external-api](./private-subnet-lambda-access-external-api.png)

---

## 📦 Stack Components

### ✅ VPC
- 2 Availability Zones
- 1 **Public Subnet** (for NAT Gateway)
- 1 **Private Subnet with Egress** (for Lambda)

### ✅ NAT Gateway
- Allows the Lambda in a private subnet to call external APIs (e.g., OpenAI).

### ✅ Lambda Function
- Located in **Private Subnet**
- Uses security group allowing HTTPS (port 443) outbound
- Bundles dependencies with `requirements.txt`
- Environment variable `OPENAI_API_KEY` is loaded from `.env`

### ✅ API Gateway
- Exposes a public `POST /invoke` endpoint
- Directly integrated with Lambda
- No auth (for now)

> 🔐 `.env` should contain:
```env
OPENAI_API_KEY=your-openai-api-key-here
```

---

# Install dependencies

```bash
pip install -r requirements.txt
```
# Bootstrap CDK (if not already)

```bash
cdk bootstrap
```
# Deploy the stack

```bash
cdk deploy
```

## 📬 API Usage

Once deployed, you’ll get an output like:
```bash
https://xxxxxxxxxx.execute-api.region.amazonaws.com/prod/
```
To call your Lambda via API Gateway:

```bash
curl -X POST https://xxxxxxxxxx.execute-api.region.amazonaws.com/prod/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello OpenAI"}'
```
