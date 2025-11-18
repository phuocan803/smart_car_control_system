# SmartCar - Control System

Hệ thống điều khiển xe thông minh với 4 chế độ: OpenCV, Keyboard GUI, Web Control, Manual.

---

## Cấu trúc thư mục

```
Demo/
├── Hand/
│   ├── hand.py           - MediaPipe hand detection & gesture analysis
│   └── openCV.py         - Camera test with visualization
├── UART/
│   ├── UART.py           - Serial communication controller
│   └── transfer_UART.py  - OpenCV to Arduino bridge
├── Car/
│   └── SmartCar.ino      - Arduino firmware (3 modes)
├── Web/
│   └── web_control.py    - HTTP server for LAN control
├── keyboard_control.py   - GUI keyboard control (Tkinter)
└── run.py                - Main launcher
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

## 4 Chế độ điều khiển

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

| Tính năng | Test Camera | OpenCV | Keyboard GUI | Web Control |
|-----------|-------------|--------|--------------|-------------|
| Cần Arduino | Không | Có | Có | Có |
| Cần Camera | Có | Có | Không | Không |
| Interface | OpenCV Window | OpenCV Window | Tkinter GUI | Browser |
| Test Mode | N/A | Không | Có | Có |
| Multi-user | Không | Không | Không | Có |
| Use case | Test | Demo AI | Development | Remote Control |

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

```bash
# 1. Test camera (không cần Arduino)
.venv/Scripts/python.exe run.py → [1]

# 2. Test keyboard GUI (không cần Arduino)
.venv/Scripts/python.exe /Keyboard/keyboard_control.py --test

# 3. Test web server (không cần Arduino)
.venv/Scripts/python.exe Web/web_control.py --test    

# 4. Test với Arduino
Upload SmartCar.ino → Chọn mode → .venv/Scripts/python.exe run.py
```
