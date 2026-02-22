# SmartCar AWS Cloud Control Deployment Guide

Complete setup and operational guide for running the SmartCar Cloud Control Server on AWS EC2 with Amazon Bedrock AI integration.

---

## Overview

The SmartCar AWS Cloud Control service enables vehicle operation over local network (LAN) and global internet connections. It bridges web clients with embedded microcontrollers while utilizing AI foundation models for natural language intent processing.

### Key Features

- **Responsive Web Dashboard**: Touch and keyboard responsive control panel (`W`, `A`, `S`, `D`, `X`).
- **AI Intent Parsing**: Converts natural language command phrases into vehicle control directives using Amazon Bedrock.
- **Telemetry Audit Log**: Real-time tracking of executed manual and AI commands.
- **Status Telemetry**: Periodically broadcasts vehicle connection and command state.
- **Hardware Simulation**: Enables server testing without active serial hardware.

---

## Prerequisites

### Dependencies

```bash
pip install boto3 pyserial flask requests
```

### AWS Bedrock Model Access

- Active AWS account with permissions for Amazon Bedrock foundation models.
- Target Region: `ap-northeast-1` (Tokyo) or `us-east-1` (N. Virginia).
- Model Endpoint: `amazon.nova-sonic-v1:0`

---

## AWS Configuration

### 1. Install & Configure AWS CLI

```bash
aws configure
```

Provide your account credentials:

```text
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: ap-northeast-1
Default output format: json
```

### 2. Verify Bedrock Model Access

```bash
aws bedrock list-foundation-models --region ap-northeast-1
```

---

## Server Execution

### Execution with Serial Hardware

Upload `firmware/smart_car.ino` to your Arduino board and run:

```bash
python3 web/cloud_server.py
```

### Hardware Simulation Mode

Run the server without an active serial hardware connection:

```bash
python3 web/cloud_server.py --test
```

---

## API Specifications

### Directional Control Endpoints

- `GET /cmd/W` — Drive Forward
- `GET /cmd/S` — Drive Reverse
- `GET /cmd/A` — Turn Left
- `GET /cmd/D` — Turn Right
- `GET /cmd/X` — Emergency Stop

### Natural Language Endpoint

- `POST /api/voice` — Payload: `{"text": "drive forward"}`

### System Status Endpoint

- `GET /status` — Returns vehicle connection status and current command telemetry JSON.
