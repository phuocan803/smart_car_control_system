# -*- coding: utf-8 -*-
"""
cloud_bridge_client.py - Bridge Client linking Remote AWS Cloud Server with Local Serial Hardware
Polls command telemetry from AWS EC2 web gateway and forwards to local Arduino over serial link.
"""
import serial
import time
import requests
import sys
import os

# Configuration defaults
SERVER_URL = "https://voicecar.pngha.io.vn"
COM_PORT = 'COM8'
BAUD_RATE = 9600
POLL_INTERVAL = 0.1

def auto_detect_port():
    """Auto-detect connected USB serial COM ports."""
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
            print("SIMULATION MODE ACTIVE — Running without active Arduino hardware.")
            self.is_running = True
    
    def connect_arduino(self):
        """Connect to Arduino via USB Serial."""
        try:
            if not self.com_port:
                print("Error: Serial COM port not specified or detected.")
                sys.exit(1)
            
            print(f"Connecting to serial port {self.com_port}...")
            self.ser = serial.Serial(self.com_port, self.baud_rate, timeout=1)
            time.sleep(2)
            
            # Select Python Keyboard Mode on firmware
            self.ser.write(b'3')
            time.sleep(1)
            
            # Flush buffer
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            print(f"Arduino connected on port {self.com_port}.")
            self.is_running = True
            
        except Exception as e:
            print(f"Error: Connection to Arduino failed: {e}")
            print("Troubleshooting:")
            print("  - Verify USB cable connection")
            print("  - Ensure smart_car.ino firmware is uploaded")
            print("  - Confirm assigned COM port")
            sys.exit(1)
    
    def get_server_status(self):
        """Poll active command telemetry from remote cloud web server."""
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
            if self.error_count % 10 == 0:
                print(f"Warning: Cloud server connection error: {e}")
            self.error_count += 1
            return None
    
    def send_to_arduino(self, command):
        """Send command character code to Arduino over serial link."""
        try:
            if self.test_mode:
                self.command_count += 1
                return True
            elif self.ser and self.ser.is_open:
                self.ser.write(command.encode())
                self.command_count += 1
                return True
        except Exception as e:
            print(f"Error: Transmission to Arduino failed: {e}")
            return False
    
    def run(self):
        """Main polling loop."""
        print(f"\nCloud Bridge Client Initialized")
        print(f"  Target Cloud Server: {self.server_url}")
        print(f"  Execution Mode: {'SIMULATION MODE' if self.test_mode else f'Arduino @ {self.com_port}'}")
        print(f"  Polling Interval: {POLL_INTERVAL}s")
        print(f"\nMonitoring command events from cloud server...")
        print(f"Press Ctrl+C to terminate.\n")
        
        try:
            while self.is_running:
                command = self.get_server_status()
                
                if command and command != self.last_command:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] New Command Event: {self.last_command} -> {command} (Event #{self.command_count})")
                    
                    self.send_to_arduino(command)
                    self.last_command = command
                elif command:
                    self.send_to_arduino(command)
                
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nTerminating Cloud Bridge Client...")
            self.stop()
    
    def stop(self):
        """Stop bridge process and safely release serial resources."""
        self.is_running = False
        
        if not self.test_mode and self.ser and self.ser.is_open:
            print("Sending STOP command to Arduino...")
            self.ser.write(b'X')
            time.sleep(0.2)
            self.ser.close()
        
        print(f"\nCloud Bridge Client terminated cleanly.")
        print(f"  Total Commands Relayed: {self.command_count}")
        print(f"  Network Errors: {self.error_count}")

def main():
    print("=" * 70)
    print("  SMART CAR CLOUD BRIDGE CLIENT")
    print("  AWS Cloud Server ↔ Local Arduino Hardware Gateway")
    print("=" * 70)
    print()
    
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    
    if test_mode:
        print("SIMULATION MODE ACTIVE — Running without active Arduino hardware.\n")
        bridge = LocalBridgeClient(
            server_url=SERVER_URL,
            com_port=None,
            baud_rate=BAUD_RATE,
            test_mode=True
        )
        bridge.run()
        return
    
    com_port = COM_PORT
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        com_port = sys.argv[1]
        print(f"Using specified COM port: {com_port}")
    else:
        detected_port = auto_detect_port()
        if detected_port:
            print(f"Auto-detected serial port: {detected_port}")
            use_detected = input(f"Use {detected_port}? (y/n): ").strip().lower()
            if use_detected == 'y':
                com_port = detected_port
            else:
                com_port = input("Enter COM port (e.g., COM8 or /dev/ttyUSB0): ").strip()
    
    print()
    bridge = LocalBridgeClient(
        server_url=SERVER_URL,
        com_port=com_port,
        baud_rate=BAUD_RATE
    )
    bridge.run()

if __name__ == "__main__":
    main()
