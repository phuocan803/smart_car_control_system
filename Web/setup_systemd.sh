#!/bin/bash
# -*- coding: utf-8 -*-
# setup_systemd.sh - Setup systemd service for SmartCar
# Usage: sudo bash Web/setup_systemd.sh

set -e

echo "=========================================="
echo "SmartCar - systemd Service Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo bash Web/setup_systemd.sh"
    exit 1
fi

# Get current user and directory
CURRENT_USER=${SUDO_USER:-$USER}
CURRENT_DIR=$(pwd)
VENV_PATH="$CURRENT_DIR/venv"
SCRIPT_PATH="$CURRENT_DIR/Web/aws_web_control.py"

echo "User: $CURRENT_USER"
echo "Directory: $CURRENT_DIR"
echo "Virtual env: $VENV_PATH"
echo "Script: $SCRIPT_PATH"
echo ""

# Verify paths exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Run: python3 -m venv venv"
    exit 1
fi

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/smartcar.service"

echo "Creating systemd service file..."

cat > $SERVICE_FILE << EOF
[Unit]
Description=SmartCar AWS Web Control
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$VENV_PATH/bin"
ExecStart=$VENV_PATH/bin/python3 $SCRIPT_PATH
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created: $SERVICE_FILE"
echo ""

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload
echo "✓ Daemon reloaded"
echo ""

# Enable service
echo "Enabling service..."
systemctl enable smartcar
echo "✓ Service enabled (will start on boot)"
echo ""

# Start service
echo "Starting service..."
systemctl start smartcar
echo "✓ Service started"
echo ""

# Wait a moment for service to start
sleep 2

# Check status
echo "=========================================="
echo "Service Status:"
echo "=========================================="
systemctl status smartcar --no-pager
echo ""

# Show useful commands
echo "=========================================="
echo "Useful Commands:"
echo "=========================================="
echo ""
echo "Check status:"
echo "  sudo systemctl status smartcar"
echo ""
echo "View logs:"
echo "  sudo journalctl -u smartcar -f"
echo ""
echo "Restart service:"
echo "  sudo systemctl restart smartcar"
echo ""
echo "Stop service:"
echo "  sudo systemctl stop smartcar"
echo ""
echo "Disable service:"
echo "  sudo systemctl disable smartcar"
echo ""
echo "=========================================="
echo ""

# Get EC2 IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")

echo "Access web interface at:"
echo "  http://$PUBLIC_IP:8080"
echo ""
echo "Setup complete!"
