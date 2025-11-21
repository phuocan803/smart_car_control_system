# 🎥 Camera Web Streaming - Real-time (OpenCV)

## Mô tả

Server Flask stream camera **real-time không delay** bằng OpenCV qua LAN.

- ✅ **Không delay** - Stream trực tiếp từ camera buffer
- ✅ **Tương thích mọi camera** - USB Webcam, Pi Camera, laptop webcam
- ✅ **Đơn giản** - Chỉ cần OpenCV, không cần picamera2/fswebcam
- ✅ **FPS cao** - Lên tới 30 FPS (tùy camera)

**Không liên quan** đến các module điều khiển xe (keyboard_control, web_control).

## Yêu cầu phần cứng

- Raspberry Pi 4 / Pi 3 / PC / Laptop
- **Bất kỳ USB Webcam** hoặc Pi Camera Module
- Kết nối mạng LAN/WiFi

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/phuocan803/smart_car_control_system.git
cd smart_car_control_system/Camera
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements_pi.txt
```

Hoặc cài thủ công:

```bash
pip install flask opencv-python
```

**Trên Raspberry Pi Ubuntu:**

```bash
sudo apt update
sudo apt install -y python3-opencv python3-flask
```

### 3. Kiểm tra camera

```bash
# Liệt kê cameras
ls /dev/video*

# Test với Python
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera lỗi'); cap.release()"
```

**Nếu dùng Pi Camera trên Ubuntu:**

```bash
# Load kernel module
sudo modprobe bcm2835-v4l2
echo "bcm2835-v4l2" | sudo tee -a /etc/modules
```

## Chạy server

### Chế độ thường

```bash
python3 web_camera.py
```

Server sẽ hiển thị:

```
====================================================
CAMERA WEB STREAMING SERVER - REAL-TIME
====================================================

📹 Camera: USB_WEBCAM
📍 Camera Index: 0
📐 Độ phân giải: 640x480
🎞️  FPS: 30
🖼️  JPEG Quality: 80%

🌐 Địa chỉ truy cập:
  - Local:  http://localhost:5000
  - LAN:    http://192.168.1.100:5000

✨ Streaming real-time qua OpenCV (không delay)
💡 Tương thích với mọi loại camera (USB/Pi Camera)
```

### Chạy nền

```bash
nohup python3 web_camera.py > camera.log 2>&1 &
```

## Sử dụng

1. **Khởi động server** (Raspberry Pi hoặc PC)
2. **Mở browser** trên bất kỳ thiết bị nào trong LAN
3. **Truy cập**: `http://<IP>:5000`

Ví dụ: `http://192.168.1.100:5000`

## Cấu hình

Chỉnh sửa `web_camera.py`:

```python
CAMERA_INDEX = 0           # 0 = camera đầu tiên, 1 = thứ hai, ...
FRAME_WIDTH = 640          # Độ phân giải ngang
FRAME_HEIGHT = 480         # Độ phân giải dọc
JPEG_QUALITY = 80          # Chất lượng JPEG (0-100)
FPS = 30                   # FPS tối đa (camera tự điều chỉnh)
```

### Nhiều cameras

Nếu có nhiều camera, thay đổi `CAMERA_INDEX`:

```python
CAMERA_INDEX = 0  # Camera đầu tiên
CAMERA_INDEX = 1  # Camera thứ hai
CAMERA_INDEX = 2  # Camera thứ ba
```

## Tối ưu hiệu năng

### Giảm delay (mạng yếu/Pi cũ)

```python
CAMERA_INDEX = 0
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
JPEG_QUALITY = 60
FPS = 15
```

### Tăng chất lượng (mạng tốt)

```python
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
JPEG_QUALITY = 90
FPS = 30
```

### So sánh với phương pháp cũ

| Phương pháp | Delay | FPS | CPU Usage | Độ phức tạp |
|-------------|-------|-----|-----------|-------------|
| **OpenCV (mới)** | **~50ms** | **30** | **Thấp** | **Đơn giản** |
| fswebcam (cũ) | ~200ms | 5-10 | Trung bình | Phức tạp |
| picamera2 (cũ) | ~100ms | 10-15 | Thấp | Rất phức tạp |

**Ưu điểm OpenCV:**

- ✅ Stream trực tiếp từ buffer camera (không delay)
- ✅ Tương thích 100% với mọi loại camera
- ✅ Không cần cài fswebcam/picamera2
- ✅ Đơn giản, ổn định

## Troubleshooting

### Camera không mở được

```bash
# Kiểm tra camera
ls -l /dev/video*

# Test với Python
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened()); cap.release()"

# Thử camera index khác
# Sửa CAMERA_INDEX = 1 hoặc 2 trong web_camera.py
```

### Pi Camera không hoạt động (Ubuntu)

```bash
# Load kernel module
sudo modprobe bcm2835-v4l2

# Thêm vào auto-load
echo "bcm2835-v4l2" | sudo tee -a /etc/modules

# Kiểm tra
ls /dev/video*
```

### Không truy cập được từ máy khác

```bash
# Kiểm tra firewall
sudo ufw allow 5000/tcp

# Kiểm tra IP
hostname -I

# Ping test
ping <IP_CUA_PI>
```

### Streaming bị lag

- Giảm `FRAME_WIDTH` và `FRAME_HEIGHT`
- Giảm `JPEG_QUALITY` xuống 60-70
- Kiểm tra băng thông mạng

### Port 5000 đã được sử dụng

Sửa trong `web_camera.py`:

```python
app.run(host='0.0.0.0', port=8080, ...)  # Đổi sang port khác
```

## So sánh với module khác

| Module | Port | Chức năng | Camera |
|--------|------|-----------|--------|
| **Camera/web_camera.py** | **5000** | **Stream camera** | **Bắt buộc** |
| Web/web_control.py | 8080 | Điều khiển xe | Không cần |
| Keyboard/keyboard_control.py | - | Điều khiển xe | Không cần |
| UART/transfer_UART.py | - | OpenCV → Arduino | Bắt buộc |

Module camera **hoàn toàn độc lập**, chỉ dùng để xem camera qua web.
