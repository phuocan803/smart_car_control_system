# -*- coding: utf-8 -*-
"""
local_bridge_client.py - Bridge Client for AWS Web Control
DATE: 25/02/2026
Polls commands from EC2 server and forwards to local Arduino via Zigbee
"""
import serial
import time
import requests
import sys
import os

# Configuration
SERVER_URL = "https://voicecar.pngha.io.vn"
COM_PORT = 'COM8'  # Change this to your Arduino COM port
BAUD_RATE = 9600
POLL_INTERVAL = 0.1  # Poll every 100ms

def auto_detect_port():
    """Auto detect Arduino COM port"""
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        return None
    
    usb_ports = [p for p in ports if 'Bluetooth' not in p.description]
    if usb_ports:
        return usb_ports[0].device
    return ports[0].device if ports else None

class LocalBridgeClient:
    def __init__(self, server_url, com_port=None, baud_rate=BAUD_RATE, test_mode=False):
        self.server_url = server_url
        self.com_port = com_port or auto_detect_port()
        self.baud_rate = baud_rate
        self.test_mode = test_mode
        self.ser = None
        self.last_command = None
        self.is_running = False
        self.command_count = 0
        self.error_count = 0
        
        if not test_mode:
            self.connect_arduino()
        else:
            print("✓ TEST MODE - Không cần Arduino")
            self.is_running = True
    
    def connect_arduino(self):
        """Connect to Arduino via Serial/Zigbee"""
        try:
            if not self.com_port:
                print("✗ Không tìm thấy COM port")
                print("  Vui lòng chỉ định COM port thủ công")
                sys.exit(1)
            
            print(f"Đang kết nối {self.com_port}...")
            self.ser = serial.Serial(self.com_port, self.baud_rate, timeout=1)
            time.sleep(2)
            
            # Select Mode 3 (Keyboard/Web Control)
            self.ser.write(b'3')
            time.sleep(1)
            
            # Clear buffer
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            print(f"✓ Đã kết nối Arduino tại {self.com_port}")
            self.is_running = True
            
        except Exception as e:
            print(f"✗ Lỗi kết nối Arduino: {e}")
            print("  Kiểm tra:")
            print("  - Arduino đã được cắm vào USB")
            print("  - SmartCar.ino đã upload lên Arduino")
            print("  - COM port đúng")
            sys.exit(1)
    
    def get_server_status(self):
        """Get current command from server"""
        try:
            response = requests.get(
                f"{self.server_url}/status",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('current_command', 'X')
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            if self.error_count % 10 == 0:  # Only print every 10th error
                print(f"✗ Lỗi kết nối server: {e}")
            self.error_count += 1
            return None
    
    def send_to_arduino(self, command):
        """Send command to Arduino"""
        try:
            if self.test_mode:
                # In test mode, just count
                self.command_count += 1
                return True
            elif self.ser and self.ser.is_open:
                self.ser.write(command.encode())
                self.command_count += 1
                return True
        except Exception as e:
            print(f"✗ Lỗi gửi lệnh tới Arduino: {e}")
            return False
    
    def run(self):
        """Main polling loop"""
        print(f"\n✓ Bridge Client đã sẵn sàng")
        print(f"  Server: {self.server_url}")
        print(f"  Mode: {'TEST MODE' if self.test_mode else f'Arduino @ {self.com_port}'}")
        print(f"  Poll Interval: {POLL_INTERVAL}s")
        print(f"\nĐang lắng nghe lệnh từ server...")
        print(f"Nhấn Ctrl+C để dừng\n")
        
        try:
            while self.is_running:
                # Get command from server
                command = self.get_server_status()
                
                # If command changed, send to Arduino
                if command and command != self.last_command:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] Lệnh mới: {self.last_command} → {command} (#{self.command_count})")
                    
                    self.send_to_arduino(command)
                    self.last_command = command
                
                # Send current command continuously (like web_control.py)
                elif command:
                    self.send_to_arduino(command)
                
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\nĐang dừng Bridge Client...")
            self.stop()
    
    def stop(self):
        """Stop bridge and close connections"""
        self.is_running = False
        
        # Send stop command
        if not self.test_mode and self.ser and self.ser.is_open:
            print("Gửi lệnh STOP tới Arduino...")
            self.ser.write(b'X')
            time.sleep(0.2)
            self.ser.close()
        
        print(f"\n✓ Bridge Client đã dừng")
        print(f"  Tổng lệnh: {self.command_count}")
        print(f"  Lỗi: {self.error_count}")

def main():
    print("=" * 70)
    print("  SMARTCAR LOCAL BRIDGE CLIENT")
    print("  AWS EC2 Server ↔ Local Arduino (Zigbee)")
    print("=" * 70)
    print()
    
    # Check for test mode
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    
    if test_mode:
        print("✓ TEST MODE - Không cần Arduino\n")
        
        # Create and run bridge in test mode
        bridge = LocalBridgeClient(
            server_url=SERVER_URL,
            com_port=None,
            baud_rate=BAUD_RATE,
            test_mode=True
        )
        
        bridge.run()
        return
    
    # Check COM port
    com_port = COM_PORT
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        com_port = sys.argv[1]
        print(f"Sử dụng COM port: {com_port}")
    else:
        detected_port = auto_detect_port()
        if detected_port:
            print(f"Tự động phát hiện: {detected_port}")
            use_detected = input(f"Sử dụng {detected_port}? (y/n): ").strip().lower()
            if use_detected == 'y':
                com_port = detected_port
            else:
                com_port = input("Nhập COM port (vd: COM8): ").strip()
    
    print()
    
    # Create and run bridge
    bridge = LocalBridgeClient(
        server_url=SERVER_URL,
        com_port=com_port,
        baud_rate=BAUD_RATE
    )
    
    bridge.run()

if __name__ == "__main__":
    main()
