# SmartCar Control System

An integrated, multi-modal control platform for autonomous and remote-controlled robotic vehicles. The system combines Computer Vision (OpenCV & MediaPipe), Graphical User Interfaces, Local Network Web Control, AWS Cloud Infrastructure, and AI-driven Natural Language Processing (LangChain & OpenAI).

---

## Project History & Honors

- **Phase 1 (NetSecTour 2025)**: Initial vehicle control modules (Computer Vision hand gesture detection, desktop Tkinter keyboard GUI, local LAN web server, and serial hardware bridge) were originally developed for **NetSecTour 2025** without AI voice capabilities.
- **Phase 2 (Amazon Nova AI Hackathon)**: The system was expanded with Amazon Nova AI speech integration, LangChain natural language processing, AWS EC2 cloud infrastructure, and a local bridge client for submission to the **Amazon Nova AI Hackathon**.
- **Awards & Recognition**:
  - **Top 100 Student Team (Project)** — Amazon Nova AI Hackathon
  - **Feedback Prize Winner** — 1 of 60 Global Cash Prize Winners ($50 Cash Prize)
  - **Devpost Project Page**: [Smart Voice-Controlled Car on Devpost](https://devpost.com/software/smart-voice-controlled-car)

---

## System Overview

The **SmartCar Control System** provides a versatile control ecosystem designed to bridge high-level software interfaces with low-level embedded hardware. The platform supports seven distinct control modes ranging from direct hardware testing to cloud-assisted voice navigation.

### Key Capabilities

- **Computer Vision Tracking**: Touchless vehicle navigation using real-time dual-hand gesture classification powered by MediaPipe Hands and OpenCV.
- **Desktop Graphical Control**: Low-latency keyboard-driven vehicle steering implemented using Python Tkinter GUI components.
- **Local Area Network (LAN) Web Server**: Flask-based HTTP REST service and web control panel allowing local browser-based operation.
- **AWS Cloud Infrastructure & Bridge Client**: Global remote vehicle telemetry and control over the internet using AWS EC2, Nginx reverse proxy, Systemd, and a bi-directional WebSocket/REST bridge.
- **Natural Language & AI Voice Processing**: Hands-free voice navigation using SpeechRecognition, OpenAI GPT models, and LangChain intent extraction.
- **Embedded Arduino Firmware**: Multi-mode serial command interpreter operating at a 20Hz update cycle (50ms interval) with safety auto-stop mechanisms.

---

## System Architecture

```text
+-----------------------------------------------------------------------+
|                           USER INTERFACES                             |
|  +-------------------+  +-------------------+  +-------------------+  |
|  | Web Browser (LAN) |  | Camera Gestures   |  | Voice Input (Mic) |  |
|  +---------+---------+  +---------+---------+  +---------+---------+  |
+------------|----------------------|----------------------|------------+
             |                      |                      |
             v                      v                      v
+-----------------------------------------------------------------------+
|                         PYTHON CONTROL HOST                           |
|  +-------------------+  +-------------------+  +-------------------+  |
|  | Flask Server      |  | MediaPipe Engine  |  | LangChain Agent   |  |
|  +---------+---------+  +---------+---------+  +---------+---------+  |
|            |                      |                      |            |
|            +------------------+   |   +------------------+            |
|                               |   |   |                               |
|                               v   v   v                               |
|                       +-------------------+                           |
|                       | Serial Bridge     |                           |
|                       | (PySerial @ 9600) |                           |
|                       +---------+---------+                           |
+---------------------------------|-------------------------------------+
                                  | USB Serial (/dev/ttyUSB0 or COM3)
                                  v
+-----------------------------------------------------------------------+
|                          EMBEDDED HARDWARE                            |
|  +-----------------------------------------------------------------+  |
|  | Arduino Microcontroller (SmartCar.ino)                          |  |
|  +--------------------------------+--------------------------------+  |
|                                   |                                   |
|                                   v                                   |
|  +-----------------------------------------------------------------+  |
|  | L298N Dual H-Bridge Driver ---> Dual DC Drive Motors            |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
```

---

## Repository Structure

```text
smart_car_control_system/
├── Camera/                          # Video feed capture and streaming
│   ├── web_camera.py               # Flask video streaming server
│   ├── web.html                    # Web interface for camera feed
│   ├── README_CAMERA.md            # Camera setup documentation
│   └── requirements_pi.txt         # Camera module dependencies
├── Car/                             # Microcontroller firmware and serial tests
│   ├── SmartCar.ino                # Arduino C++ firmware (multi-mode interpreter)
│   └── test_car.py                 # Standalone serial test utility
├── Hand/                            # Computer Vision hand gesture processing
│   ├── hand.py                     # MediaPipe hand detector & classifier
│   └── openCV.py                   # Real-time gesture visualization script
├── Keyboard/                        # Graphical desktop control
│   └── keyboard_control.py         # Tkinter GUI keyboard controller
├── LangChain_test/                  # AI voice control & LLM intent agent
│   ├── Voice.py                    # Speech recognition & LangChain module
│   ├── README.md                   # Voice control setup guide
│   └── requirements.txt            # Speech & AI dependencies
├── Test_Zigbee/                     # Wireless communication testing
│   └── test.py                     # Serial communication test script
├── UART/                            # Serial bridge modules
│   ├── UART.py                     # PySerial communication wrapper
│   ├── transfer_UART.py            # Computer Vision to Arduino bridge
│   └── hand.py                     # Gesture detection utility functions
├── Web/                             # Web servers, cloud APIs, and deployment
│   ├── web_control.py              # Local LAN HTTP control server
│   ├── web.html                    # Local web dashboard UI
│   ├── aws_web_voice_control.py    # AWS EC2 cloud web & voice server
│   ├── aws_web_voice.html          # Cloud voice control web interface
│   ├── local_bridge_client.py      # Cloud-to-Arduino bridge client
│   ├── deploy_ec2.sh               # AWS EC2 deployment automation script
│   ├── setup_systemd.sh            # Systemd service setup script
│   ├── README_AWS.md               # AWS deployment guide
│   └── requirements_aws.txt        # Web server dependencies
├── .gitignore                       # Git exclusion rules
├── requirements.txt                 # Unified Python dependencies
├── run.py                           # Master system launcher CLI
└── smartcar_nginx.conf              # Nginx reverse proxy configuration
```

---

## Specifications & Requirements

### Hardware Specifications

| Component | Specification | Function |
|-----------|---------------|----------|
| **Microcontroller** | Arduino Uno / Mega / Nano | Real-time motor PWM control and safety timeouts |
| **Motor Driver** | L298N Dual H-Bridge Driver | Power amplification for DC motors |
| **Drive Motors** | 2x 5V-12V DC Gear Motors | Left and Right wheel propulsion |
| **Camera** | USB Webcam / Raspberry Pi Camera | 720p/1080p video feed for gesture analysis |
| **Host Compute** | Raspberry Pi 4 / PC (Linux / macOS / Windows) | High-level image processing and network bridge |

### Software Prerequisites

- **Python**: 3.10 or higher
- **Arduino IDE**: 1.8.x or 2.x
- **Dependencies**: `opencv-python`, `mediapipe`, `pyserial`, `flask`, `flask-cors`, `requests`, `SpeechRecognition`, `langchain`, `openai`, `pynput`, `Pillow`

---

## Installation & Setup

### 1. Clone Repository & Install Python Dependencies

```bash
git clone https://github.com/phuocan803/smart_car_control_system.git
cd smart_car_control_system

# Install Python requirements
pip install -r requirements.txt
```

### 2. Flash Microcontroller Firmware

1. Open `Car/SmartCar.ino` in Arduino IDE.
2. Connect your Arduino board via USB cable.
3. Select your Board and Serial Port under the **Tools** menu.
4. Upload `SmartCar.ino` to the board.
5. Confirm serial baud rate is set to **9600**.

---

## Operational Modes & Usage

Launch the main interactive launcher:

```bash
python3 run.py
```

### Mode 1: Camera Gesture Test
Visualizes MediaPipe hand tracking and gesture detection without sending serial commands.

```bash
python3 run.py  # Select Option [1]
```

**Gesture Command Mapping:**
- **STOP (`X`)**: No hands detected, invalid pose, or asymmetrical hand state.
- **FORWARD (`W`)**: Both hands closed into fists (<=1 finger extended per hand).
- **REVERSE (`S`)**: Both hands fully open (>=3 fingers extended per hand).
- **LEFT (`A`)**: Right hand raised higher than left hand by more than 80 pixels.
- **RIGHT (`D`)**: Left hand raised higher than right hand by more than 80 pixels.

### Mode 2: OpenCV Gesture Control
Translates real-time camera gesture recognition into serial control codes sent to the vehicle hardware.

```bash
python3 run.py  # Select Option [2]
```

### Mode 3: Keyboard GUI Control
Opens a Tkinter desktop window featuring directional button controls and keyboard bindings (`W`, `A`, `S`, `D`, `X`).

```bash
python3 run.py  # Select Option [3]
```

### Mode 4: LAN Web Control
Starts an HTTP Flask web server providing a responsive web control interface accessible at `http://<HOST_IP>:8080`.

```bash
python3 run.py  # Select Option [4]
```

### Mode 5: Local AWS Server Test
Runs the AWS cloud web server locally for testing and API development.

```bash
python3 run.py  # Select Option [5]
```

### Mode 6: AWS Cloud Bridge Client
Connects the local Arduino serial interface to a remote AWS EC2 cloud instance, enabling remote vehicle control from anywhere over the internet.

```bash
python3 run.py  # Select Option [6]
```

### Mode 7: AI Voice Control (LangChain + OpenAI)
Listens to voice input from the microphone, converts speech to text, and uses LangChain intent classification to control vehicle movement.

```bash
python3 run.py  # Select Option [7]
```

---

## API & Serial Communication Protocol

### Serial Command Protocol (PySerial @ 9600 Baud)

| Command Character | Description | Vehicle Action |
|-------------------|-------------|----------------|
| `W` | Forward | Drive both motors forward |
| `S` | Reverse | Drive both motors in reverse |
| `A` | Left | Turn vehicle left |
| `D` | Right | Turn vehicle right |
| `X` | Stop | Brake and stop all motors |

### REST API Endpoints (LAN & AWS Cloud Web Server)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cmd/W` | GET | Execute Forward command |
| `/cmd/S` | GET | Execute Reverse command |
| `/cmd/A` | GET | Execute Turn Left command |
| `/cmd/D` | GET | Execute Turn Right command |
| `/cmd/X` | GET | Execute Emergency Stop command |
| `/status` | GET | Return vehicle connection and status JSON |
| `/api/voice` | POST | Process voice audio input payload |

---

## AWS Cloud Deployment

To deploy the web control portal on an AWS EC2 instance:

1. Copy repository files to your AWS EC2 instance.
2. Execute the automated deployment script:
   ```bash
   cd Web
   bash deploy_ec2.sh
   ```
3. Configure Nginx reverse proxy using `smartcar_nginx.conf`.
4. Register and start systemd background services using `Web/setup_systemd.sh`.
