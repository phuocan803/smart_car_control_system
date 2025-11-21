# AWS Integration Summary

## Files Created

### 1. Web/aws_web_control.py
Python HTTP server với AWS Bedrock integration:
- `AWSBedrockLLM` class: Wrapper cho Amazon Nova Sonic 2
- `SmartCarController`: Enhanced controller với LLM support
- `SmartCarRequestHandler`: HTTP endpoints cho manual và AI control
- Endpoints:
  - `GET /` - Serve HTML interface
  - `GET /status` - System status JSON
  - `GET /cmd/<command>` - Manual command (W/A/S/D/X)
  - `POST /llm/parse` - Natural language parsing

### 2. Web/aws_web.html
Modern web interface với:
- Dual control modes: Manual buttons + Natural language input
- Real-time status dashboard
- Command history với source tracking (manual/AI)
- Responsive design
- Example commands (Vietnamese + English)
- Keyboard shortcuts support

### 3. Web/README_AWS.md
Comprehensive documentation:
- Feature overview
- AWS setup instructions (CLI, credentials, Bedrock access)
- Usage examples (Vietnamese + English)
- API documentation
- Troubleshooting guide
- Cost estimation
- Code architecture

### 4. Web/QUICKSTART_AWS.md
Quick start guide:
- Step-by-step setup (5 steps)
- Multiple credential configuration options
- Test commands
- Troubleshooting checklist
- API testing examples

### 5. Web/requirements_aws.txt
AWS-specific dependencies:
```
boto3>=1.34.0
pyserial==3.5
```

### 6. Web/AWS_INTEGRATION_SUMMARY.md
This file - overview of all changes

## Updated Files

### 1. run.py
Added Mode 5: AWS Web Control
- New menu option
- Launch aws_web_control.py

### 2. .kiro/steering/product.md
Updated to reflect:
- 5 control modes (added AWS Web Control)
- Natural language control feature
- AWS Bedrock integration
- Command history tracking

### 3. .kiro/steering/tech.md
Added:
- boto3 dependency
- AWS setup commands
- aws_web_control.py execution
- AWS configuration instructions

### 4. .kiro/steering/structure.md
Updated Web/ module documentation:
- New files: aws_web_control.py, aws_web.html
- New endpoint: /llm/parse
- AWS-specific files

## Features

### Natural Language Control
- Parse Vietnamese and English commands
- Convert to W/A/S/D/X commands
- Real-time feedback with explanations

### Dual Control Modes
- Manual: Click buttons or press keys (W/A/S/D/X)
- AI: Type natural language commands

### Command Tracking
- Separate counters for manual vs AI commands
- Command history with timestamps
- Source identification (manual/llm)

### Test Mode
- Run without Arduino: `--test` flag
- Test LLM without hardware
- Development-friendly

### AWS Integration
- Amazon Nova Sonic 2 (amazon.nova-sonic-v1:0)
- Region: ap-northeast-1 (Tokyo)
- Graceful fallback if LLM unavailable
- Optional: `--no-llm` flag

## Architecture

```
User Input
    ↓
┌─────────────────────────────────┐
│   Web Interface (aws_web.html)  │
│   - Manual buttons              │
│   - Natural language input      │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  HTTP Server (aws_web_control)  │
│  - GET /cmd/<command>           │
│  - POST /llm/parse              │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│    AWSBedrockLLM (if AI mode)   │
│    - Parse natural language     │
│    - Return W/A/S/D/X           │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│    SmartCarController           │
│    - Continuous streaming 20Hz  │
│    - Command history            │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│    Serial (pyserial)            │
│    - COM8, 9600 baud            │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│    Arduino (SmartCar.ino)       │
│    - Mode 3: Python Keyboard    │
│    - Motor control              │
└─────────────────────────────────┘
```

## Usage Examples

### Start Server
```bash
# With Arduino
python Web/aws_web_control.py

# Test mode (no Arduino)
python Web/aws_web_control.py --test

# No LLM (manual only)
python Web/aws_web_control.py --no-llm
```

### Natural Language Commands

Vietnamese:
- "đi thẳng" → W (forward)
- "rẽ trái" → A (left)
- "quay phải" → D (right)
- "lùi lại" → S (backward)
- "dừng lại" → X (stop)

English:
- "go forward" → W
- "turn left" → A
- "turn right" → D
- "go backward" → S
- "stop" → X

### API Calls

Manual:
```bash
curl http://localhost:8080/cmd/W
```

AI:
```bash
curl -X POST http://localhost:8080/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "đi thẳng"}'
```

Status:
```bash
curl http://localhost:8080/status
```

## Configuration

### AWS Credentials
Three options:
1. AWS CLI: `aws configure`
2. Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
3. Credentials file: `~/.aws/credentials`

### Model Configuration
```python
# In aws_web_control.py
AWS_REGION = 'ap-northeast-1'
MODEL_ID = 'amazon.nova-sonic-v1:0'
```

### Serial Configuration
```python
COM_PORT = 'COM8'  # Change as needed
BAUD_RATE = 9600
SERVER_PORT = 8080
```

## Testing Checklist

- [ ] Install boto3: `pip install boto3`
- [ ] Configure AWS credentials
- [ ] Enable Amazon Nova Sonic 2 in AWS Console
- [ ] Test LLM: `python Web/aws_web_control.py --test`
- [ ] Try Vietnamese commands
- [ ] Try English commands
- [ ] Upload Arduino firmware
- [ ] Test with Arduino
- [ ] Test manual control
- [ ] Test AI control
- [ ] Check command history
- [ ] Test from mobile device (LAN)

## Cost Estimation

Amazon Nova Sonic 2 (ap-northeast-1):
- Input: ~$0.0006 per 1K tokens
- Output: ~$0.0024 per 1K tokens
- Average command: ~50-100 tokens
- Cost per command: ~$0.0001
- 1000 commands: ~$0.10

Very affordable for development and testing!

## Next Steps

1. Test the integration
2. Customize system prompt for better accuracy
3. Add more complex commands
4. Integrate with camera streaming
5. Add voice input (Web Speech API)
6. Deploy to cloud (EC2, Lambda)

## Support

- AWS Bedrock: https://docs.aws.amazon.com/bedrock/
- Amazon Nova: https://aws.amazon.com/bedrock/nova/
- boto3: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
