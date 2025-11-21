# -*- coding: utf-8 -*-
"""
web_camera.py - Camera Web Streaming Server (Real-time)
NGÀY: 21/11/2025

Stream camera trực tiếp qua web bằng OpenCV (không delay)
Chạy trên Raspberry Pi hoặc PC với bất kỳ webcam/Pi Camera nào
"""
from flask import Flask, Response, send_file, jsonify
import cv2
import socket
import os

app = Flask(__name__)

# Cấu hình camera
CAMERA_INDEX = 0  # 0 = camera đầu tiên, 1 = camera thứ hai, ...
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
JPEG_QUALITY = 80
FPS = 30  # FPS tối đa (camera sẽ tự điều chỉnh)

# Global video capture
camera = None

def init_camera():
    """Khởi tạo camera"""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(CAMERA_INDEX)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        camera.set(cv2.CAP_PROP_FPS, FPS)
        
        if not camera.isOpened():
            print(f"❌ Không thể mở camera {CAMERA_INDEX}")
            return False
        
        print(f"✅ Camera {CAMERA_INDEX} đã sẵn sàng")
        return True
    return True

def detect_camera_type():
    """Phát hiện loại camera (chỉ để hiển thị)"""
    # Thử detect Pi Camera
    if os.path.exists('/dev/video0'):
        try:
            with open('/sys/class/video4linux/video0/name', 'r') as f:
                name = f.read().strip()
                if 'bcm2835' in name.lower() or 'mmal' in name.lower():
                    return 'picamera'
        except:
            pass
        return 'usb_webcam'
    return 'unknown'


def get_local_ip():
    """Lấy địa chỉ IP LAN"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def generate_frames():
    """Generator để stream video frames (real-time, không delay)"""
    if not init_camera():
        print("❌ Không thể khởi tạo camera")
        return
    
    print("📹 Bắt đầu streaming...")
    
    while True:
        success, frame = camera.read()
        
        if not success:
            print("⚠️ Không đọc được frame")
            break
        
        # Encode frame thành JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        
        if not ret:
            continue
        
        # Convert to bytes
        frame_bytes = buffer.tobytes()
        
        # Yield frame theo MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Trang chính hiển thị video stream"""
    html_path = os.path.join(os.path.dirname(__file__), 'web.html')
    return send_file(html_path)

@app.route('/camera_info')
def camera_info():
    """API trả về thông tin camera"""
    actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH) if camera else FRAME_WIDTH
    actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT) if camera else FRAME_HEIGHT
    actual_fps = camera.get(cv2.CAP_PROP_FPS) if camera else FPS
    
    return jsonify({
        'width': int(actual_width),
        'height': int(actual_height),
        'fps': int(actual_fps),
        'quality': JPEG_QUALITY,
        'ip': get_local_ip(),
        'port': 5000,
        'camera_type': detect_camera_type(),
        'camera_index': CAMERA_INDEX
    })

@app.route('/video_feed')
def video_feed():
    """Route để stream video (MJPEG)"""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def main():
    """Khởi động server"""
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("CAMERA WEB STREAMING SERVER - REAL-TIME")
    print("=" * 60)
    
    # Test camera
    if init_camera():
        actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(camera.get(cv2.CAP_PROP_FPS))
        
        print(f"\n📹 Camera: {detect_camera_type().upper()}")
        print(f"📍 Camera Index: {CAMERA_INDEX}")
        print(f"📐 Độ phân giải: {actual_width}x{actual_height}")
        print(f"🎞️  FPS: {actual_fps}")
        print(f"🖼️  JPEG Quality: {JPEG_QUALITY}%")
    else:
        print("\n❌ CẢNH BÁO: Không tìm thấy camera!")
        print("Kiểm tra:")
        print("  - Webcam đã cắm chưa")
        print("  - Thử đổi CAMERA_INDEX = 1 hoặc 2")
        print("  - Pi Camera: sudo modprobe bcm2835-v4l2")
        return
    
    print(f"\n🌐 Địa chỉ truy cập:")
    print(f"  - Local:  http://localhost:5000")
    print(f"  - LAN:    http://{local_ip}:5000")
    print(f"\n✨ Streaming real-time qua OpenCV (không delay)")
    print(f"💡 Tương thích với mọi loại camera (USB/Pi Camera)")
    print("\nNhấn Ctrl+C để dừng server")
    print("=" * 60)
    print()
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    finally:
        if camera:
            camera.release()
            print("\n✅ Đã đóng camera")

if __name__ == "__main__":
    main()
