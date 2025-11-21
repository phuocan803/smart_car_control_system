# EC2 Deployment Guide - SmartCar AWS Web Control

Hướng dẫn deploy SmartCar lên Amazon EC2.

## EC2 Instance Setup

### 1. Launch EC2 Instance

**Recommended Configuration:**
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.micro (free tier) hoặc t3.small
- Storage: 20GB gp3
- Security Group: Mở port 8080 (HTTP custom)

**Security Group Rules:**
```
Type: Custom TCP
Port: 8080
Source: 0.0.0.0/0 (hoặc IP cụ thể cho bảo mật)
Description: SmartCar Web Control
```

### 2. IAM Role Configuration (Khuyến nghị)

Tạo IAM Role cho EC2 với quyền Bedrock:

**Policy JSON:**
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

**Attach Role to EC2:**
1. EC2 Console → Instances
2. Chọn instance → Actions → Security → Modify IAM role
3. Chọn role vừa tạo → Update IAM role

**Lợi ích:** Không cần AWS credentials, tự động authentication qua instance role.

### 3. Connect to EC2

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

## Installation on EC2

### 1. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Python and Dependencies

```bash
# Python 3 (usually pre-installed on Ubuntu 22.04)
python3 --version

# pip
sudo apt install python3-pip -y

# Virtual environment (recommended)
sudo apt install python3-venv -y
```

### 3. Clone/Upload Project

**Option A: Git Clone**
```bash
cd ~
git clone <your-repo-url> smartcar
cd smartcar
```

**Option B: SCP Upload**
```bash
# From local machine
scp -i your-key.pem -r /path/to/smartcar ubuntu@<EC2_IP>:~/
```

### 4. Install Python Dependencies

```bash
cd ~/smartcar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r Web/requirements_aws.txt

# Or manual install
pip install boto3 pyserial
```

### 5. Configure Serial Port (if using Arduino)

```bash
# Find Arduino port
ls /dev/ttyUSB* /dev/ttyACM*

# Give permission
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyUSB0  # Or your port

# Logout and login again for group changes
```

## Running the Server

### Option 1: Foreground (Testing)

```bash
cd ~/smartcar
source venv/bin/activate

# Test mode (no Arduino)
python3 Web/aws_web_control.py --test

# With Arduino
python3 Web/aws_web_control.py
```

### Option 2: Background with nohup

```bash
cd ~/smartcar
source venv/bin/activate

nohup python3 Web/aws_web_control.py > smartcar.log 2>&1 &

# Check process
ps aux | grep aws_web_control

# View logs
tail -f smartcar.log

# Stop
pkill -f aws_web_control
```

### Option 3: systemd Service (Production)

Create service file:
```bash
sudo nano /etc/systemd/system/smartcar.service
```

Content:
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

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smartcar
sudo systemctl start smartcar

# Check status
sudo systemctl status smartcar

# View logs
sudo journalctl -u smartcar -f

# Restart
sudo systemctl restart smartcar

# Stop
sudo systemctl stop smartcar
```

## Access the Web Interface

### From Internet
```
http://<EC2_PUBLIC_IP>:8080
```

### From EC2 Instance (testing)
```bash
curl http://localhost:8080/status
```

### Test LLM
```bash
curl -X POST http://localhost:8080/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "đi thẳng"}'
```

## AWS Credentials (if not using IAM Role)

### Option 1: AWS CLI
```bash
# Install AWS CLI
sudo apt install awscli -y

# Configure
aws configure
```

### Option 2: Environment Variables
```bash
# Add to ~/.bashrc
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="ap-northeast-1"

# Reload
source ~/.bashrc
```

### Option 3: Credentials File
```bash
mkdir -p ~/.aws
nano ~/.aws/credentials
```

Content:
```ini
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

```bash
nano ~/.aws/config
```

Content:
```ini
[default]
region = ap-northeast-1
output = json
```

## Verify IAM Role (Recommended Method)

```bash
# Check if instance has IAM role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Test Bedrock access
aws bedrock list-foundation-models --region ap-northeast-1
```

## Monitoring

### Check Server Status
```bash
# systemd service
sudo systemctl status smartcar

# Process
ps aux | grep aws_web_control

# Port
sudo netstat -tlnp | grep 8080
```

### View Logs
```bash
# systemd logs
sudo journalctl -u smartcar -f

# nohup logs
tail -f ~/smartcar/smartcar.log

# Real-time monitoring
watch -n 1 'curl -s http://localhost:8080/status | python3 -m json.tool'
```

### Resource Usage
```bash
# CPU and Memory
top
htop  # sudo apt install htop

# Disk
df -h

# Network
sudo iftop  # sudo apt install iftop
```

## Security Best Practices

### 1. Restrict Security Group
```bash
# Only allow specific IPs
Type: Custom TCP
Port: 8080
Source: YOUR_IP/32
```

### 2. Use HTTPS (with nginx reverse proxy)

Install nginx:
```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

Configure nginx:
```bash
sudo nano /etc/nginx/sites-available/smartcar
```

Content:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/smartcar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Firewall
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8080/tcp  # SmartCar (if not using nginx)
sudo ufw enable
```

### 4. Authentication (Optional)

Add basic auth to nginx:
```bash
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd smartcar_user

# Add to nginx config
location / {
    auth_basic "SmartCar Control";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8080;
}
```

## Troubleshooting

### Port 8080 already in use
```bash
# Find process
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

### Permission denied on serial port
```bash
sudo chmod 666 /dev/ttyUSB0
sudo usermod -a -G dialout ubuntu
# Logout and login
```

### boto3 not found
```bash
source venv/bin/activate
pip install boto3
```

### AWS credentials error
```bash
# Check IAM role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Test AWS CLI
aws sts get-caller-identity
```

### LLM not available
```bash
# Check Bedrock access
aws bedrock list-foundation-models --region ap-northeast-1

# Enable model access in AWS Console
# Bedrock → Model access → Request access for Amazon Nova Sonic
```

## Auto-start on Boot

Using systemd (already configured above):
```bash
sudo systemctl enable smartcar
```

Or using crontab:
```bash
crontab -e

# Add line:
@reboot cd /home/ubuntu/smartcar && /home/ubuntu/smartcar/venv/bin/python3 Web/aws_web_control.py > smartcar.log 2>&1 &
```

## Backup and Updates

### Backup
```bash
# Backup project
tar -czf smartcar-backup-$(date +%Y%m%d).tar.gz ~/smartcar

# Download to local
scp -i your-key.pem ubuntu@<EC2_IP>:~/smartcar-backup-*.tar.gz .
```

### Update Code
```bash
cd ~/smartcar
git pull  # If using git

# Or upload new files
# scp -i your-key.pem -r Web/ ubuntu@<EC2_IP>:~/smartcar/

# Restart service
sudo systemctl restart smartcar
```

## Cost Optimization

### EC2 Instance
- Use t3.micro (free tier eligible)
- Stop instance when not in use
- Use Reserved Instances for long-term

### Bedrock
- Amazon Nova Sonic 2: ~$0.0001 per command
- Very affordable for development
- Monitor usage in AWS Cost Explorer

### Data Transfer
- Inbound: Free
- Outbound: First 100GB/month free

## Performance Tuning

### Increase worker threads (if needed)
```python
# In aws_web_control.py
# Use ThreadingHTTPServer for concurrent requests
from http.server import ThreadingHTTPServer

server = ThreadingHTTPServer(('0.0.0.0', SERVER_PORT), SmartCarRequestHandler)
```

### Enable caching
```python
# Cache LLM responses for common commands
from functools import lru_cache

@lru_cache(maxsize=100)
def parse_command_cached(text):
    return self.llm.parse_command(text)
```

## Next Steps

1. ✓ Deploy to EC2
2. ✓ Configure IAM role
3. ✓ Setup systemd service
4. ✓ Test LLM functionality
5. [ ] Add HTTPS with nginx
6. [ ] Setup monitoring (CloudWatch)
7. [ ] Configure auto-scaling (if needed)
8. [ ] Add authentication
9. [ ] Setup CI/CD pipeline

## Support

- EC2 Documentation: https://docs.aws.amazon.com/ec2/
- Bedrock on EC2: https://docs.aws.amazon.com/bedrock/latest/userguide/
- systemd: https://www.freedesktop.org/software/systemd/man/systemd.service.html
