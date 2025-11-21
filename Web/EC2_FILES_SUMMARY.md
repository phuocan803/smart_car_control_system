# EC2 Deployment Files Summary

## New Files Created for EC2

### 1. Web/aws_web_control.py
- **Updated for EC2**: Changed default COM_PORT to `/dev/ttyUSB0`
- **IAM Role Support**: Automatically uses EC2 instance role if available
- **No credentials needed**: When using IAM role

### 2. Web/EC2_DEPLOYMENT.md
Complete EC2 deployment guide:
- EC2 instance setup
- IAM role configuration
- Installation steps
- systemd service setup
- Security best practices
- HTTPS with nginx
- Monitoring and troubleshooting

### 3. Web/EC2_QUICKSTART.md
5-minute quick start guide:
- Minimal steps to get running
- IAM role setup
- Security group configuration
- Verification steps

### 4. Web/deploy_ec2.sh
Automated deployment script:
- System update
- Python installation
- Virtual environment setup
- Dependency installation
- AWS credentials check
- Bedrock access verification
- Serial port detection
- Server testing

Usage:
```bash
bash Web/deploy_ec2.sh
```

### 5. Web/setup_systemd.sh
systemd service installer:
- Creates service file
- Enables auto-start on boot
- Starts service
- Shows status and commands

Usage:
```bash
sudo bash Web/setup_systemd.sh
```

## EC2-Specific Configuration

### Serial Port
```python
# Linux/EC2
COM_PORT = '/dev/ttyUSB0'  # or /dev/ttyACM0

# Windows (original)
COM_PORT = 'COM8'
```

### IAM Role (Recommended)
No need for AWS credentials when using IAM role:
```bash
# EC2 automatically gets credentials from instance metadata
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

### Security Group
Required inbound rule:
```
Type: Custom TCP
Port: 8080
Source: 0.0.0.0/0 (or specific IP)
```

## Deployment Methods

### Method 1: Quick Test (Development)
```bash
source venv/bin/activate
python3 Web/aws_web_control.py --test
```

### Method 2: Background with nohup
```bash
nohup python3 Web/aws_web_control.py > smartcar.log 2>&1 &
```

### Method 3: systemd Service (Production)
```bash
sudo bash Web/setup_systemd.sh
```

## File Structure on EC2

```
/home/ubuntu/smartcar/
├── venv/                      # Virtual environment
├── Web/
│   ├── aws_web_control.py     # Main server (updated for EC2)
│   ├── aws_web.html           # Web interface
│   ├── requirements_aws.txt   # Dependencies
│   ├── deploy_ec2.sh          # Deployment script ⭐
│   ├── setup_systemd.sh       # Service installer ⭐
│   ├── EC2_DEPLOYMENT.md      # Full guide ⭐
│   ├── EC2_QUICKSTART.md      # Quick start ⭐
│   └── EC2_FILES_SUMMARY.md   # This file ⭐
└── ...

/etc/systemd/system/
└── smartcar.service           # systemd service file
```

## IAM Policy for Bedrock

Minimal policy for SmartCar:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:ap-northeast-1::foundation-model/amazon.nova-sonic-v1:0"
        }
    ]
}
```

## systemd Service Configuration

Location: `/etc/systemd/system/smartcar.service`

```ini
[Unit]
Description=SmartCar AWS Web Control
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/smartcar
Environment="PATH=/home/ubuntu/smartcar/venv/bin"
ExecStart=/home/ubuntu/smartcar/venv/bin/python3 /home/ubuntu/smartcar/Web/aws_web_control.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Common Commands

### Deployment
```bash
# Initial setup
bash Web/deploy_ec2.sh

# Setup systemd
sudo bash Web/setup_systemd.sh
```

### Service Management
```bash
# Status
sudo systemctl status smartcar

# Start
sudo systemctl start smartcar

# Stop
sudo systemctl stop smartcar

# Restart
sudo systemctl restart smartcar

# Enable auto-start
sudo systemctl enable smartcar

# Disable auto-start
sudo systemctl disable smartcar
```

### Logs
```bash
# Follow logs
sudo journalctl -u smartcar -f

# Last 50 lines
sudo journalctl -u smartcar -n 50

# Today's logs
sudo journalctl -u smartcar --since today
```

### Testing
```bash
# Status endpoint
curl http://localhost:8080/status

# Manual command
curl http://localhost:8080/cmd/W

# AI command
curl -X POST http://localhost:8080/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "đi thẳng"}'
```

## Differences from Windows Version

| Feature | Windows | EC2/Linux |
|---------|---------|-----------|
| Serial Port | COM8 | /dev/ttyUSB0 |
| AWS Credentials | Manual config | IAM Role (auto) |
| Service | Manual start | systemd (auto) |
| Deployment | Manual | Automated script |
| Monitoring | Manual | journalctl |
| Auto-start | No | Yes (systemd) |

## Security Considerations

### 1. IAM Role (Best Practice)
- ✓ No credentials in code
- ✓ Automatic rotation
- ✓ Least privilege access
- ✓ Audit trail in CloudTrail

### 2. Security Group
- Restrict port 8080 to specific IPs
- Use VPC for internal access
- Consider using ALB with HTTPS

### 3. HTTPS (Production)
- Use nginx reverse proxy
- Get SSL certificate with certbot
- Redirect HTTP to HTTPS

### 4. Authentication
- Add basic auth to nginx
- Use AWS Cognito
- Implement API keys

## Monitoring

### CloudWatch Logs
```bash
# Install CloudWatch agent
sudo apt install amazon-cloudwatch-agent -y

# Configure to send logs
# /var/log/smartcar.log → CloudWatch
```

### CloudWatch Metrics
- CPU utilization
- Memory usage
- Network traffic
- Custom metrics (command count)

### Alarms
- High CPU usage
- Service down
- High error rate

## Cost Optimization

### EC2
- Use t3.micro (free tier)
- Stop when not in use
- Use Spot instances for dev

### Bedrock
- Cache common commands
- Batch requests if possible
- Monitor usage in Cost Explorer

### Data Transfer
- Keep traffic within same region
- Use CloudFront for static assets

## Backup and Recovery

### Backup
```bash
# Backup project
tar -czf smartcar-backup-$(date +%Y%m%d).tar.gz ~/smartcar

# Backup to S3
aws s3 cp smartcar-backup-*.tar.gz s3://your-bucket/backups/
```

### Recovery
```bash
# Restore from backup
tar -xzf smartcar-backup-20260224.tar.gz

# Or redeploy
bash Web/deploy_ec2.sh
```

## Scaling

### Vertical Scaling
- Upgrade instance type (t3.micro → t3.small)
- Add more memory/CPU

### Horizontal Scaling
- Use Application Load Balancer
- Multiple EC2 instances
- Auto Scaling Group

### Considerations
- Serial port access (only one instance)
- Shared state (use Redis/DynamoDB)
- Session management

## Next Steps

1. ✓ Deploy to EC2
2. ✓ Setup IAM role
3. ✓ Configure systemd
4. ✓ Test functionality
5. [ ] Add HTTPS
6. [ ] Setup monitoring
7. [ ] Configure backups
8. [ ] Add authentication
9. [ ] Setup CI/CD
10. [ ] Load testing

## Support Resources

- [EC2_DEPLOYMENT.md](EC2_DEPLOYMENT.md) - Full deployment guide
- [EC2_QUICKSTART.md](EC2_QUICKSTART.md) - 5-minute setup
- [README_AWS.md](README_AWS.md) - AWS features documentation
- [AWS EC2 Docs](https://docs.aws.amazon.com/ec2/)
- [AWS Bedrock Docs](https://docs.aws.amazon.com/bedrock/)
- [systemd Manual](https://www.freedesktop.org/software/systemd/man/)

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Port not accessible | Check security group |
| LLM not working | Check IAM role, enable model |
| Service won't start | Check logs: `journalctl -u smartcar` |
| Permission denied | `sudo chmod 666 /dev/ttyUSB0` |
| boto3 not found | `pip install boto3` |
| High CPU usage | Check for infinite loops |
| Memory leak | Restart service |

## Contact

For issues or questions:
- Check documentation in Web/ folder
- Review logs: `sudo journalctl -u smartcar -f`
- Test endpoints: `curl http://localhost:8080/status`
