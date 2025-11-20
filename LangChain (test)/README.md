# 🎤 Voice Control - LangChain + OpenAI

Điều khiển SmartCar bằng giọng nói tiếng Việt sử dụng LangChain và OpenAI GPT.

## Tính năng

✅ **Nhận diện tiếng Việt** - Google Speech Recognition  
✅ **LangChain + OpenAI** - Hiểu ngữ cảnh và biến thể lệnh  
✅ **Fallback simple matching** - Không cần API key  
✅ **Real-time control** - Gửi lệnh trực tiếp qua UART  
✅ **Demo mode** - Test không cần Arduino  

## Lệnh hỗ trợ

| Lệnh | Các cách nói |
|------|-------------|
| **W** (Tiến) | tiến, đi thẳng, đi tới, về phía trước, forward |
| **S** (Lùi) | lùi, đi lùi, quay lại, về sau, backward |
| **A** (Trái) | trái, rẽ trái, queo trái, sang trái, left |
| **D** (Phải) | phải, rẽ phải, queo phải, sang phải, right |
| **X** (Dừng) | dừng, stop, đứng lại, ngừng, thôi |

## Cài đặt

### 1. Dependencies

```bash
pip install -r requirements.txt
```

**Lưu ý:** PyAudio cần compiler:

- **Windows:** Tải wheel từ [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- **Linux:** `sudo apt install portaudio19-dev python3-pyaudio`
- **macOS:** `brew install portaudio`

### 2. OpenAI API Key

Lấy API key từ [OpenAI Platform](https://platform.openai.com/api-keys)

**Windows:**

```cmd
set OPENAI_API_KEY=sk-...your-key...
```

**Linux/macOS:**

```bash
export OPENAI_API_KEY=sk-...your-key...
```

**Hoặc tạo file `.env`:**

```
OPENAI_API_KEY=sk-...your-key...
```

### 3. Arduino

```
1. Upload Car/SmartCar.ino
2. Mở Serial Monitor (9600 baud)
3. Chọn [3] - Python Keyboard Mode
```

## Sử dụng

### Mode 1: LangChain + OpenAI (Khuyến nghị)

```bash
python Voice.py
```

- Hiểu ngữ cảnh tốt hơn
- Xử lý biến thể câu phức tạp
- Cần API key ($0.002/1K tokens)

### Mode 2: Simple Matching (Miễn phí)

```bash
python Voice.py --simple
```

- Không cần API key
- Chỉ so khớp từ khóa
- Nhanh hơn nhưng kém linh hoạt

### Mode 3: Demo (Không cần Arduino)

```bash
python Voice.py --demo
```

- Test nhận diện giọng nói
- Không gửi lệnh serial
- In lệnh ra console

## Ví dụ

**LangChain mode:**

```
🎤 Đang nghe...
📝 Nghe được: 'xe đi về phía trước đi'
✅ Lệnh: TIẾN (W)
📤 Đã gửi lệnh [1]

🎤 Đang nghe...
📝 Nghe được: 'quay xe sang bên trái'
✅ Lệnh: TRÁI (A)
📤 Đã gửi lệnh [2]
```

**Simple matching mode:**

```
🎤 Đang nghe...
📝 Nghe được: 'tiến'
✅ Lệnh: TIẾN (W)
📤 Đã gửi lệnh [1]
```

## Cấu hình

Chỉnh sửa `Voice.py`:

```python
COM_PORT = 'COM8'           # COM port Arduino
BAUD_RATE = 9600            # Baud rate
OPENAI_API_KEY = '...'      # Hoặc dùng env variable

# Thêm lệnh mới
COMMANDS = {
    'W': ['tiến', 'forward', 'thêm từ khóa...'],
    # ...
}
```

## Troubleshooting

### Lỗi PyAudio

```bash
# Windows - Tải wheel phù hợp với Python version
pip install PyAudio-0.2.14-cp310-cp310-win_amd64.whl

# Ubuntu
sudo apt install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Microphone không hoạt động

```python
# Liệt kê microphones
import speech_recognition as sr
print(sr.Microphone.list_microphone_names())

# Chọn microphone cụ thể (sửa trong Voice.py)
self.microphone = sr.Microphone(device_index=1)
```

### Nhận diện kém chính xác

- Tăng độ dài timeout: `listen(source, timeout=10)`
- Giảm ambient noise trong phòng
- Nói rõ ràng, gần mic
- Dùng LangChain mode để hiểu ngữ cảnh

### OpenAI API lỗi

```bash
# Kiểm tra API key
echo %OPENAI_API_KEY%  # Windows
echo $OPENAI_API_KEY   # Linux

# Test API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Không kết nối Arduino

- Kiểm tra COM port: Device Manager (Windows)
- Đổi `COM_PORT = 'COM8'` trong code
- Chạy `--demo` mode để test nhận diện

## Chi phí

**OpenAI API:**

- Model: GPT-3.5 Turbo
- Input: $0.0015/1K tokens
- Output: $0.002/1K tokens
- Ước tính: ~5-10 tokens/lệnh = $0.00001/lệnh
- **100 lệnh ≈ $0.001 (rất rẻ)**

**Alternative miễn phí:**

- Simple matching mode (`--simple`)
- Hoặc dùng local LLM (Ollama, LLaMA)

## So sánh modes

| Feature | LangChain | Simple Matching |
|---------|-----------|-----------------|
| Chi phí | $0.00001/lệnh | Miễn phí |
| Độ chính xác | 95%+ | 70-80% |
| Ngữ cảnh | Hiểu tốt | Chỉ từ khóa |
| Latency | ~1-2s | ~0.1s |
| Internet | Cần | Không cần |

## Tích hợp với run.py

Thêm vào `run.py`:

```python
elif choice == '5':
    print("\nMode 5: Voice Control")
    subprocess.run([sys.executable, 'LangChain/Voice.py'])
```
