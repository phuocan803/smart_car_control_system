# Project Structure

## Directory Organization

```
SmartCar/
├── Hand/              # Computer vision & gesture recognition
├── UART/              # Serial communication bridge
├── Car/               # Arduino firmware
├── Camera/            # Flask camera streaming server
├── Web/               # HTTP control server
├── Keyboard/          # Tkinter GUI control
├── LangChain (test)/  # Experimental voice control
├── Test_Zigbee/       # Zigbee communication tests
├── run.py             # Main launcher with mode selection
└── requirements.txt   # Python dependencies
```

## Module Responsibilities

### Hand/ - Computer Vision
- `hand.py`: MediaPipe hand detector class with gesture analysis
- `openCV.py`: Standalone camera test with visualization
- Provides: `handDetector` class, gesture recognition logic

### UART/ - Serial Bridge
- `UART.py`: Serial communication controller
- `transfer_UART.py`: OpenCV-to-Arduino bridge (Mode 2)
- `hand.py`: Hand detection utilities
- Handles: Command streaming at 20Hz, auto-stop safety

### Car/ - Firmware
- `SmartCar.ino`: Arduino firmware with 3 modes
- `test_car.py`: Arduino testing script
- Implements: Motor control, mode selection, safety timeouts

### Keyboard/ - GUI Control
- `keyboard_control.py`: Tkinter GUI with W/A/S/D/X buttons
- Features: Test mode, auto-connect, continuous command streaming

### Web/ - Remote Control
- `web_control.py`: HTTP server for LAN control
- `web.html`: Browser interface with responsive design
- `aws_web_control.py`: AWS-enhanced server with LLM integration
- `aws_web.html`: Advanced interface with natural language input
- `requirements_aws.txt`: AWS-specific dependencies
- `README_AWS.md`: AWS setup and usage guide
- Endpoints: `/cmd/<command>`, `/status`, `/llm/parse`

### Camera/ - Streaming
- `web_camera.py`: Flask server for camera streaming
- `web.html`: Camera viewer interface
- `README_CAMERA.md`: Ubuntu setup guide

## Code Conventions

### Python Files
- UTF-8 encoding with BOM: `# -*- coding: utf-8 -*-`
- Header comment with filename, description, date
- Class names: PascalCase (`handDetector`)
- Constants: UPPER_SNAKE_CASE (`COM_PORT`, `BAUD_RATE`)
- Vietnamese comments and UI text

### Arduino Files
- Header comment with mode descriptions
- `#define` for pin configurations and speed constants
- Mode selection via Serial input (1/2/3)
- Function naming: camelCase (`moveForward`, `executeCommand`)

### Command Protocol
- Single character commands: W (forward), S (backward), A (left), D (right), X (stop)
- Uppercase only for consistency
- Continuous streaming (not event-based)

## File Naming
- Python: snake_case (`keyboard_control.py`, `transfer_UART.py`)
- Arduino: PascalCase (`SmartCar.ino`)
- HTML: lowercase (`web.html`)

## Configuration

- Serial port: `/dev/ttyUSB0` (Linux/EC2) or `COM8` (Windows) with auto-detection fallback
- Baud rate: 9600 (standard across all modules)
- Web server: Port 8080
- Camera resolution: 1920x1280, detection confidence 0.7
- AWS Region: ap-northeast-1 (Tokyo)
- AWS Model: amazon.nova-sonic-v1:0 (Amazon Nova Sonic 2)
