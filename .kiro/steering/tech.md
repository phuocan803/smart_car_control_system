# Technology Stack

## Languages

- Python 3.10+ (primary application logic)
- C++ (Arduino firmware)
- HTML/JavaScript (web interfaces)

## Core Dependencies

```
opencv-python==4.10.0.84    # Computer vision
mediapipe==0.10.14          # Hand detection ML model
pyserial==3.5               # Arduino communication
tkinter                     # GUI (built-in with Python)
Flask                       # Web server (Camera module)
boto3>=1.34.0               # AWS Bedrock (optional, for AI control)
```

## Hardware Communication

- Serial protocol: 9600 baud rate
- Default port: COM8 (Windows)
- Command format: Single character (W/A/S/D/X)
- Streaming rate: 20Hz (50ms intervals)

## Arduino Platform

- Compatible boards: Uno/Mega/Nano
- Motor driver: L298N H-bridge
- Pin configuration:
  - ENA=5, ENB=6 (PWM speed control)
  - IN1=7, IN2=8, IN3=9, IN4=11 (direction)

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Or manual install
pip install opencv-python==4.10.0.84 mediapipe==0.10.14 pyserial==3.5
```

### Running
```bash
# Main launcher (interactive menu)
python run.py

# Direct mode execution
python Hand/openCV.py                    # Test camera only
python UART/transfer_UART.py             # OpenCV mode
python Keyboard/keyboard_control.py      # Keyboard GUI
python Web/web_control.py                # Web server
python Web/aws_web_control.py            # AWS AI control

# Test modes (no Arduino required)
python Keyboard/keyboard_control.py --test
python Web/web_control.py --test
python Web/aws_web_control.py --test
```

### AWS Setup (for AI control)
```bash
# Install AWS dependencies
pip install -r Web/requirements_aws.txt

# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (ap-northeast-1)

# Enable Amazon Nova Sonic 2 in AWS Console
# Bedrock → Model access → Request access
```

### Arduino
```
1. Open Car/SmartCar.ino in Arduino IDE
2. Upload to board
3. Open Serial Monitor (9600 baud)
4. Select mode: [1] OpenCV, [2] Manual, [3] Python Keyboard
```

## Development Tools

- Arduino IDE for firmware development
- Virtual environment recommended for Python
- Auto port detection available via `serial.tools.list_ports`
