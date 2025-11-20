# 🎥 Raspberry Pi Camera Web Streaming

## Mô tả

Server Flask độc lập chạy trên **Raspberry Pi 4 với Ubuntu** để stream camera qua LAN.

**Không liên quan** đến các module điều khiển xe (keyboard_control, web_control, transfer_UART).

## Yêu cầu phần cứng

- Raspberry Pi 4 (hoặc Pi 3/Zero) với **Ubuntu OS**
- **USB Webcam** (khuyến nghị) hoặc Pi Camera Module (CSI)
- Kết nối mạng LAN/WiFi

## Cài đặt trên Raspberry Pi Ubuntu

### 1. Clone repository

```bash
git clone https://github.com/phuocan803/smart_car_control_system.git
cd smart_car_control_system/Camera
```

### 2. Cài đặt dependencies

#### Cho USB Webcam (Khuyến nghị cho Ubuntu)

```bash
# Cài đặt fswebcam
sudo apt update
sudo apt install -y fswebcam

# Cài đặt Flask
pip3 install flask
```

#### Cho Pi Camera Module (CSI) - Nâng cao

```bash
# Ubuntu không hỗ trợ picamera2 tốt, cần dùng libcamera
sudo apt update
sudo apt install -y libcamera-apps libcamera-tools v4l-utils

# Cài đặt Flask
pip3 install flask

# Load kernel module cho Pi Camera
sudo modprobe bcm2835-v4l2
echo "bcm2835-v4l2" | sudo tee -a /etc/modules
```

**Lưu ý:** Ubuntu trên Raspberry Pi khó cấu hình Pi Camera Module. **Khuyến nghị dùng USB Webcam** để đơn giản hơn.

### 3. Kiểm tra camera

#### USB Webcam (Khuyến nghị)

```bash
# Kiểm tra camera được nhận diện
ls /dev/video*

# Test chụp ảnh
fswebcam -r 640x480 test.jpg

# Kiểm tra thông tin camera
v4l2-ctl --device=/dev/video0 --all
```

#### Pi Camera Module (Nâng cao)

```bash
# Kiểm tra camera CSI được nhận diện
ls /dev/video*

# Test với libcamera (nếu cài đặt)
libcamera-hello --list-cameras

# Hoặc test với v4l2
v4l2-ctl --list-devices
v4l2-ctl --device=/dev/video0 --all
```

## Chạy server

### Chế độ thường

```bash
python3 web_camera.py
```

### Chạy nền với nohup

```bash
nohup python3 web_camera.py > camera.log 2>&1 &
```

### Chạy với systemd (tự động khởi động)

Tạo file `/etc/systemd/system/camera-stream.service`:

```ini
[Unit]
Description=SmartCar Camera Streaming Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/smart_car_control_system/Camera
ExecStart=/home/pi/smart_car_control_system/Camera/venv/bin/python web_camera.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Kích hoạt:

```bash
sudo systemctl daemon-reload
sudo systemctl enable camera-stream.service
sudo systemctl start camera-stream.service
sudo systemctl status camera-stream.service
```

## Sử dụng

1. **Khởi động server** trên Raspberry Pi
2. **Tìm IP của Pi** (hiển thị khi server start hoặc dùng `hostname -I`)
3. **Mở browser** trên máy khác trong cùng mạng LAN
4. **Truy cập**: `http://<PI_IP>:5000`

Ví dụ: `http://192.168.1.100:5000`

## Cấu hình

Chỉnh sửa các tham số trong `web_camera.py`:

```python
CAMERA_TYPE = 'fswebcam'   # Khuyến nghị 'fswebcam' cho Ubuntu
FRAME_WIDTH = 640          # Độ phân giải ngang (px)
FRAME_HEIGHT = 480         # Độ phân giải dọc (px)
JPEG_QUALITY = 80          # Chất lượng ảnh (0-100)
FPS = 10                   # Frame per second (5-10 cho fswebcam)
```

**Lưu ý cho Ubuntu:**

- **Khuyến nghị dùng USB Webcam** với `fswebcam` (tương thích tốt nhất)
- Pi Camera Module (CSI) trên Ubuntu cần cấu hình phức tạp
- Giảm FPS xuống 5-10 khi dùng `fswebcam` để giảm CPU usage

## Tối ưu hiệu năng

### Giảm độ trễ (cho mạng yếu/Pi cũ)

```python
CAMERA_TYPE = 'fswebcam'
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
JPEG_QUALITY = 60
FPS = 5
```

### Tăng chất lượng (USB Webcam + mạng tốt)

```python
CAMERA_TYPE = 'fswebcam'
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
JPEG_QUALITY = 90
FPS = 10
```

### So sánh hiệu năng trên Ubuntu

| Loại camera | Tương thích Ubuntu | CPU Usage | Độ trễ | Khuyến nghị |
|-------------|-------------------|-----------|--------|-------------|
| Pi Camera + libcamera | ⚠️ Khó cấu hình | Thấp (~15%) | Thấp | Không khuyến nghị |
| USB Webcam + fswebcam | ✅ Tốt | Trung bình (~20%) | Trung bình | **Khuyến nghị** |

**Khuyến nghị cho Ubuntu:** Dùng **USB Webcam** với `fswebcam` để dễ cài đặt và ổn định.

## Troubleshooting

### Lỗi "picamera2 not found" trên Ubuntu

```bash
# Ubuntu không hỗ trợ picamera2 tốt
# Khuyến nghị: Đổi sang fswebcam với USB Webcam

# Hoặc cài đặt libcamera (cho Pi Camera)
sudo apt update
sudo apt install -y libcamera-apps libcamera-tools
```

### Pi Camera không hoạt động trên Ubuntu

```bash
# Ubuntu không có raspi-config, cần cấu hình thủ công

# Kiểm tra kernel module
lsmod | grep bcm2835

# Load module nếu chưa có
sudo modprobe bcm2835-v4l2

# Thêm vào /etc/modules để tự động load
echo "bcm2835-v4l2" | sudo tee -a /etc/modules

# Kiểm tra camera được nhận diện
ls /dev/video*
v4l2-ctl --list-devices

# Nếu vẫn không được -> Khuyến nghị dùng USB Webcam
```

### USB Webcam không mở được

```bash
# Kiểm tra camera được nhận diện
ls -l /dev/video*

# Kiểm tra quyền truy cập
sudo usermod -a -G video $USER

# Test với fswebcam
fswebcam -r 640x480 test.jpg

# Kiểm tra thông tin camera
v4l2-ctl --device=/dev/video0 --all

# Khởi động lại
sudo reboot
```

### Port 5000 đã được sử dụng

Đổi port trong `web_camera.py`:

```python
app.run(host='0.0.0.0', port=8080, ...)
```

### Streaming bị lag/giật

- Giảm `FRAME_WIDTH`, `FRAME_HEIGHT`
- Giảm `FPS` xuống 10-15
- Giảm `JPEG_QUALITY` xuống 50-70
- Kiểm tra băng thông mạng

### Không truy cập được từ máy khác

```bash
# Kiểm tra firewall
sudo ufw allow 5000/tcp

# Kiểm tra IP
hostname -I

# Ping từ máy khác
ping <PI_IP>
```
