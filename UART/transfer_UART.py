# -*- coding: utf-8 -*-
"""
transfer_UART.py - OpenCV Hand Gesture to SmartCar UART Controller
NGÀY: 19/11/2025
"""
import cv2
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Hand'))
import hand as htm
import UART

COM_PORT = 'COM8'
UART_BAUD = 9600
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1280

gesture_to_command = {
    'X': 'X',
    'W': 'W',
    'S': 'S',
    'A': 'A',
    'D': 'D'
}

colors = {
    'X': (128, 128, 128),
    'W': (0, 255, 0),
    'S': (0, 0, 255),
    'A': (255, 0, 255),
    'D': (0, 255, 255)
}

def auto_detect_port():
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("Không tìm thấy cổng COM nào")
        return None
    
    print("Các cổng khả dụng:")
    for p in ports:
        print(f"  {p.device} - {p.description}")
    
    usb_ports = [p for p in ports if 'Bluetooth' not in p.description]
    
    if usb_ports:
        selected = usb_ports[0].device
        print(f"\nĐã chọn: {selected} (USB)")
        return selected
    else:
        selected = ports[0].device
        print(f"\nĐã chọn: {selected} (Bluetooth - có thể không ổn định)")
        return selected

def main():
    print("=" * 60)
    print("ĐIỀU KHIỂN XE BẰNG Cử CHỈ TAY QUA UART")
    print("=" * 60)
    print()
    
    if not UART_PORT:
        print("Đang tự động tìm cổng COM...")
        port = auto_detect_port()
        if not port:
            print("Không tìm thấy cổng COM. Vui lòng kết nối Arduino.")
            return
    else:
        port = UART_PORT
        print(f"Đang sử dụng cổng đã cấu hình: {port}")
    
    print(f"Tốc độ truyền: {UART_BAUD} baud")
    print()
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    
    if not cap.isOpened():
        print("Không mở được camera")
        return
    
    print("Camera đã mở thành công")
    
    detector = htm.handDetector(detectionCon=0.7, maxHands=2)
    
    with UART.UARTController(port=port, baud_rate=UART_BAUD) as uart:
        if not uart.is_connected:
            print("Kết nối UART thất bại. Thoát chương trình...")
            cap.release()
            return
        
        print("Đang chọn chế độ OpenCV trên Arduino...")
        uart.send_command('1')
        time.sleep(1)
        
        for _ in range(5):
            response = uart.read_response()
            if response:
                print(f"    Arduino: {response}")
            time.sleep(0.1)
        
        pTime = 0
        last_gesture = 'X'
        frame_count = 0
        
        print("\n===== Bắt đầu điều khiển =====")
        print("Nhấn 'q' để thoát\n")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Không đọc được frame")
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hands
                frame = detector.findHands(frame)
                
                # Analyze gesture
                gesture, description = detector.analyzeGesture(frame)
                
                if frame_count % 5 == 0 or gesture != last_gesture:
                    command = gesture_to_command.get(gesture, 'X')
                    if uart.send_command(command):
                        if gesture != last_gesture:
                            log_prefix = "DỮNG" if gesture == 'X' else f"  {gesture}   "
                            print(f"[{uart.command_count:4d}] {log_prefix} | {description}")
                            last_gesture = gesture
                
                response = uart.read_response()
                if response and ">>>" in response:
                    print(f"    {response}")
                
                color = colors.get(gesture, (255, 255, 255))
                
                cv2.rectangle(frame, (20, 20), (800, 220), color, -1)
                cv2.rectangle(frame, (20, 20), (800, 220), (0, 0, 0), 5)
                
                cv2.putText(frame, f"Cu chi: {gesture}", (40, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 5)
                
                stats = uart.get_stats()
                cv2.putText(frame, f"Lenh: '{stats['last_command']}' | Count: {stats['command_count']}", 
                           (40, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                
                cv2.putText(frame, description, (40, 190),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
                
                instructions = [
                    "X=Dung | W=Tien | S=Lui | A=Trai | D=Phai",
                    f"UART: {port} @ {UART_BAUD} baud",
                    "Nhan 'q' de thoat"
                ]
                
                y_offset = frame.shape[0] - 120
                for i, text in enumerate(instructions):
                    cv2.putText(frame, text, (20, y_offset + i*35),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                
                cTime = time.time()
                fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
                pTime = cTime
                cv2.putText(frame, f"FPS: {int(fps)}", (frame.shape[1] - 200, 40),
                           cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 255, 0), 3)
                
                cv2.imshow("Dieu khien xe bang cu chi tay", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except KeyboardInterrupt:
            print("\nNgat boi nguoi dung")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("\nDa dong camera")
            print("UART se tu dong ngat ket noi va gui lenh dung")
    
    print("Chuong trinh ket thuc an toan")


if __name__ == "__main__":
    main()
