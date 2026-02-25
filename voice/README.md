# Voice Control - LangChain & OpenAI Integration

Natural language voice control system for smart vehicles using SpeechRecognition, OpenAI GPT models, and LangChain intent classification.

---

## Capabilities

- **Speech Recognition**: Google Speech Recognition integration for multi-lingual spoken command capture.
- **Contextual Intent Classification**: LangChain and OpenAI GPT integration to understand variable phrasing and intent.
- **Offline Fallback Parser**: Keyword matching algorithm requiring no external API keys.
- **Real-Time Command Dispatch**: Direct UART serial transmission to vehicle microcontroller hardware.
- **Simulation Mode**: Interactive demonstration mode for testing voice recognition without hardware serial links.

---

## Command Phrase Mapping

| Command Code | Action | Example Spoken Variations |
|--------------|--------|---------------------------|
| `W` | Move Forward | `"forward"`, `"go ahead"`, `"drive forward"`, `"move forward"` |
| `S` | Move Reverse | `"reverse"`, `"move back"`, `"go backward"`, `"backward"` |
| `A` | Turn Left | `"left"`, `"turn left"`, `"steer left"`, `"go left"` |
| `D` | Turn Right | `"right"`, `"turn right"`, `"steer right"`, `"go right"` |
| `X` | Stop | `"stop"`, `"halt"`, `"brake"`, `"emergency stop"` |

---

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Note: PyAudio requires native audio compiler libraries:
- **Linux/Ubuntu**: `sudo apt install portaudio19-dev python3-pyaudio`
- **macOS**: `brew install portaudio`
- **Windows**: Download wheel binaries from PyAudio release pages.

### 2. Configure OpenAI API Credentials

Set your API Key in your terminal environment:

```bash
export OPENAI_API_KEY="sk-...your-key..."
```

---

## Execution Modes

### Mode 1: LangChain + OpenAI Intent Parser (Recommended)

```bash
python voice_controller.py
```

### Mode 2: Simple Local Keyword Matcher (Offline Mode)

```bash
python voice_controller.py --simple
```

### Mode 3: Hardware Simulation Mode (No Serial Link)

```bash
python voice_controller.py --demo
```
