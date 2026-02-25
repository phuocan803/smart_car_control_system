# Project Structure & Architecture

## Repository Directory Organization

```text
smart_car_control_system/
├── camera/                           # Video feed capture and web streaming
│   ├── camera_server.py            # Flask video streaming server
│   ├── camera_view.html            # Web interface for camera feed
│   ├── README.md                   # Camera setup documentation
│   └── requirements_pi.txt         # Camera dependencies
├── docs/                             # Project documentation and guides
│   ├── AWS_DEPLOYMENT_GUIDE.md     # AWS EC2 deployment guide
│   ├── VOICE_CONTROL_GUIDE.md      # Voice control architecture guide
│   └── NOVA_SONIC_GUIDE.md         # Amazon Nova AI setup guide
├── firmware/                         # Microcontroller firmware and motor tests
│   ├── smart_car.ino               # Arduino C++ firmware (multi-mode interpreter)
│   └── motor_test.py               # Standalone serial motor test utility
├── keyboard/                         # Desktop GUI control
│   └── keyboard_controller.py      # Tkinter GUI keyboard controller
├── nginx/                            # Web server reverse proxy configuration
│   └── smartcar_nginx.conf         # Nginx configuration file
├── serial_bridge/                    # Serial UART bridge modules
│   ├── serial_interface.py         # PySerial communication wrapper
│   ├── gesture_serial_bridge.py    # Computer Vision to Arduino bridge
│   └── hand_utils.py               # Hand tracking utility helpers
├── vision/                           # Computer Vision hand gesture processing
│   ├── hand_tracker.py             # MediaPipe hand detector & classifier
│   └── gesture_visualizer.py       # Real-time gesture visualization script
├── voice/                            # AI voice control & LLM intent agent
│   ├── voice_controller.py         # Speech recognition & LangChain module
│   ├── README.md                   # Voice control setup guide
│   └── requirements.txt            # Speech & AI dependencies
├── web/                              # Local & Cloud Web control servers
│   ├── local_server.py             # Local LAN HTTP control server
│   ├── local_dashboard.html        # Local web control interface UI
│   ├── cloud_server.py             # AWS EC2 cloud web & voice server
│   ├── cloud_dashboard.html        # Cloud voice control web interface UI
│   ├── cloud_bridge_client.py      # Cloud-to-Arduino bridge client
│   ├── deploy_ec2.sh               # AWS EC2 deployment automation script
│   ├── setup_systemd.sh            # Systemd service installer script
│   └── requirements_aws.txt        # Web server dependencies
├── zigbee/                           # Wireless communication testing
│   └── zigbee_serial_test.py       # Serial communication test script
├── .kiro/                            # Steering documentation
│   └── steering/                   # Technical, product, and structural specifications
├── requirements.txt                 # Unified Python dependencies
├── run.py                           # Master system launcher CLI
└── README.md                         # Main project documentation
```

## Module Responsibilities

### `camera/` — Video Streaming
- `camera_server.py`: Flask MJPEG web streaming server.
- `camera_view.html`: Web interface for live video feed monitoring.

### `vision/` — Computer Vision & Hand Detection
- `hand_tracker.py`: MediaPipe hand detection module with 2-hand gesture analysis.
- `gesture_visualizer.py`: Standalone camera test visualizer displaying real-time hand skeleton and gesture output.

### `serial_bridge/` — Serial Telemetry Link
- `serial_interface.py`: Object-oriented PySerial wrapper with context manager support.
- `gesture_serial_bridge.py`: Computer Vision gesture engine linked to Arduino via serial link.
- `hand_utils.py`: Helper functions for MediaPipe landmark extraction and finger counting.

### `firmware/` — Microcontroller Firmware
- `smart_car.ino`: C++ Arduino firmware implementing motor PWM control, mode selection menus, and safety auto-stop timeouts.
- `motor_test.py`: Standalone motor driver diagnostic script.

### `keyboard/` — Desktop GUI
- `keyboard_controller.py`: Tkinter graphical desktop application supporting keyboard steering (`W`, `A`, `S`, `D`, `X`) and interactive buttons.

### `voice/` — AI Voice Control
- `voice_controller.py`: Natural language voice processing using SpeechRecognition, OpenAI GPT models, and LangChain intent classification.

### `web/` — Web Controls & Cloud Infrastructure
- `local_server.py` & `local_dashboard.html`: LAN HTTP REST control server.
- `cloud_server.py` & `cloud_dashboard.html`: Remote web gateway for AWS EC2 cloud deployments.
- `cloud_bridge_client.py`: Local bridge client linking remote AWS cloud servers with local Zigbee serial hardware.

## Coding Conventions

- **Clean Technical English**: All comments, docstrings, console logs, and UI components are strictly written in 100% icon-free, emoji-free technical English.
- **Python Conventions**: Lowercase `snake_case` filenames, PEP 8 styling, explicit imports, UTF-8 encoding.
- **Arduino Conventions**: Standard C++ camelCase function names, uppercase macro definitions (`#define`), explicit pin mapping.
- **Command Protocol**: Character codes `W` (Forward), `S` (Reverse), `A` (Left), `D` (Right), `X` (Stop).
