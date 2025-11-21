# -*- coding: utf-8 -*-
"""
aws_web_control.py - SmartCar AWS-Enhanced Web Control Server
NGÀY: 24/02/2026
Tích hợp Amazon Nova Sonic 2 cho điều khiển bằng ngôn ngữ tự nhiên
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import serial
import time
import threading
import json
import socket
import os
import sys

# AWS Bedrock imports
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("WARNING: boto3 not installed. LLM features will be disabled.")
    print("Install with: pip install boto3")

COM_PORT = '/dev/ttyUSB0'  # Linux/EC2 default (was COM8 for Windows)
BAUD_RATE = 9600
SERVER_PORT = 8080

# AWS Configuration
AWS_REGION = 'ap-southeast-1'  # Using your configured region
MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'  # Claude 3 Haiku

# EC2 Instance Role will be used automatically if available
# No need for explicit credentials if using IAM role

def auto_detect_port():
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        return None
    
    usb_ports = [p for p in ports if 'Bluetooth' not in p.description]
    if usb_ports:
        return usb_ports[0].device
    return ports[0].device if ports else None

class AWSBedrockLLM:
    """AWS Bedrock client for Amazon Nova Sonic 2"""
    def __init__(self, region=AWS_REGION, model_id=MODEL_ID):
        self.region = region
        self.model_id = model_id
        self.client = None
        self.available = False
        
        if AWS_AVAILABLE:
            try:
                self.client = boto3.client('bedrock-runtime', region_name=region)
                self.available = True
                print(f"✓ AWS Bedrock initialized: {model_id} in {region}")
            except Exception as e:
                print(f"✗ AWS Bedrock initialization failed: {e}")
                print("  LLM features will be disabled")
        else:
            print("✗ boto3 not available. LLM features disabled")
    
    def parse_command(self, user_input):
        """Parse natural language input to car command"""
        if not self.available:
            return {
                'success': False,
                'error': 'LLM not available',
                'command': None
            }
        
        system_prompt = """You are a SmartCar command parser. Convert natural language to car commands.

Available commands:
- W: Move forward (tiến, đi thẳng, forward, go ahead)
- S: Move backward (lùi, đi lùi, backward, reverse)
- A: Turn left (rẽ trái, queo trái, left, turn left)
- D: Turn right (rẽ phải, queo phải, right, turn right)
- X: Stop (dừng, stop, halt)

Respond ONLY with a JSON object in this exact format:
{"command": "W", "explanation": "Moving forward"}

Examples:
User: "đi thẳng" -> {"command": "W", "explanation": "Moving forward"}
User: "turn left" -> {"command": "A", "explanation": "Turning left"}
User: "dừng lại" -> {"command": "X", "explanation": "Stopping"}
"""
        
        try:
            request_body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": f"{system_prompt}\n\nUser input: {user_input}"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 100,
                    "temperature": 0.1,
                    "topP": 0.9
                }
            }
            
            response = self.client.converse(
                modelId=self.model_id,
                messages=request_body["messages"],
                inferenceConfig=request_body["inferenceConfig"]
            )
            
            # Extract response text
            response_text = response['output']['message']['content'][0]['text']
            
            # Parse JSON response
            result = json.loads(response_text)
            
            # Validate command
            if result.get('command') in ['W', 'A', 'S', 'D', 'X']:
                return {
                    'success': True,
                    'command': result['command'],
                    'explanation': result.get('explanation', ''),
                    'raw_input': user_input
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid command from LLM',
                    'command': None
                }
                
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse LLM response: {e}',
                'command': None
            }
        except ClientError as e:
            return {
                'success': False,
                'error': f'AWS Bedrock error: {e}',
                'command': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {e}',
                'command': None
            }

class SmartCarController:
    def __init__(self, test_mode=False, enable_llm=True):
        self.test_mode = test_mode
        self.ser = None
        self.current_command = 'X'
        self.command_count = 0
        self.llm_command_count = 0
        self.is_running = False
        self.command_history = []
        
        # Initialize LLM
        self.llm = AWSBedrockLLM() if enable_llm else None
        
        if not test_mode:
            self.connect_arduino()
        else:
            self.is_running = True
            print("TEST MODE - Không cần Arduino")
        
        self.send_thread = threading.Thread(target=self.continuous_send, daemon=True)
        self.send_thread.start()
    
    def connect_arduino(self):
        try:
            port = COM_PORT if COM_PORT else auto_detect_port()
            if not port:
                print("Không tìm thấy COM port")
                print("Chạy ở chế độ TEST MODE")
                self.test_mode = True
                self.is_running = True
                return
            
            print(f"Đang kết nối {port}...")
            self.ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)
            
            self.ser.write(b'3')
            time.sleep(1)
            
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            self.is_running = True
            print(f"✓ Đã kết nối {port}")
        except Exception as e:
            print(f"✗ Lỗi kết nối: {e}")
            print("Chạy ở chế độ TEST MODE")
            self.test_mode = True
            self.is_running = True
    
    def send_command(self, command, source='manual'):
        if command not in ['W', 'A', 'S', 'D', 'X']:
            return False
        
        self.current_command = command
        timestamp = time.strftime("%H:%M:%S")
        
        # Add to history
        self.command_history.append({
            'timestamp': timestamp,
            'command': command,
            'source': source
        })
        
        # Keep only last 50 commands
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]
        
        if source == 'llm':
            self.llm_command_count += 1
            print(f"[{timestamp}] LLM Command: {command}")
        else:
            print(f"[{timestamp}] Manual Command: {command}")
        
        return True
    
    def parse_natural_language(self, text):
        """Parse natural language using LLM"""
        if not self.llm or not self.llm.available:
            return {
                'success': False,
                'error': 'LLM not available. Please check AWS credentials and boto3 installation.',
                'command': None
            }
        
        return self.llm.parse_command(text)
    
    def continuous_send(self):
        while self.is_running:
            try:
                if self.test_mode:
                    self.command_count += 1
                elif self.ser and self.ser.is_open:
                    self.ser.write(self.current_command.encode())
                    self.command_count += 1
                time.sleep(0.05)
            except Exception as e:
                print(f"Lỗi gửi lệnh: {e}")
                break
    
    def get_status(self):
        return {
            'current_command': self.current_command,
            'command_count': self.command_count,
            'llm_command_count': self.llm_command_count,
            'is_running': self.is_running,
            'test_mode': self.test_mode,
            'llm_available': self.llm.available if self.llm else False,
            'history': self.command_history[-10:]  # Last 10 commands
        }
    
    def stop(self):
        self.is_running = False
        if self.ser and self.ser.is_open:
            self.ser.write(b'X')
            time.sleep(0.2)
            self.ser.close()

# Global controller instance
controller = None

class SmartCarRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_path = os.path.join(os.path.dirname(__file__), 'aws_web.html')
            with open(html_path, 'r', encoding='utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            status = controller.get_status()
            self.wfile.write(json.dumps(status).encode('utf-8'))
        
        elif self.path.startswith('/cmd/'):
            command = self.path.split('/')[-1].upper()
            if controller.send_command(command, source='manual'):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'success': True,
                    'command': command,
                    'message': f'Lệnh {command} đã được gửi'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'success': False,
                    'message': 'Lệnh không hợp lệ. Chỉ chấp nhận: W, A, S, D, X'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/llm/parse':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                user_input = data.get('text', '')
                
                if not user_input:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {'success': False, 'error': 'No text provided'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                # Parse with LLM
                result = controller.parse_natural_language(user_input)
                
                # If successful, send command
                if result['success']:
                    controller.send_command(result['command'], source='llm')
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {'success': False, 'error': 'Invalid JSON'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {args[0]} - {args[1]}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main(test_mode=False, enable_llm=True):
    global controller
    
    print("=" * 70)
    print("SMARTCAR AWS-ENHANCED WEB CONTROL SERVER")
    print("Amazon Nova Sonic 2 - Natural Language Control")
    print("=" * 70)
    
    controller = SmartCarController(test_mode=test_mode, enable_llm=enable_llm)
    
    local_ip = get_local_ip()
    server = HTTPServer(('0.0.0.0', SERVER_PORT), SmartCarRequestHandler)
    
    print(f"\n✓ Server đang chạy tại:")
    print(f"  - Local:  http://localhost:{SERVER_PORT}")
    print(f"  - LAN:    http://{local_ip}:{SERVER_PORT}")
    
    if controller.llm and controller.llm.available:
        print(f"\n✓ LLM Features: ENABLED")
        print(f"  - Model: {MODEL_ID}")
        print(f"  - Region: {AWS_REGION}")
    else:
        print(f"\n✗ LLM Features: DISABLED")
        print(f"  - Install boto3: pip install boto3")
        print(f"  - Configure AWS credentials: aws configure")
    
    print(f"\nĐiều khiển bằng curl:")
    print(f"  curl http://{local_ip}:{SERVER_PORT}/cmd/W")
    print(f"  curl -X POST http://{local_ip}:{SERVER_PORT}/llm/parse \\")
    print(f"       -H 'Content-Type: application/json' \\")
    print(f"       -d '{{\"text\": \"đi thẳng\"}}'")
    
    print(f"\nMở trình duyệt: http://{local_ip}:{SERVER_PORT}")
    print(f"\nNhấn Ctrl+C để dừng server")
    print("=" * 70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nĐang đóng server...")
        controller.stop()
        server.shutdown()
        print("Server đã đóng")

if __name__ == "__main__":
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    no_llm = '--no-llm' in sys.argv
    main(test_mode=test_mode, enable_llm=not no_llm)
