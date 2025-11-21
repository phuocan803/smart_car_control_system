# EC2 Quick Start - 5 Minutes Setup

Triển khai SmartCar lên EC2 trong 5 phút.

## Prerequisites

- EC2 instance đang chạy (Ubuntu 22.04 LTS)
- Security Group mở port 8080
- SSH access

## Step 1: Connect to EC2 (30 seconds)

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

## Step 2: Run Deployment Script (3 minutes)

```bash
# Clone or upload project
cd ~
# (Assuming project is already uploaded)

# Run deployment script
cd smartcar
bash Web/deploy_ec2.sh
```

Script sẽ tự động:
- ✓ Update system
- ✓ Install Python dependencies
- ✓ Create virtual environment
- ✓ Check AWS credentials/IAM role
- ✓ Test Bedrock access
- ✓ Check serial port
- ✓ Test server

## Step 3: Start Server (30 seconds)

### Option A: Quick Test
```bash
source venv/bin/activate
python3 Web/aws_web_control.py --test
```

### Option B: Production (systemd)
```bash
sudo bash Web/setup_systemd.sh
```

## Step 4: Access Web Interface (30 seconds)

Open browser:
```
http://<EC2_PUBLIC_IP>:8080
```

Test commands:
- Click buttons: W/A/S/D/X
- Type: "đi thẳng", "rẽ trái", "dừng lại"

## Done! 🎉

Total time: ~5 minutes

## IAM Role Setup (Recommended)

### Create IAM Role

1. IAM Console → Roles → Create role
2. Select: AWS service → EC2
3. Add policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:ap-northeast-1::foundation-model/amazon.nova-sonic-v1:0"
        }
    ]
}
```

4. Name: `SmartCarBedrockRole`
5. Create role

### Attach to EC2

1. EC2 Console → Select instance
2. Actions → Security → Modify IAM role
3. Select `SmartCarBedrockRole`
4. Update IAM role

### Verify

```bash
# On EC2
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Should show role name
```

## Security Group Setup

Add inbound rule:

```
Type: Custom TCP
Port: 8080
Source: 0.0.0.0/0 (or your IP for security)
Description: SmartCar Web Control
```

## Enable Amazon Nova Sonic 2

1. AWS Console → Amazon Bedrock
2. Region: ap-northeast-1 (Tokyo)
3. Model access → Request model access
4. Select: Amazon Nova Sonic
5. Submit request
6. Wait for approval (~2-5 minutes)

## Verify Everything Works

```bash
# Check service status
sudo systemctl status smartcar

# Check logs
sudo journalctl -u smartcar -f

# Test API
curl http://localhost:8080/status

# Test LLM
curl -X POST http://localhost:8080/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "đi thẳng"}'
```

## Troubleshooting

### Port 8080 not accessible
```bash
# Check security group in EC2 console
# Check if server is running
sudo systemctl status smartcar
```

### LLM not available
```bash
# Check IAM role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Check Bedrock access
aws bedrock list-foundation-models --region ap-northeast-1

# Enable model in AWS Console
```

### Service won't start
```bash
# Check logs
sudo journalctl -u smartcar -n 50

# Check permissions
ls -la ~/smartcar/Web/aws_web_control.py

# Restart
sudo systemctl restart smartcar
```

## Next Steps

- [ ] Add HTTPS with nginx
- [ ] Setup monitoring
- [ ] Configure auto-scaling
- [ ] Add authentication
- [ ] Setup CloudWatch logs

## Cost Estimate

- EC2 t3.micro: $0.0104/hour (~$7.5/month)
- Bedrock Nova Sonic: ~$0.0001/command
- Data transfer: First 100GB free

Total: ~$8-10/month for development

## Support

Full documentation: [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md)
