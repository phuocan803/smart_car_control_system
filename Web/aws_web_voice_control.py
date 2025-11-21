# -*- coding: utf-8 -*-
"""
aws_web_voice_control.py - SmartCar AWS Voice Control Server
DATE: 24/02/2026
Voice input/output with Amazon Polly and Web Speech API
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import serial
import time
import threading
import json
import socket
import os
import sys
import base64

# AWS Bedrock imports
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("WARNING: boto3 not installed. LLM and voice features will be disabled.")
    print("Install with: pip install boto3")

COM_PORT = '/dev/ttyUSB0'  # Linux/EC2 default
BAUD_RATE = 9600
SERVER_PORT = 8080

# AWS Configuration
AWS_REGION = 'ap-southeast-1'
MODEL_ID = 'amazon.nova-2-sonic-v1:0'  # Nova 2 Sonic - Speech-to-Speech
TEXT_MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'  # Fallback for text
NOVA_VOICE_ID = 'en-US-Female-1'  # Nova 2 Sonic voice

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
    """AWS Bedrock client for Nova 2 Sonic (Speech-to-Speech)"""
    def __init__(self, region=AWS_REGION, model_id=MODEL_ID):
        self.region = region
        self.model_id = model_id
        self.text_model_id = TEXT_MODEL_ID
        self.client = None
        self.available = False
        
        if AWS_AVAILABLE:
            try:
                self.client = boto3.client('bedrock-runtime', region_name=region)
                self.available = True
                print(f"✓ AWS Bedrock initialized: {model_id} in {region}")
                print(f"✓ Nova 2 Sonic: Speech-to-Speech conversational AI")
            except Exception as e:
                print(f"✗ AWS initialization failed: {e}")
                print("  Voice features will be disabled")
        else:
            print("✗ boto3 not available. Voice features disabled")
    
    def parse_command(self, user_input):
        """Parse natural language input to car command using keyword matching (LLM fallback)"""
        # Keyword-based parsing (works without AWS Bedrock)
        text = user_input.lower().strip()
        
        # Forward commands
        if any(word in text for word in ['forward', 'ahead', 'go', 'move forward', 'straight']):
            return {
                'success': True,
                'command': 'W',
                'explanation': 'Moving forward',
                'raw_input': user_input,
                'method': 'keyword'
            }
        
        # Backward commands
        if any(word in text for word in ['back', 'backward', 'reverse']):
            return {
                'success': True,
                'command': 'S',
                'explanation': 'Moving backward',
                'raw_input': user_input,
                'method': 'keyword'
            }
        
        # Left commands
        if any(word in text for word in ['left', 'turn left']):
            return {
                'success': True,
                'command': 'A',
                'explanation': 'Turning left',
                'raw_input': user_input,
                'method': 'keyword'
            }
        
        # Right commands
        if any(word in text for word in ['right', 'turn right']):
            return {
                'success': True,
                'command': 'D',
                'explanation': 'Turning right',
                'raw_input': user_input,
                'method': 'keyword'
            }
        
        # Stop commands
        if any(word in text for word in ['stop', 'halt', 'brake', 'wait']):
            return {
                'success': True,
                'command': 'X',
                'explanation': 'Stopping',
                'raw_input': user_input,
                'method': 'keyword'
            }
        
        # If LLM is available, try using it
        if self.available:
            try:
                system_prompt = """You are a SmartCar command parser. Convert natural language to car commands.

Available commands:
- W: Move forward (go forward, move ahead, drive forward)
- S: Move backward (go back, reverse, move backward)
- A: Turn left (turn left, go left, left turn)
- D: Turn right (turn right, go right, right turn)
- X: Stop (stop, halt, brake)

Respond ONLY with a JSON object in this exact format:
{"command": "W", "explanation": "Moving forward"}

Examples:
User: "go forward" -> {"command": "W", "explanation": "Moving forward"}
User: "turn left" -> {"command": "A", "explanation": "Turning left"}
User: "stop" -> {"command": "X", "explanation": "Stopping"}
"""
                
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
                    modelId=self.text_model_id,
                    messages=request_body["messages"],
                    inferenceConfig=request_body["inferenceConfig"]
                )
                
                response_text = response['output']['message']['content'][0]['text']
                result = json.loads(response_text)
                
                if result.get('command') in ['W', 'A', 'S', 'D', 'X']:
                    result['method'] = 'llm'
                    result['raw_input'] = user_input
                    return result
                    
            except Exception as e:
                print(f"LLM parsing failed, using keyword match: {e}")
        
        # No match found
        return {
            'success': False,
            'error': 'Could not understand command. Try: forward, back, left, right, stop',
            'command': None,
            'method': 'none'
        }
    
    def text_to_speech(self, text):
        """Convert text to speech - returns text for browser TTS"""
        # Since AWS Bedrock models are not available for channel partner accounts,
        # we return the text and let the browser handle TTS with Web Speech API
        return {
            'success': True,
            'text': text,
            'method': 'browser_tts',
            'message': 'Using browser text-to-speech'
        }

class SmartCarController:
    def __init__(self, test_mode=False, enable_llm=True):
        self.test_mode = test_mode
        self.ser = None
        self.current_command = 'X'
        self.command_count = 0
        self.llm_command_count = 0
        self.voice_command_count = 0
        self.is_running = False
        self.command_history = []
        
        # Initialize LLM
        self.llm = AWSBedrockLLM() if enable_llm else None
        
        if not test_mode:
            self.connect_arduino()
        else:
            self.is_running = True
            print("TEST MODE - No Arduino needed")
        
        self.send_thread = threading.Thread(target=self.continuous_send, daemon=True)
        self.send_thread.start()
    
    def connect_arduino(self):
        try:
            port = COM_PORT if COM_PORT else auto_detect_port()
            if not port:
                print("No COM port found")
                print("Running in TEST MODE")
                self.test_mode = True
                self.is_running = True
                return
            
            print(f"Connecting to {port}...")
            self.ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)
            
            self.ser.write(b'3')
            time.sleep(1)
            
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            self.is_running = True
            print(f"✓ Connected to {port}")
        except Exception as e:
            print(f"✗ Connection error: {e}")
            print("Running in TEST MODE")
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
        
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]
        
        if source == 'llm':
            self.llm_command_count += 1
            print(f"[{timestamp}] LLM Command: {command}")
        elif source == 'voice':
            self.voice_command_count += 1
            print(f"[{timestamp}] Voice Command: {command}")
        else:
            print(f"[{timestamp}] Manual Command: {command}")
        
        return True
    
    def parse_natural_language(self, text):
        """Parse natural language using LLM"""
        if not self.llm or not self.llm.available:
            return {
                'success': False,
                'error': 'LLM not available',
                'command': None
            }
        
        return self.llm.parse_command(text)
    
    def text_to_speech(self, text):
        """Convert text to speech"""
        if not self.llm or not self.llm.available:
            return {
                'success': False,
                'error': 'Polly not available'
            }
        
        return self.llm.text_to_speech(text)
    
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
                print(f"Send error: {e}")
                break
    
    def get_status(self):
        return {
            'current_command': self.current_command,
            'command_count': self.command_count,
            'llm_command_count': self.llm_command_count,
            'voice_command_count': self.voice_command_count,
            'is_running': self.is_running,
            'test_mode': self.test_mode,
            'llm_available': self.llm.available if self.llm else False,
            'nova_sonic_available': self.llm.available if self.llm else False,
            'history': self.command_history[-10:]
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
            
            html_path = os.path.join(os.path.dirname(__file__), 'aws_web_voice.html')
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
                    'message': f'Command {command} sent'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    'success': False,
                    'message': 'Invalid command. Only W, A, S, D, X accepted'
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
                source = data.get('source', 'llm')  # 'llm' or 'voice'
                
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
                    controller.send_command(result['command'], source=source)
                
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
        
        elif self.path == '/tts':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                text = data.get('text', '')
                
                if not text:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {'success': False, 'error': 'No text provided'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                # Convert to speech
                result = controller.text_to_speech(text)
                
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
    print("SMARTCAR AWS VOICE CONTROL SERVER")
    print("Web Speech API - Voice Recognition with Keyword Matching")
    print("=" * 70)
    
    controller = SmartCarController(test_mode=test_mode, enable_llm=enable_llm)
    
    local_ip = get_local_ip()
    server = HTTPServer(('0.0.0.0', SERVER_PORT), SmartCarRequestHandler)
    
    print(f"\n✓ Server running at:")
    print(f"  - Local:  http://localhost:{SERVER_PORT}")
    print(f"  - LAN:    http://{local_ip}:{SERVER_PORT}")
    print(f"  - HTTPS:  https://voicecar.pngha.io.vn")
    
    print(f"\n✓ Voice Features: ENABLED")
    print(f"  - Voice Input: Web Speech API (browser-based)")
    print(f"  - Voice Output: Web Speech API (browser TTS)")
    print(f"  - Command Parsing: Keyword matching")
    print(f"  - Supported: forward, back, left, right, stop")
    
    if controller.llm and controller.llm.available:
        print(f"\n✓ AWS Bedrock: AVAILABLE (but not required)")
        print(f"  - Text Model: {TEXT_MODEL_ID}")
        print(f"  - Region: {AWS_REGION}")
        print(f"  - Note: Using keyword matching due to model access restrictions")
    else:
        print(f"\n✓ Keyword Matching: ACTIVE")
        print(f"  - No AWS Bedrock required")
        print(f"  - Direct command recognition")
    
    print(f"\nOpen browser: https://voicecar.pngha.io.vn")
    print(f"Press Ctrl+C to stop server")
    print("=" * 70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        controller.stop()
        server.shutdown()
        print("Server closed")

if __name__ == "__main__":
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    no_llm = '--no-llm' in sys.argv
    main(test_mode=test_mode, enable_llm=not no_llm)
