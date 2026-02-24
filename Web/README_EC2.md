# SmartCar on EC2 - Complete Guide

🚗 Deploy SmartCar với Amazon Nova Sonic 2 trên EC2 instance.

## 📚 Documentation Index

### Quick Start (Choose One)

1. **[EC2_QUICKSTART.md](EC2_QUICKSTART.md)** ⭐ START HERE
   - 5-minute setup guide
   - Minimal steps
   - Perfect for first-time deployment

2. **[QUICKSTART_AWS.md](QUICKSTART_AWS.md)**
   - General AWS setup (works on any machine)
   - Detailed credential configuration
   - Multiple setup options

### Detailed Guides

3. **[EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md)** 📖 COMPREHENSIVE
   - Complete EC2 deployment guide
   - IAM role configuration
   - systemd service setup
   - Security best practices
   - HTTPS with nginx
   - Monitoring and troubleshooting

4. **[README_AWS.md](README_AWS.md)**
   - AWS features documentation
   - API endpoints
   - Natural language examples
   - Cost estimation

### Reference

5. **[AWS_INTEGRATION_SUMMARY.md](AWS_INTEGRATION_SUMMARY.md)**
   - Architecture overview
   - Files created
   - Features list
   - Usage examples

6. **[EC2_FILES_SUMMARY.md](EC2_FILES_SUMMARY.md)**
   - EC2-specific files
   - Configuration differences
   - Common commands
   - Troubleshooting reference

## 🚀 Quick Start (3 Commands)

```bash
# 1. Deploy
bash Web/deploy_ec2.sh

# 2. Setup service
sudo bash Web/setup_systemd.sh

# 3. Access
# Open: http://<EC2_IP>:8080
```

## 📁 Files Overview

### Scripts
- **deploy_ec2.sh** - Automated deployment script
- **setup_systemd.sh** - systemd service installer

### Documentation
- **EC2_QUICKSTART.md** - 5-minute setup
- **EC2_DEPLOYMENT.md** - Complete guide
- **README_AWS.md** - AWS features
- **QUICKSTART_AWS.md** - General AWS setup
- **AWS_INTEGRATION_SUMMARY.md** - Architecture
- **EC2_FILES_SUMMARY.md** - Reference
- **README_EC2.md** - This file

### Application
- **aws_web_control.py** - Python server (EC2-optimized)
- **aws_web.html** - Web interface
- **requirements_aws.txt** - Dependencies

## 🎯 Choose Your Path

### Path 1: Quick Test (5 minutes)
```bash
bash Web/deploy_ec2.sh
# Follow prompts, start server
```
→ Read: [EC2_QUICKSTART.md](EC2_QUICKSTART.md)

### Path 2: Production Setup (15 minutes)
```bash
bash Web/deploy_ec2.sh
sudo bash Web/setup_systemd.sh
# Configure HTTPS, monitoring
```
→ Read: [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md)

### Path 3: Custom Configuration
→ Read: [README_AWS.md](README_AWS.md)
→ Modify: `aws_web_control.py`

## 🔑 Key Features

### EC2-Optimized
- ✓ IAM role support (no credentials needed)
- ✓ Linux serial port (`/dev/ttyUSB0`)
- ✓ systemd service (auto-start)
- ✓ Automated deployment scripts

### AWS Integration
- ✓ Amazon Nova Sonic 2 (ap-northeast-1)
- ✓ Natural language control (Vietnamese + English)
- ✓ Real-time command processing
- ✓ Command history tracking

### Production Ready
- ✓ systemd service management
- ✓ Automatic restart on failure
- ✓ Logging with journalctl
- ✓ Security group configuration

## 📋 Prerequisites

### EC2 Instance
- Ubuntu 22.04 LTS
- t3.micro or larger
- Security group: port 8080 open
- IAM role with Bedrock access (recommended)

### AWS Services
- Amazon Bedrock enabled
- Amazon Nova Sonic 2 access approved
- Region: ap-northeast-1 (Tokyo)

## 🛠️ Installation

### Step 1: Connect to EC2
```bash
ssh -i your-key.pem ubuntu@<EC2_IP>
```

### Step 2: Upload Project
```bash
# Option A: Git
git clone <repo-url> smartcar

# Option B: SCP
scp -i key.pem -r smartcar/ ubuntu@<EC2_IP>:~/
```

### Step 3: Deploy
```bash
cd smartcar
bash Web/deploy_ec2.sh
```

### Step 4: Setup Service (Optional)
```bash
sudo bash Web/setup_systemd.sh
```

## 🌐 Access

### Web Interface
```
http://<EC2_PUBLIC_IP>:8080
```

### API Endpoints
```bash
# Status
curl http://<EC2_IP>:8080/status

# Manual command
curl http://<EC2_IP>:8080/cmd/W

# AI command
curl -X POST http://<EC2_IP>:8080/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "đi thẳng"}'
```

## 🔐 IAM Role Setup

### Create Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "bedrock:InvokeModel",
            "Resource": "arn:aws:bedrock:ap-northeast-1::foundation-model/amazon.nova-sonic-v1:0"
        }
    ]
}
```

### Attach to EC2
1. EC2 Console → Instance
2. Actions → Security → Modify IAM role
3. Select role → Update

### Verify
```bash
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

## 📊 Monitoring

### Service Status
```bash
sudo systemctl status smartcar
```

### Logs
```bash
# Follow logs
sudo journalctl -u smartcar -f

# Last 50 lines
sudo journalctl -u smartcar -n 50
```

### Resource Usage
```bash
top
htop  # sudo apt install htop
```

## 🐛 Troubleshooting

### Quick Checks
```bash
# Is service running?
sudo systemctl status smartcar

# Check logs
sudo journalctl -u smartcar -n 50

# Test endpoint
curl http://localhost:8080/status

# Check IAM role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Port not accessible | Check security group |
| LLM not working | Enable model in Bedrock console |
| Service won't start | Check logs: `journalctl -u smartcar` |
| Permission denied | `sudo chmod 666 /dev/ttyUSB0` |

→ Full troubleshooting: [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md#troubleshooting)

## 💰 Cost Estimate

- **EC2 t3.micro**: ~$7.5/month (free tier eligible)
- **Bedrock Nova Sonic**: ~$0.0001/command
- **Data transfer**: First 100GB free

**Total**: ~$8-10/month for development

## 🔒 Security Best Practices

1. **Use IAM Role** (not credentials)
2. **Restrict Security Group** (specific IPs only)
3. **Enable HTTPS** (nginx + certbot)
4. **Add Authentication** (basic auth or Cognito)
5. **Monitor Logs** (CloudWatch)

→ Details: [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md#security-best-practices)

## 📈 Next Steps

### Immediate
- [ ] Deploy to EC2
- [ ] Test web interface
- [ ] Try AI commands
- [ ] Setup systemd service

### Production
- [ ] Configure HTTPS
- [ ] Add authentication
- [ ] Setup monitoring
- [ ] Configure backups
- [ ] Load testing

### Advanced
- [ ] Auto-scaling
- [ ] Load balancer
- [ ] CI/CD pipeline
- [ ] Multi-region deployment

## 📞 Support

### Documentation
- Quick start: [EC2_QUICKSTART.md](EC2_QUICKSTART.md)
- Full guide: [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md)
- AWS features: [README_AWS.md](README_AWS.md)
- Reference: [EC2_FILES_SUMMARY.md](EC2_FILES_SUMMARY.md)

### AWS Resources
- [EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon Nova Models](https://aws.amazon.com/bedrock/nova/)

### Commands Reference
```bash
# Service management
sudo systemctl {start|stop|restart|status} smartcar

# Logs
sudo journalctl -u smartcar -f

# Testing
curl http://localhost:8080/status

# Deployment
bash Web/deploy_ec2.sh
sudo bash Web/setup_systemd.sh
```

## 🎓 Learning Path

1. **Start**: [EC2_QUICKSTART.md](EC2_QUICKSTART.md)
2. **Deploy**: Run `deploy_ec2.sh`
3. **Test**: Access web interface
4. **Learn**: [README_AWS.md](README_AWS.md)
5. **Production**: [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md)
6. **Optimize**: [EC2_FILES_SUMMARY.md](EC2_FILES_SUMMARY.md)

## ✅ Checklist

### Pre-deployment
- [ ] EC2 instance running
- [ ] Security group configured (port 8080)
- [ ] IAM role created and attached
- [ ] Amazon Nova Sonic 2 enabled

### Deployment
- [ ] Project uploaded to EC2
- [ ] `deploy_ec2.sh` executed successfully
- [ ] Dependencies installed
- [ ] Server tested

### Production
- [ ] systemd service configured
- [ ] Service auto-starts on boot
- [ ] Logs accessible via journalctl
- [ ] Web interface accessible

### Security
- [ ] IAM role used (not credentials)
- [ ] Security group restricted
- [ ] HTTPS configured (optional)
- [ ] Authentication added (optional)

## 🎉 Success Criteria

Your deployment is successful when:

1. ✓ Server responds: `curl http://localhost:8080/status`
2. ✓ Web interface loads: `http://<EC2_IP>:8080`
3. ✓ Manual commands work: Click W/A/S/D/X buttons
4. ✓ AI commands work: Type "đi thẳng" and get response
5. ✓ Service auto-starts: `sudo systemctl status smartcar`

## 📝 Notes

- Default serial port: `/dev/ttyUSB0` (Linux)
- Default web port: `8080`
- Default region: `ap-northeast-1` (Tokyo)
- Model: `amazon.nova-sonic-v1:0`

---

**Ready to deploy?** Start with [EC2_QUICKSTART.md](EC2_QUICKSTART.md) 🚀
