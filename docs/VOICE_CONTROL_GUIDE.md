# Smart Car Voice Control Architecture Guide

System architecture, API flow, and command processing for browser speech recognition and AWS Polly text-to-speech feedback.

---

## Technical Architecture

### Voice Command Pipeline

1. **Speech Capture**: Audio recorded via client microphone using standard HTML5 / Web Speech APIs.
2. **Speech-to-Text**: Real-time client-side transcription into text string payload.
3. **Intent Parsing**: Text payload transmitted via HTTP POST to `/api/voice`. LangChain or Amazon Bedrock parses intent into vehicle movement codes (`W`, `A`, `S`, `D`, `X`).
4. **Hardware Dispatch**: Command code transmitted to microcontroller over PySerial UART at 9600 baud rate.
5. **Auditory Feedback**: Response text synthesized via AWS Polly neural text-to-speech engine and played back to the user.

---

## Supported Natural Language Commands

| Vehicle Action | Internal Code | Example Spoken Phrases |
|----------------|---------------|------------------------|
| Move Forward | `W` | `"go forward"`, `"drive ahead"`, `"move forward"` |
| Move Reverse | `S` | `"reverse"`, `"move backward"`, `"go back"` |
| Turn Left | `A` | `"turn left"`, `"steer left"`, `"go left"` |
| Turn Right | `D` | `"turn right"`, `"steer right"`, `"go right"` |
| Emergency Stop | `X` | `"stop"`, `"halt"`, `"brake"` |

---

## Execution Instructions

Run the cloud voice control web application:

```bash
python3 web/cloud_server.py
```

Access the dashboard at `http://localhost:8080` and use the microphone control button for hands-free operation.
