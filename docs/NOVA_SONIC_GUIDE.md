# Amazon Nova Foundation Model Setup Guide

Configuration and integration steps for deploying Amazon Nova AI models on AWS Bedrock for vehicle command intent classification.

---

## AWS Bedrock Configuration Steps

1. Log in to the AWS Management Console.
2. Open the **Amazon Bedrock** service console.
3. Set your active region to `ap-northeast-1` (Tokyo) or `us-east-1` (N. Virginia).
4. Select **Model Access** from the left navigation panel.
5. Request access for **Amazon Nova**.
6. Upon approval, verify access via the AWS CLI:
   ```bash
   aws bedrock list-foundation-models --region ap-northeast-1
   ```

---

## Environment Setup

Configure environment variables for authorization:

```bash
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="ap-northeast-1"
```
