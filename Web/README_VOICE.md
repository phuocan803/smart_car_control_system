# SmartCar Voice Control - Complete Guide

Voice input/output control system using Web Speech API and AWS Polly.

## 🎤 Features

### Voice Input
- **Web Speech API** - Browser-based speech recognition
- **Real-time transcription** - See what you say
- **English language** - Optimized for English commands
- **Hands-free control** - No typing needed

### Voice Output
- **AWS Polly** - Neural text-to-speech
- **Natural voice** - Joanna (English female voice)
- **Command confirmation** - Hear responses
- **Error feedback** - Audio error messages

### Text Input
- **Natural language** - Type commands in plain English
- **LLM processing** - Claude 3 Haiku understands context
- **Example commands** - Click to try
- **Keyboard shortcuts** - Press Enter to send

## 🚀 Quick Start

### 1. Start Server
```bash
python3 Web/aws_web_voice_control.py --test
```

### 2. Open Browser
```
http://localhost:8080
```

### 3. Try Voice Control
1. Click the microphone button 🎤
2. Say: "go forward"
3. Hear the confirmation
4. Car moves forward!

## 📋 Voice Commands

### Movement Commands
```
"go forward"    → W (Forward)
"move ahead"    → W (Forward)
"drive forward" → W (Forward)

"turn left"     → A (Left)
"go left"       → A (Left)
"left turn"     → A (Left)

"turn right"    → D (Right)
"go right"      → D (Right)
"right turn"    → D (Right)

"go back"       → S (Backward)
"reverse"       → S (Backward)
"move backward" → S (Backward)

"stop"          → X (Stop)
"halt"          → X (Stop)
"brake"         → X (Stop)
```

## 🔧 Technical Architecture

### Voice Input Flow
```
User speaks
    ↓
Web Speech API (Browser)
    ↓
Transcript text
    ↓
POST /llm/parse (source: 'voice')
    ↓
AWS Bedrock (Claude 3 Haiku)
    ↓
Command (W/A/S/D/X)
    ↓
SmartCar Controller
    ↓
Arduino (Serial)
```

### Voice Output Flow
```
Command executed
    ↓
Explanation text
    ↓
POST /tts
    ↓
AWS Polly (Neural TTS)
    ↓
MP3 audio (base64)
    ↓
Browser Audio API
    ↓
Speaker output
```

## 🌐 Browser Compatibility

### Web Speech API Support
- ✅ Chrome/Edge (Chromium) - Full support
- ✅ Safari (iOS/macOS) - Full support
- ⚠️ Firefox - Limited support
- ❌ Internet Explorer - Not supported

### Recommended Browsers
1. **Chrome** - Best performance
2. **Edge** - Full features
3. **Safari** - iOS/macOS support

## 🔐 AWS Configuration

### Required Services
1. **AWS Bedrock** - LLM processing
2. **AWS Polly** - Text-to-speech

### IAM Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
        },
        {
            "Effect": "Allow",
            "Action": [
                "polly:SynthesizeSpeech"
            ],
            "Resource": "*"
        }
    ]
}
```

### Configuration
```python
# In aws_web_voice_control.py
AWS_REGION = 'ap-southeast-1'
MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'
POLLY_VOICE_ID = 'Joanna'  # English female
```

### Available Polly Voices
```python
# English voices
'Joanna'    # Female (default)
'Matthew'   # Male
'Ivy'       # Female, child
'Joey'      # Male, child
'Kendra'    # Female
'Kimberly'  # Female
'Salli'     # Female
'Justin'    # Male, child
'Kevin'     # Male, child
```

## 📊 API Endpoints

### Voice Command
```bash
POST /llm/parse
Content-Type: application/json

{
    "text": "go forward",
    "source": "voice"
}

Response:
{
    "success": true,
    "command": "W",
    "explanation": "Moving forward",
    "raw_input": "go forward"
}
```

### Text-to-Speech
```bash
POST /tts
Content-Type: application/json

{
    "text": "Moving forward"
}

Response:
{
    "success": true,
    "audio": "base64_encoded_mp3_data",
    "format": "mp3"
}
```

### Status
```bash
GET /status

Response:
{
    "current_command": "W",
    "command_count": 150,
    "llm_command_count": 25,
    "voice_command_count": 10,
    "is_running": true,
    "test_mode": false,
    "llm_available": true,
    "polly_available": true,
    "history": [...]
}
```

## 🎯 Usage Examples

### Voice Control
```javascript
// Browser automatically handles this
1. Click microphone button
2. Speak: "turn left"
3. Hear: "Turning left"
4. Car turns left
```

### Text Control
```javascript
// Type in text box
Input: "move forward"
Response: "✓ Moving forward → W"
Audio: "Moving forward"
```

### Manual Control
```javascript
// Click buttons or press keys
Button: W
Response: Immediate movement
No audio feedback
```

## 🐛 Troubleshooting

### Voice Recognition Not Working

**Issue**: Microphone button disabled
```
Solution: Use Chrome, Edge, or Safari
Check: Browser console for errors
```

**Issue**: "Not allowed to use microphone"
```
Solution: Grant microphone permission
Chrome: Settings → Privacy → Microphone
```

**Issue**: Recognition stops immediately
```
Solution: Check microphone is working
Test: Record audio in another app
```

### Voice Output Not Working

**Issue**: No audio response
```
Check: AWS Polly permissions
Check: Browser audio not muted
Check: Server logs for errors
```

**Issue**: "Polly not available"
```
Solution: Install boto3
Solution: Configure AWS credentials
Solution: Check IAM permissions
```

### LLM Not Understanding Commands

**Issue**: Wrong command executed
```
Solution: Speak clearly
Solution: Use example commands
Solution: Check microphone quality
```

**Issue**: "Invalid command from LLM"
```
Check: Model has access
Check: AWS credentials valid
Check: Server logs for details
```

## 💰 Cost Estimation

### AWS Polly
- **Neural voices**: $16 per 1M characters
- **Average response**: ~20 characters
- **Cost per command**: ~$0.0003
- **1000 commands**: ~$0.30

### AWS Bedrock (Claude 3 Haiku)
- **Input**: ~$0.00025 per 1K tokens
- **Output**: ~$0.00125 per 1K tokens
- **Average command**: ~100 tokens
- **Cost per command**: ~$0.00015
- **1000 commands**: ~$0.15

### Total Cost
- **Per command**: ~$0.00045
- **1000 commands**: ~$0.45
- **Very affordable** for development and testing

## 🔒 Security Considerations

### Microphone Access
- Browser requests permission
- User must explicitly allow
- Can be revoked anytime

### Data Privacy
- Voice data processed in browser
- Only text sent to server
- No audio stored on server

### AWS Security
- Use IAM roles on EC2
- Least privilege permissions
- Enable CloudTrail logging

## 📈 Performance

### Latency
- **Voice recognition**: 1-2 seconds
- **LLM processing**: 0.5-1 second
- **TTS generation**: 0.5-1 second
- **Total**: 2-4 seconds end-to-end

### Optimization Tips
1. Use neural Polly voices (faster)
2. Cache common responses
3. Reduce LLM temperature
4. Use faster model if available

## 🎓 Advanced Usage

### Custom Voice Commands
Edit system prompt in `aws_web_voice_control.py`:
```python
system_prompt = """
Add your custom commands here:
- "full speed" -> W with high speed
- "slow down" -> Reduce speed
"""
```

### Different Polly Voice
```python
POLLY_VOICE_ID = 'Matthew'  # Male voice
POLLY_VOICE_ID = 'Kendra'   # Different female
```

### Multiple Languages
```javascript
// In HTML
recognition.lang = 'vi-VN';  // Vietnamese
recognition.lang = 'ja-JP';  // Japanese
```

## 📚 References

### Web Speech API
- [MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Browser Support](https://caniuse.com/speech-recognition)

### AWS Polly
- [AWS Polly Documentation](https://docs.aws.amazon.com/polly/)
- [Voice List](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)
- [Neural Voices](https://docs.aws.amazon.com/polly/latest/dg/ntts-voices-main.html)

### AWS Bedrock
- [Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude Models](https://docs.anthropic.com/claude/docs)

## 🎉 Summary

You now have a complete voice-controlled SmartCar system with:
- ✅ Voice input (Web Speech API)
- ✅ Voice output (AWS Polly)
- ✅ Natural language understanding (Claude)
- ✅ English interface
- ✅ Real-time feedback
- ✅ Command history
- ✅ Multiple control modes

**Start using**: `python3 Web/aws_web_voice_control.py --test`
