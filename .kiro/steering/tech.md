# Technology Stack & Technical Specifications

## Programming Languages

- **Python**: 3.10+ (Core application logic, computer vision, web servers, AI voice processing)
- **C++**: Arduino AVR/SAMD (Microcontroller firmware and motor PWM control)
- **HTML5 / CSS3 / JavaScript (ES6)**: Web interface panels and real-time telemetry display

## Core Dependencies

```text
opencv-python==4.10.0.84    # Computer vision processing
mediapipe==0.10.14          # ML-based hand tracking and landmark classification
pyserial==3.5               # Serial port communication
Flask                       # Web application framework
requests                    # HTTP client for cloud bridge polling
SpeechRecognition           # Microphone audio input capture
langchain                   # LLM orchestration and prompt chaining
langchain-openai            # OpenAI GPT integration
```

## Serial Communication & Hardware Telemetry

- **Baud Rate**: 9600 baud
- **Interface Ports**: `/dev/ttyUSB0` (Linux / Raspberry Pi) or `COM8` / `COM3` (Windows) with auto-detection fallback
- **Wireless Link**: USB Zigbee Transceiver module connected to host PC, wirelessly linked to vehicle Zigbee receiver
- **Update Frequency**: 20Hz continuous command streaming (50ms interval)
- **Command Protocol**: Character codes `W` (Forward), `S` (Reverse), `A` (Left), `D` (Right), `X` (Stop)

## Hardware Components

- **Microcontroller**: Arduino Uno / Mega / Nano
- **Motor Driver**: L298N Dual H-Bridge Driver
- **Pin Assignment**:
  - `ENA` = Pin 5, `ENB` = Pin 6 (PWM speed control)
  - `IN1` = Pin 7, `IN2` = Pin 8, `IN3` = Pin 9, `IN4` = Pin 11 (Directional H-Bridge switches)
- **Drive Motors**: 2x 5V-12V DC Gear Motors

## System Execution Commands

### Environment Setup

```bash
# Clone repository
git clone https://github.com/phuocan803/smart_car_control_system.git
cd smart_car_control_system

# Install Python requirements
pip install -r requirements.txt
```

### System Launcher

```bash
# Interactive CLI menu
python3 run.py
```

### Direct Module Execution

```bash
# Vision gesture visualizer
python3 vision/gesture_visualizer.py

# Computer Vision serial bridge
python3 serial_bridge/gesture_serial_bridge.py

# Graphical desktop keyboard controller
python3 keyboard/keyboard_controller.py

# Local LAN web server
python3 web/local_server.py

# AWS EC2 cloud web server
python3 web/cloud_server.py

# AWS Cloud bridge client
python3 web/cloud_bridge_client.py

# AI Voice controller
python3 voice/voice_controller.py
```

### Simulation & Test Modes (No Hardware Required)

```bash
python3 keyboard/keyboard_controller.py --test
python3 web/local_server.py --test
python3 web/cloud_bridge_client.py --test
```
