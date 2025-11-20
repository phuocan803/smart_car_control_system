# -*- coding: utf-8 -*-
"""
web_camera.py - Raspberry Pi Camera Web Streaming Server
NGÀY: 20/11/2025

Chạy trên Raspberry Pi 4 Ubuntu để stream camera qua LAN
Không liên quan đến các module điều khiển xe
Hỗ trợ cả picamera2 (Pi Camera) và fswebcam (USB Webcam)
"""
from flask import Flask, Response, send_file, jsonify
import subprocess
import socket
import os
import time
from io import BytesIO

app = Flask(__name__)

# Cấu hình camera
CAMERA_TYPE = 'auto'  # 'auto', 'picamera2', hoặc 'fswebcam'
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
JPEG_QUALITY = 80
FPS = 10  # Giới hạn FPS để giảm CPU usage

def detect_camera_type():
    """Tự động phát hiện loại camera"""
    try:
        # Kiểm tra picamera2
        from picamera2 import Picamera2
        try:
            picam2 = Picamera2()
            picam2.close()
            print("Phát hiện: Pi Camera Module (picamera2)")
            return 'picamera2'
        except:
            pass
    except ImportError:
        pass
    
    # Kiểm tra USB camera
    result = subprocess.run(['ls', '/dev/video0'], capture_output=True)
    if result.returncode == 0:
        print("Phát hiện: USB Webcam")
        return 'fswebcam'
    
    print("Không tìm thấy camera nào!")
    return None

def get_local_ip():
    """Lấy địa chỉ IP LAN của Raspberry Pi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def generate_frames():
    """Generator để stream video frames"""
    # Auto-detect camera nếu cần
    camera_type = CAMERA_TYPE
    if camera_type == 'auto':
        camera_type = detect_camera_type()
        if not camera_type:
            print("Lỗi: Không tìm thấy camera")
            return
    
    if camera_type == 'picamera2':
        # Sử dụng picamera2 cho Pi Camera Module
        try:
            from picamera2 import Picamera2
            
            picam2 = Picamera2()
            config = picam2.create_video_configuration(
                main={"size": (FRAME_WIDTH, FRAME_HEIGHT)}
            )
            picam2.configure(config)
            picam2.start()
            
            print(f"Pi Camera đã khởi động: {FRAME_WIDTH}x{FRAME_HEIGHT} @ {FPS}fps")
            
            try:
                while True:
                    # Capture frame as JPEG
                    frame_bytes = picam2.capture_file(BytesIO(), format='jpeg')
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes.getvalue() + b'\r\n')
                    
                    time.sleep(1.0 / FPS)
            
            finally:
                picam2.stop()
                picam2.close()
                print("Đã đóng Pi Camera")
        
        except ImportError:
            print("Lỗi: picamera2 chưa cài đặt")
            print("Ubuntu: sudo apt install -y python3-picamera2")
            print("Hoặc đổi CAMERA_TYPE = 'fswebcam' trong code")
            return
        
        except Exception as e:
            print(f"Lỗi Pi Camera: {e}")
            print("Thử: sudo modprobe bcm2835-v4l2")
            print("Hoặc đổi sang USB Webcam")
            return
    
    else:
        # Sử dụng fswebcam cho USB camera
        print(f"Sử dụng fswebcam: {FRAME_WIDTH}x{FRAME_HEIGHT} @ {FPS}fps")
        
        # Kiểm tra fswebcam có sẵn không
        result = subprocess.run(['which', 'fswebcam'], capture_output=True)
        if result.returncode != 0:
            print("Lỗi: fswebcam chưa cài đặt")
            print("Cài đặt: sudo apt install -y fswebcam")
            return
        
        while True:
            try:
                # Capture từ USB camera bằng fswebcam
                cmd = [
                    'fswebcam',
                    '-r', f'{FRAME_WIDTH}x{FRAME_HEIGHT}',
                    '--jpeg', str(JPEG_QUALITY),
                    '--no-banner',
                    '-'
                ]
                
                result = subprocess.run(cmd, capture_output=True)
                
                if result.returncode == 0:
                    frame_bytes = result.stdout
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    print(f"Lỗi fswebcam: {result.stderr.decode()}")
                
                time.sleep(1.0 / FPS)
            
            except Exception as e:
                print(f"Lỗi capture: {e}")
                time.sleep(1)

@app.route('/')
def index():
    """Trang chính hiển thị video stream"""
    html_path = os.path.join(os.path.dirname(__file__), 'web.html')
    return send_file(html_path)

@app.route('/camera_info')
def camera_info():
    """API trả về thông tin camera"""
    camera_type = CAMERA_TYPE
    if camera_type == 'auto':
        camera_type = detect_camera_type() or 'unknown'
    
    return jsonify({
        'width': FRAME_WIDTH,
        'height': FRAME_HEIGHT,
        'fps': FPS,
        'quality': JPEG_QUALITY,
        'ip': get_local_ip(),
        'port': 5000,
        'camera_type': camera_type
    })

@app.route('/video_feed')
def video_feed():
    """Route để stream video"""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def main():
    """Khởi động server"""
    local_ip = get_local_ip()
    
    # Auto-detect camera nếu cần
    camera_type = CAMERA_TYPE
    if camera_type == 'auto':
        print("Đang tự động phát hiện camera...")
        camera_type = detect_camera_type()
        if not camera_type:
            print("\n CẢNH BÁO: Không tìm thấy camera nào!")
            print("Kiểm tra:")
            print("  - Pi Camera: sudo modprobe bcm2835-v4l2")
            print("  - USB Camera: ls /dev/video*")
            print("\nServer sẽ khởi động nhưng không có video stream")
        print()
    
    print("=" * 60)
    print("RASPBERRY PI CAMERA WEB STREAMING SERVER")
    print("=" * 60)
    print(f"\nCamera: {camera_type if camera_type else 'Không phát hiện'}")
    print(f"Địa chỉ truy cập:")
    print(f"  - Local:  http://localhost:5000")
    print(f"  - LAN:    http://{local_ip}:5000")
    print(f"\nCấu hình:")
    print(f"  - Độ phân giải: {FRAME_WIDTH}x{FRAME_HEIGHT}")
    print(f"  - FPS: {FPS}")
    print(f"  - JPEG Quality: {JPEG_QUALITY}%")
    print(f"\nĐộc lập hoàn toàn với các module điều khiển xe")
    print(f"Chỉ dùng để xem camera qua web browser")
    print("\nNhấn Ctrl+C để dừng server")
    print("=" * 60)
    print()
    
    app.run(
        host='0.0.0.0',  # Lắng nghe trên tất cả interfaces
        port=5000,
        debug=False,
        threaded=True
    )

if __name__ == "__main__":
    main()
