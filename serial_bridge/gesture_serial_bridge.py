# -*- coding: utf-8 -*-
"""
gesture_serial_bridge.py - OpenCV Hand Gesture to Smart Car UART Controller Bridge
"""
import cv2
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'vision'))
import hand_tracker as htm
import serial_interface as UART

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
    """Auto-detect connected USB serial COM ports."""
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No COM ports detected.")
        return None
    
    print("Available serial ports:")
    for p in ports:
        print(f"  {p.device} - {p.description}")
    
    usb_ports = [p for p in ports if 'Bluetooth' not in p.description]
    
    if usb_ports:
        selected = usb_ports[0].device
        print(f"\nSelected USB port: {selected}")
        return selected
    else:
        selected = ports[0].device
        print(f"\nSelected fallback port: {selected}")
        return selected

def main():
    print("=" * 60)
    print("SMART CAR GESTURE CONTROL SERIAL BRIDGE")
    print("=" * 60)
    print()
    
    if not COM_PORT:
        print("Auto-detecting serial COM port...")
        port = auto_detect_port()
        if not port:
            print("Error: No valid serial COM port found. Connect Arduino and retry.")
            return
    else:
        port = COM_PORT
        print(f"Using configured serial port: {port}")
    
    print(f"Baud rate: {UART_BAUD} baud")
    print()
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    
    if not cap.isOpened():
        print("Error: Unable to open camera device.")
        return
    
    print("Camera initialized successfully.")
    detector = htm.handDetector(detectionCon=0.7, maxHands=2)
    
    with UART.UARTController(port=port, baud_rate=UART_BAUD) as uart:
        if not uart.is_connected:
            print("UART serial connection failed. Exiting...")
            cap.release()
            return
        
        print("Selecting OpenCV control mode on Arduino firmware...")
        uart.send_command('1')
        time.sleep(1)
        
        pTime = 0
        last_gesture = 'X'
        frame_count = 0
        
        print("\n===== Starting Real-Time Gesture Steering =====")
        print("Press 'q' to exit.\n")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Unable to capture video frame.")
                    break
                
                frame = cv2.flip(frame, 1)
                frame = detector.findHands(frame)
                gesture, description = detector.detectGesture(frame)
                
                if frame_count % 5 == 0 or gesture != last_gesture:
                    command = gesture_to_command.get(gesture, 'X')
                    if uart.send_command(command):
                        if gesture != last_gesture:
                            log_prefix = "STOP" if gesture == 'X' else f" {gesture} "
                            print(f"[{uart.command_count:4d}] {log_prefix} | {description}")
                            last_gesture = gesture
                
                color = colors.get(gesture, (255, 255, 255))
                
                cv2.rectangle(frame, (20, 20), (800, 220), color, -1)
                cv2.rectangle(frame, (20, 20), (800, 220), (255, 255, 255), 5)
                
                cv2.putText(frame, f"Gesture: {gesture}", (40, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 5)
                
                cv2.putText(frame, f"Command: '{uart.last_command}' | Count: {uart.command_count}", 
                           (40, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
                
                cv2.putText(frame, description, (40, 190),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)
                
                instructions = [
                    "X=Stop | W=Forward | S=Reverse | A=Left | D=Right",
                    f"UART Port: {port} @ {UART_BAUD} baud",
                    "Press 'q' to quit"
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
                
                cv2.imshow("Smart Car Hand Gesture Steering", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except KeyboardInterrupt:
            print("\nTerminated by user.")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("\nCamera released.")
            print("UART serial connection closed.")
    
    print("Program exited cleanly.")

if __name__ == "__main__":
    main()
