# -*- coding: utf-8 -*-
"""
camera_server.py - Camera Web Streaming Server (Real-time)
"""
from flask import Flask, Response, send_file, jsonify
import cv2
import socket
import os

app = Flask(__name__)

# Camera configuration
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
JPEG_QUALITY = 80
FPS = 30

# Global video capture instance
camera = None

def init_camera():
    """Initialize camera device."""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(CAMERA_INDEX)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        camera.set(cv2.CAP_PROP_FPS, FPS)
        
        if not camera.isOpened():
            print(f"Error: Unable to open camera index {CAMERA_INDEX}")
            return False
        
        print(f"Camera index {CAMERA_INDEX} initialized successfully.")
        return True
    return True

def detect_camera_type():
    """Detect camera hardware driver type."""
    if os.path.exists('/dev/video0'):
        try:
            with open('/sys/class/video4linux/video0/name', 'r') as f:
                name = f.read().strip()
                if 'bcm2835' in name.lower() or 'mmal' in name.lower():
                    return 'picamera'
        except Exception:
            pass
        return 'usb_webcam'
    return 'unknown'

def get_local_ip():
    """Retrieve local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def generate_frames():
    """Generator streaming video frames in MJPEG format."""
    if not init_camera():
        print("Error: Camera initialization failed.")
        return
    
    print("Starting camera video stream...")
    
    while True:
        success, frame = camera.read()
        
        if not success:
            print("Warning: Failed to capture frame.")
            break
        
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Main route displaying video stream dashboard UI."""
    html_path = os.path.join(os.path.dirname(__file__), 'camera_view.html')
    return send_file(html_path)

@app.route('/camera_info')
def camera_info():
    """API endpoint returning camera configuration JSON."""
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
    """Route streaming real-time video feed (MJPEG)."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def main():
    """Start camera streaming server."""
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("CAMERA WEB STREAMING SERVER - REAL-TIME")
    print("=" * 60)
    
    if init_camera():
        actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(camera.get(cv2.CAP_PROP_FPS))
        
        print(f"\nCamera Driver: {detect_camera_type().upper()}")
        print(f"Camera Index: {CAMERA_INDEX}")
        print(f"Resolution: {actual_width}x{actual_height}")
        print(f"FPS: {actual_fps}")
        print(f"JPEG Quality: {JPEG_QUALITY}%")
    else:
        print("\nWARNING: Camera hardware not detected!")
        print("Troubleshooting steps:")
        print("  - Verify USB camera connection")
        print("  - Try setting CAMERA_INDEX = 1 or 2")
        print("  - On Raspberry Pi: sudo modprobe bcm2835-v4l2")
        return
    
    print(f"\nAccess URLs:")
    print(f"  - Local:  http://localhost:5000")
    print(f"  - LAN:    http://{local_ip}:5000")
    print(f"\nPress Ctrl+C to terminate server.")
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
            print("\nCamera device released.")

if __name__ == "__main__":
    main()
