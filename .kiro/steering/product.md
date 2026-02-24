# SmartCar Control System

Multi-mode robotic car control system with AI-powered gesture recognition and remote control capabilities.

## Core Functionality

The system provides 5 control modes:
- OpenCV Mode: AI hand gesture recognition using MediaPipe
- Keyboard GUI: Tkinter-based desktop control interface
- Web Control: Browser-based LAN remote control
- AWS Web Control: Natural language control with Amazon Nova Sonic 2
- Manual Mode: Direct Arduino serial control

## Hardware Platform

Arduino-based robot car with L298N motor driver, dual DC motors, and webcam for computer vision features.

## Key Features

- Real-time hand gesture detection (2-hand recognition)
- Multi-platform control (desktop GUI, web browser, AI vision)
- Natural language control (Vietnamese and English)
- AWS Bedrock integration with Amazon Nova Sonic 2
- Test modes for development without hardware
- Continuous command streaming at 20Hz
- Auto-stop safety mechanisms
- Command history tracking
