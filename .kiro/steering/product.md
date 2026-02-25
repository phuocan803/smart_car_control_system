# Smart Car Control System Product Overview

Multi-modal, real-time control platform for robotic vehicles integrating Computer Vision gesture recognition, Graphical User Interfaces, LAN Web Servers, AWS Cloud Infrastructure, and AI Voice Assistants.

## Product History & Honors

- **Phase 1 (NetSecTour 2025)**: Initial vehicle control modules (Computer Vision hand gesture detection, desktop Tkinter keyboard GUI, local LAN web server, and serial hardware bridge) were originally developed for **NetSecTour 2025** without AI voice capabilities.
- **Phase 2 (Amazon Nova AI Hackathon)**: Expanded with Amazon Nova AI speech processing, LangChain natural language understanding, AWS EC2 cloud deployment, and local bridge integration.
- **Awards & Recognition**:
  - **Feedback Prize Winner** — 1 of 60 Global Cash Prize Winners
  - **Official Student Project** — 1 of 102 Global Student Entries (Amazon Nova AI Hackathon)
  - **Devpost Submission**: [NovaDrive: AI Voice-Controlled Smart Car on Devpost](https://devpost.com/software/smart-voice-controlled-car)

## Operational Control Modes

1. **Camera Gesture Test**: Visualizes MediaPipe hand tracking and classification in real-time.
2. **OpenCV Gesture Control**: Translates dual-hand gesture classification into wireless serial control codes.
3. **Desktop Keyboard GUI**: Low-latency vehicle steering using a Tkinter desktop panel.
4. **Local LAN Web Control**: Browser-based REST control interface served via Flask at port 8080.
5. **Local Cloud Server Test**: Local verification environment for AWS cloud web interfaces.
6. **AWS Cloud Bridge Client**: Relays cloud telemetry from AWS EC2 servers to local serial hardware over Zigbee wireless links.
7. **AI Voice Control**: Speech-to-text recognition with LangChain and OpenAI GPT intent classification.

## Key System Features

- Dual-hand gesture navigation (`W`=Forward, `S`=Reverse, `A`=Left, `D`=Right, `X`=Stop)
- Multi-platform access (Desktop GUI, LAN Web Browser, Cloud Web Portal, Voice Input)
- Natural language intent extraction using LangChain and OpenAI
- 20Hz continuous command streaming (50ms interval) with safety auto-stop timeouts
- Standalone hardware simulation modes for development without active microcontrollers
