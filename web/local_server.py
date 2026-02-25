# -*- coding: utf-8 -*-
"""
local_server.py - Smart Car Local LAN Web Control Server
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import serial
import time
import threading
import json
import socket
import os

COM_PORT = 'COM8'
BAUD_RATE = 9600
SERVER_PORT = 8080

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

class SmartCarController:
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        self.ser = None
        self.current_command = 'X'
        self.command_count = 0
        self.is_running = False
        
        if not test_mode:
            self.connect_arduino()
        else:
            self.is_running = True
            print("SIMULATION MODE ACTIVE — Running without active Arduino hardware.")
        
        self.send_thread = threading.Thread(target=self.continuous_send, daemon=True)
        self.send_thread.start()
    
    def connect_arduino(self):
        """Establish serial connection with Arduino microcontroller."""
        try:
            port = COM_PORT if COM_PORT else auto_detect_port()
            if not port:
                print("Warning: Serial COM port not found.")
                print("Defaulting to SIMULATION MODE...")
                self.test_mode = True
                self.is_running = True
                return
            
            print(f"Connecting to serial port {port}...")
            self.ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)
            
            self.ser.write(b'3')
            time.sleep(1)
            
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            self.is_running = True
            print(f"Connected to Arduino on port {port}.")
        except Exception as e:
            print(f"Serial connection error: {e}")
            print("Defaulting to SIMULATION MODE...")
            self.test_mode = True
            self.is_running = True
    
    def send_command(self, command):
        """Register active vehicle movement command code."""
        if command not in ['W', 'A', 'S', 'D', 'X']:
            return False
        
        self.current_command = command
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Command: {command}")
        return True
    
    def continuous_send(self):
        """Background thread sending serial command codes at 20Hz (50ms interval)."""
        while self.is_running:
            try:
                if self.test_mode:
                    self.command_count += 1
                elif self.ser and self.ser.is_open:
                    self.ser.write(self.current_command.encode())
                    self.command_count += 1
                time.sleep(0.05)
            except Exception as e:
                print(f"Serial transmission error: {e}")
                break
    
    def get_status(self):
        """Return vehicle connection and command telemetry dictionary."""
        return {
            'current_command': self.current_command,
            'command_count': self.command_count,
            'is_running': self.is_running,
            'test_mode': self.test_mode
        }
    
    def stop(self):
        """Close serial connection safely."""
        self.is_running = False
        if self.ser and self.ser.is_open:
            self.ser.write(b'X')
            time.sleep(0.2)
            self.ser.close()

controller = None

class SmartCarRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_path = os.path.join(os.path.dirname(__file__), 'local_dashboard.html')
            with open(html_path, 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = controller.get_status()
            self.wfile.write(json.dumps(status).encode('utf-8'))
        
        elif self.path.startswith('/cmd/'):
            command = self.path.split('/')[-1].upper()
            if controller.send_command(command):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'success': True,
                    'command': command,
                    'message': f'Command {command} dispatched.'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'success': False,
                    'message': 'Invalid command code. Expected: W, A, S, D, X'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {args[0]} - {args[1]}")

def get_local_ip():
    """Get local LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def main(test_mode=False):
    global controller
    
    print("=" * 60)
    print("SMART CAR LAN WEB CONTROL SERVER")
    print("=" * 60)
    
    controller = Smart CarController(test_mode=test_mode)
    local_ip = get_local_ip()
    server = HTTPServer(('0.0.0.0', SERVER_PORT), Smart CarRequestHandler)
    
    print(f"\nServer running at:")
    print(f"  - Local:  http://localhost:{SERVER_PORT}")
    print(f"  - LAN:    http://{local_ip}:{SERVER_PORT}")
    print(f"\nDirect REST API Control Examples:")
    print(f"  curl http://{local_ip}:{SERVER_PORT}/cmd/W  # Forward")
    print(f"  curl http://{local_ip}:{SERVER_PORT}/cmd/A  # Turn Left")
    print(f"  curl http://{local_ip}:{SERVER_PORT}/cmd/S  # Reverse")
    print(f"  curl http://{local_ip}:{SERVER_PORT}/cmd/D  # Turn Right")
    print(f"  curl http://{local_ip}:{SERVER_PORT}/cmd/X  # Stop")
    print(f"\nWeb Interface: http://{local_ip}:{SERVER_PORT}")
    print(f"\nPress Ctrl+C to terminate server.")
    print("=" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nTerminating web control server...")
        controller.stop()
        server.shutdown()
        print("Server stopped cleanly.")

if __name__ == "__main__":
    import sys
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    main(test_mode=test_mode)
