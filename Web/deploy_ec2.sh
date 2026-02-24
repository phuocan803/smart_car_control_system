#!/bin/bash
# -*- coding: utf-8 -*-
# deploy_ec2.sh - Quick deployment script for EC2
# Usage: bash Web/deploy_ec2.sh

set -e  # Exit on error

echo "=========================================="
echo "SmartCar AWS Web Control - EC2 Deployment"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}✗ This script is for Linux/EC2 only${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Running on Linux${NC}"

# Update system
echo ""
echo "Step 1: Updating system..."
sudo apt update -qq

# Install Python and pip
echo ""
echo "Step 2: Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python installed: $PYTHON_VERSION${NC}"
else
    echo -e "${YELLOW}Installing Python3...${NC}"
    sudo apt install python3 python3-pip python3-venv -y
fi

# Create virtual environment
echo ""
echo "Step 3: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo ""
echo "Step 4: Installing dependencies..."
pip install -q --upgrade pip
pip install -q boto3 pyserial

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check AWS credentials
echo ""
echo "Step 5: Checking AWS configuration..."

# Check for IAM role (preferred method on EC2)
if curl -s -f -m 2 http://169.254.169.254/latest/meta-data/iam/security-credentials/ > /dev/null 2>&1; then
    ROLE_NAME=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/)
    if [ ! -z "$ROLE_NAME" ]; then
        echo -e "${GREEN}✓ IAM Role detected: $ROLE_NAME${NC}"
        echo -e "${GREEN}✓ No need for AWS credentials${NC}"
    fi
else
    # Check for AWS credentials
    if [ -f ~/.aws/credentials ] || [ ! -z "$AWS_ACCESS_KEY_ID" ]; then
        echo -e "${GREEN}✓ AWS credentials found${NC}"
    else
        echo -e "${YELLOW}⚠ No IAM role or AWS credentials found${NC}"
        echo -e "${YELLOW}Please configure AWS credentials:${NC}"
        echo "  1. Attach IAM role to EC2 instance (recommended)"
        echo "  2. Run: aws configure"
        echo "  3. Set environment variables"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Check Bedrock access
echo ""
echo "Step 6: Checking Bedrock access..."
if command -v aws &> /dev/null; then
    if aws bedrock list-foundation-models --region ap-northeast-1 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Bedrock access confirmed${NC}"
    else
        echo -e "${YELLOW}⚠ Cannot access Bedrock${NC}"
        echo "  Please enable Amazon Nova Sonic in AWS Console:"
        echo "  Bedrock → Model access → Request access"
    fi
else
    echo -e "${YELLOW}⚠ AWS CLI not installed${NC}"
    echo "  Install: sudo apt install awscli -y"
fi

# Check serial port (optional)
echo ""
echo "Step 7: Checking serial port..."
if ls /dev/ttyUSB* > /dev/null 2>&1 || ls /dev/ttyACM* > /dev/null 2>&1; then
    SERIAL_PORT=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
    echo -e "${GREEN}✓ Serial port found: $SERIAL_PORT${NC}"
    
    # Check permissions
    if [ -w "$SERIAL_PORT" ]; then
        echo -e "${GREEN}✓ Serial port is writable${NC}"
    else
        echo -e "${YELLOW}⚠ No write permission on serial port${NC}"
        echo "  Run: sudo chmod 666 $SERIAL_PORT"
        echo "  Or: sudo usermod -a -G dialout $USER (then logout/login)"
    fi
else
    echo -e "${YELLOW}⚠ No serial port found (Arduino not connected)${NC}"
    echo "  Will run in test mode"
fi

# Test the server
echo ""
echo "Step 8: Testing server..."
echo -e "${YELLOW}Starting server in test mode for 5 seconds...${NC}"

# Start server in background
python3 Web/aws_web_control.py --test > /tmp/smartcar_test.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test endpoints
if curl -s http://localhost:8080/status > /dev/null; then
    echo -e "${GREEN}✓ Server is responding${NC}"
    
    # Test status endpoint
    STATUS=$(curl -s http://localhost:8080/status)
    echo "  Status: $STATUS"
else
    echo -e "${RED}✗ Server not responding${NC}"
    cat /tmp/smartcar_test.log
fi

# Stop test server
kill $SERVER_PID 2>/dev/null || true
sleep 1

# Get EC2 public IP
echo ""
echo "Step 9: Getting EC2 information..."
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4 2>/dev/null || echo "127.0.0.1")

echo -e "${GREEN}✓ Public IP: $PUBLIC_IP${NC}"
echo -e "${GREEN}✓ Private IP: $PRIVATE_IP${NC}"

# Summary
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start server:"
echo "   source venv/bin/activate"
echo "   python3 Web/aws_web_control.py --test"
echo ""
echo "2. Access web interface:"
echo "   http://$PUBLIC_IP:8080"
echo ""
echo "3. Test API:"
echo "   curl http://localhost:8080/status"
echo ""
echo "4. Setup systemd service (optional):"
echo "   sudo bash Web/setup_systemd.sh"
echo ""
echo "5. Check security group:"
echo "   Make sure port 8080 is open in EC2 security group"
echo ""
echo "=========================================="
echo ""

# Ask if user wants to start server now
read -p "Start server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting server..."
    echo "Press Ctrl+C to stop"
    echo ""
    python3 Web/aws_web_control.py --test
fi
