# SmartCar - Control System

Hệ thống điều khiển xe thông minh với 5 chế độ: OpenCV, Keyboard GUI, Web Control (LAN), AWS Web Voice Control (Cloud), Manual.

---

## Cấu trúc thư mục

```
Demo/
├── Hand/
│   ├── hand.py           - MediaPipe hand detection & gesture analysis
│   └── openCV.py         - Camera test with visualization
├── UART/
│   ├── UART.py           - Serial communication controller
│   ├── transfer_UART.py  - OpenCV to Arduino bridge
│   └── hand.py           - Hand detection utilities
├── Car/
│   ├── SmartCar.ino      - Arduino firmware (3 modes)
│   └── test_car.py       - Arduino test script
├── Camera/
│   ├── web_camera.py     - Flask camera streaming server
│   ├── web.html          - Camera web interface
│   ├── README_CAMERA.md  - Camera setup guide (Ubuntu)
│   └── requirements_pi.txt - Camera dependencies
├── Web/
│   ├── web_control.py    - HTTP server for LAN control
│   ├── web.html          - Web control interface
│   ├── aws_web_voice_control.py - AWS cloud server with voice
│   ├── aws_web_voice.html       - Voice control web interface
│   ├── local_bridge_client.py   - Bridge: EC2 ↔ Arduino
│   ├── deploy_ec2.sh     - AWS deployment script
│   ├── setup_systemd.sh  - Systemd service setup
│   ├── README_AWS.md     - AWS deployment guide
│   └── requirements_aws.txt - AWS dependencies
├── Keyboard/
│   └── keyboard_control.py - GUI keyboard control (Tkinter)
├── LangChain (test)/
│   ├── Voice.py          - Voice control with LangChain + OpenAI
│   ├── README.md         - Voice control guide
│   └── requirements.txt  - Voice control dependencies
├── Test_Zigbee/
│   └── test.py           - Zigbee communication test
├── run.py                - Main launcher
└── requirements.txt      - Main dependencies
```

---

## Yêu cầu hệ thống

**Hardware:**

- Arduino (Uno/Mega/Nano)
- L298N Motor Driver
- 2 DC Motors
- Webcam (cho OpenCV mode)

**Software:**

- Python 3.10+
- Arduino IDE
- Libraries: opencv-python, mediapipe, pyserial, tkinter

---

## Cài đặt

```bash
git clone https://github.com/phuocan803/<link>
cd <link>

# Cài đặt dependencies
pip install -r requirements.txt

# Hoặc cài đặt thủ công:
pip install opencv-python==4.10.0.84 mediapipe==0.10.14 pyserial==3.5
```

---

## 5 Chế độ điều khiển

### Mode 1: Test Camera

Test nhận diện cử chỉ tay (không cần Arduino).

```bash
.venv/Scripts/python.exe run.py
# Chọn [1] - Test Camera
```

**Cử chỉ:**

- X = DỪNG (không có tay / thiếu tay / 2 tay khác trạng thái)
- W = TIẾN (2 tay nắm chặt: <=1 ngón duỗi)
- S = LÙI (2 tay xòe ra: >=3 ngón duỗi)
- A = TRÁI (tay phải cao hơn tay trái >80px)
- D = PHẢI (tay trái cao hơn tay phải >80px)

---

### Mode 2: OpenCV Mode

Điều khiển xe bằng cử chỉ tay qua camera.

**Bước 1: Arduino**

```
1. Mở Arduino IDE
2. Upload Car/SmartCar.ino
3. Mở Serial Monitor (9600 baud)
4. Chọn [1] - OpenCV Mode
```

**Bước 2: Python**

```bash
.venv/Scripts/python.exe run.py
# Chọn [2] - OpenCV Mode
# Làm cử chỉ tay trước camera
```

**Đặc điểm:**

- Gửi lệnh 20Hz (mỗi 50ms)
- Auto-stop khi mất tay
- Log chỉ hiện khi lệnh thay đổi
- Camera 1920x1280, detector confidence 0.7

---

### Mode 3: Keyboard GUI

Điều khiển bằng giao diện Tkinter với 5 nút màu.

**Bước 1: Arduino**

```
Upload SmartCar.ino và chọn [3] - Python Keyboard Mode
```

**Bước 2: Python**

```bash
.venv/Scripts/python.exe run.py
# Chọn [3] - Keyboard Mode

# Test mode (không cần Arduino):
.venv/Scripts/python.exe keyboard_control.py --test
```

**Điều khiển:**

- Nhấn W/A/S/D/X trên bàn phím
- Hoặc click chuột vào nút
- Nhấn ESC để thoát
- Gửi lệnh liên tục 20Hz

---

### Mode 4: Web Control

Server HTTP cho phép điều khiển qua LAN (browser/curl).

**Bước 1: Arduino**

```
Upload SmartCar.ino và chọn [3] - Python Keyboard Mode
```

**Bước 2: Python**

```bash
.venv/Scripts/python.exe run.py
# Chọn [4] - Web Control

# Test mode (không cần Arduino):
.venv/Scripts/python.exe Web/web_control.py --test
```

**Sử dụng:**

*Browser:* Mở `http://<IP>:8080` trên bất kỳ thiết bị nào trong LAN

*curl:*

```bash
curl http://<IP>:8080/cmd/W  # Tiến
curl http://<IP>:8080/cmd/A  # Trái
curl http://<IP>:8080/cmd/S  # Lùi
curl http://<IP>:8080/cmd/D  # Phải
curl http://<IP>:8080/cmd/X  # Dừng
curl http://<IP>:8080/status # Trạng thái
```

**Đặc điểm:**

- Giao diện web responsive
- Real-time status update 500ms
- Hỗ trợ keyboard trên web
- Multi-user support

---

### Mode 5: AWS Web Voice Control

Server AWS EC2 với điều khiển bằng giọng nói và natural language qua internet.

**⚠️ LƯU Ý QUAN TRỌNG:**

- **Server đã chạy sẵn trên EC2** → <https://voicecar.pngha.io.vn/>
- **KHÔNG cần chạy Mode 5** để điều khiển xe
- Mode 5 chỉ dành cho admin/developer test server local
- **Để điều khiển xe**: Dùng **Mode 6 (Bridge Client)** + Mở browser

**Đặc điểm:**

- ✅ Host trên AWS EC2 (Singapore) - chạy 24/7
- ✅ Truy cập từ bất kỳ đâu: <https://voicecar.pngha.io.vn/>
- ✅ Voice input: Web Speech API (browser-based)
- ✅ Natural language: "go forward", "turn left", "stop"...
- ✅ Keyword matching (không cần AWS Bedrock)
- ✅ Command history tracking

**Kiến trúc:**

```
Browser (anywhere)
    ↓ HTTPS
EC2 Server (voicecar.pngha.io.vn) ← Server đã sẵn!
    ↓ HTTP Polling  
Bridge Client (Mode 6) ← Chạy cái này trên máy local!
    ↓ Serial/Zigbee
Arduino + SmartCar
```

**Cách sử dụng đúng:**

1. **Upload SmartCar.ino** lên Arduino → Chọn Mode [3]
2. **Chạy Mode 6** (Bridge Client) trên máy có Arduino:

   ```bash
   .venv/Scripts/python.exe run.py
   # Chọn [6] - Bridge Client
   # Chọn [2] - Arduino Mode
   ```

3. **Mở browser** bất kỳ đâu: <https://voicecar.pngha.io.vn/>
4. **Điều khiển** bằng voice/button/keyboard

**API Endpoints (cho developers):**

- Keyboard (W/A/S/D/X)

*API/curl:*

```bash
# Direct commands
curl https://voicecar.pngha.io.vn/cmd/W
curl https://voicecar.pngha.io.vn/cmd/A
curl https://voicecar.pngha.io.vn/cmd/X

# Natural language
curl -X POST https://voicecar.pngha.io.vn/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "go forward", "source": "llm"}'

# Status
curl https://voicecar.pngha.io.vn/status
```

**Chạy server (trên EC2):**

```bash
cd Web
python aws_web_voice_control.py --test  # Test mode
# hoặc
python aws_web_voice_control.py         # Arduino mode
```

---

### Mode 6: Bridge Client

Bridge client kết nối AWS EC2 server với Arduino local qua Zigbee/Serial.

**Chức năng:**

- Poll lệnh từ EC2 server (100ms interval)
- Forward lệnh xuống Arduino qua Serial/Zigbee
- Gửi lệnh liên tục như web_control.py
- Hiển thị log mọi thay đổi lệnh

**Workflow:**

```
Web Browser (anywhere)
    ↓ HTTPS
AWS EC2 Server (voicecar.pngha.io.vn)
    ↓ HTTP Polling (100ms)
Local Bridge Client (máy có Arduino)
    ↓ Serial/Zigbee
Arduino + SmartCar
```

**Sử dụng:**

```bash
# Qua run.py
.venv/Scripts/python.exe run.py
# Chọn [6] - Bridge Client
# Chọn [1] - Test Mode (không cần Arduino)
# hoặc [2] - Arduino Mode

# Trực tiếp
cd Web
python local_bridge_client.py --test    # Test mode
python local_bridge_client.py           # Arduino mode
python local_bridge_client.py COM8      # Chỉ định COM port
```

**Yêu cầu:**

- Arduino upload SmartCar.ino, chọn Mode [3]
- Cài requests: `pip install requests`
- Máy có internet để kết nối EC2

**Output:**

```
[01:01:01] Lệnh mới: X → W (#175)  ← Forward
[01:01:03] Lệnh mới: W → A (#182)  ← Left
[01:01:07] Lệnh mới: A → D (#190)  ← Right
[01:01:11] Lệnh mới: D → S (#195)  ← Backward
[01:01:11] Lệnh mới: S → X (#196)  ← Stop
```

---

## Arduino Modes

**SmartCar.ino có 3 modes:**

1. **OpenCV Mode** - Nhận X/W/S/A/D từ Python, auto-stop 500ms
2. **Manual Mode** - Serial Monitor với speed control (1-9)
3. **Python Keyboard Mode** - Nhận lệnh liên tục từ Python GUI/Web

**Pins L298N:**

```
ENA = 5   (PWM Motor A)
ENB = 6   (PWM Motor B)
IN1 = 7   (Direction A1)
IN2 = 8   (Direction A2)
IN3 = 9   (Direction B1)
IN4 = 11  (Direction B2)
```

---

## So sánh các chế độ

| Tính năng | Test Camera | OpenCV | Keyboard GUI | Web Control | AWS Voice | Bridge Client |
|-----------|-------------|--------|--------------|-------------|-----------|---------------|
| Cần Arduino | Không | Có | Có | Có | Không* | Có |
| Cần Camera | Có | Có | Không | Không | Không | Không |
| Interface | OpenCV | OpenCV | Tkinter GUI | Browser | Browser | Terminal |
| Test Mode | N/A | Không | Có | Có | Có | Có |
| Multi-user | Không | Không | Không | Có | Có | Có |
| Voice Control | Không | Không | Không | Không | Có | N/A |
| Natural Language | Không | Không | Không | Không | Có | N/A |
| Remote Access | Không | Không | Không | LAN only | Internet | N/A |
| Use case | Test | Demo AI | Development | LAN Control | Cloud Control | Bridge AWS→Arduino |

*AWS Voice chạy trên EC2, cần Bridge Client để kết nối Arduino

---

## Logic nhận diện cử chỉ

**File: Hand/hand.py**

1. **getAllHandsPosition()** - Phát hiện 2 tay, phân biệt trái/phải
2. **countExtendedFingers()** - Đếm 4 ngón duỗi (không tính ngón cái)
3. **getHandHeight()** - Tính vị trí dọc trung bình
4. **analyzeGesture()** - Quyết định lệnh

**Ưu tiên:**

1. Kiểm tra rẽ (độ cao) → A/D
2. Kiểm tra nắm/xòe → W/S
3. Nếu không khớp → X (dừng)

---

## Troubleshooting

**Camera không hoạt động**

```python
# Thử thay đổi số camera
cap = cv2.VideoCapture(1)  # hoặc 2, 3
```

**Serial không kết nối**

```python
# Thay đổi COM port
UART_PORT = 'COM8'  # COM3, COM4, ...
```

**Nhận diện tay không chính xác**

- Tăng ánh sáng
- Đặt tay gần camera
- Điều chỉnh `detectionCon=0.7` trong hand.py

**Xe không chạy**

- Kiểm tra nguồn/pin
- Kiểm tra kết nối motor driver
- Test bằng Manual Mode (Mode 2 trên Arduino)

---

## Port Configuration

**Mặc định:**

- Arduino: COM8 (keyboard_control.py)
- Arduino: COM8 (transfer_UART.py)
- Web server: Port 8080
- Baud rate: 9600

**Thay đổi port:**

```python
# keyboard_control.py
COM_PORT = 'COM8'

# UART/transfer_UART.py
UART_PORT = 'COM8'

# Web/web_control.py
COM_PORT = 'COM8'
SERVER_PORT = 8080
```

---

## Test nhanh

**Test local (không cần internet):**

```bash
# 1. Test camera (không cần Arduino)
.venv/Scripts/python.exe run.py → [1]

# 2. Test keyboard GUI (không cần Arduino)
.venv/Scripts/python.exe Keyboard/keyboard_control.py --test

# 3. Test web server LAN (không cần Arduino)
.venv/Scripts/python.exe Web/web_control.py --test    

# 4. Test với Arduino (local)
Upload SmartCar.ino → Chọn mode → .venv/Scripts/python.exe run.py
```

**Test AWS Cloud (cần internet):**

```bash
# 1. Test Bridge Client log (không cần Arduino)
.venv/Scripts/python.exe run.py → [6] → [1]
# Mở browser: https://voicecar.pngha.io.vn/ và điều khiển
# Xem log hiển thị ở terminal

# 2. Test điều khiển xe thật qua internet (cần Arduino)
# Bước 1: Upload SmartCar.ino → Mode [3]
# Bước 2: Chạy Bridge Client
.venv/Scripts/python.exe run.py → [6] → [2]
# Bước 3: Mở browser bất kỳ đâu: https://voicecar.pngha.io.vn/
# Bước 4: Điều khiển bằng voice/button/keyboard

# 3. Test AWS server local (dev only)
python Web/aws_web_voice_control.py --test
```

**Quick test flow (recommended):**

```
1. run.py → [6] → [1]  (Test Bridge log)
2. Mở https://voicecar.pngha.io.vn/
3. Nhấn nút W/A/S/D/X
4. Xem log hiển thị thay đổi lệnh
```

---

## AWS Deployment

**Server đã deploy tại:**

- URL: <https://voicecar.pngha.io.vn/>
- Region: AWS EC2 Singapore (ap-southeast-1)
- Service: systemd auto-restart

**Để deploy lại:**

```bash
cd Web
./deploy_ec2.sh          # Deploy to EC2
./setup_systemd.sh       # Setup systemd service
```

Chi tiết xem [Web/README_AWS.md](Web/README_AWS.md)

---

## Dependencies

**Main (requirements.txt):**

```
opencv-python==4.10.0.84
mediapipe==0.10.14
pyserial==3.5
```

**AWS (Web/requirements_aws.txt):**

```
boto3
pyserial
requests
```

**Cài đặt:**

```bash
pip install -r requirements.txt
pip install -r Web/requirements_aws.txt
```
