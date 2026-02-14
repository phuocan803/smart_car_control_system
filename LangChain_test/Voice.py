# -*- coding: utf-8 -*-
"""
Voice.py - Voice Command Recognition for SmartCar using LangChain
NGÀY: 20/11/2025

Nhận diện giọng nói tiếng Việt để điều khiển xe
Sử dụng: speech_recognition + LangChain + OpenAI
"""
import speech_recognition as sr
import serial
import time
import sys
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# Cấu hình
COM_PORT = 'COM8'
BAUD_RATE = 9600
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Set trong environment variable

# Command mapping
COMMANDS = {
    'W': ['tiến', 'đi thẳng', 'đi tới', 'về phía trước', 'forward'],
    'S': ['lùi', 'đi lùi', 'quay lại', 'về sau', 'backward'],
    'A': ['trái', 'rẽ trái', 'queo trái', 'sang trái', 'left'],
    'D': ['phải', 'rẽ phải', 'queo phải', 'sang phải', 'right'],
    'X': ['dừng', 'stop', 'đứng lại', 'ngừng', 'thôi']
}

def auto_detect_port():
    """Tự động tìm COM port"""
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        return None
    
    usb_ports = [p for p in ports if 'Bluetooth' not in p.description]
    if usb_ports:
        return usb_ports[0].device
    return ports[0].device if ports else None

class VoiceController:
    def __init__(self, use_langchain=True):
        self.use_langchain = use_langchain
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.ser = None
        self.is_running = False
        self.current_command = 'X'
        self.command_count = 0
        
        # LangChain setup
        if use_langchain and OPENAI_API_KEY:
            self.setup_langchain()
        else:
            print("  Chế độ simple matching (không dùng LangChain)")
            self.llm = None
        
        # Calibrate microphone
        self.calibrate_microphone()
    
    def setup_langchain(self):
        """Thiết lập LangChain với OpenAI"""
        try:
            # Khởi tạo LLM
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                openai_api_key=OPENAI_API_KEY
            )
            
            # Prompt template
            template = """Bạn là trợ lý nhận diện lệnh điều khiển xe thông minh.

Các lệnh hợp lệ:
- W: tiến, đi thẳng, đi tới, về phía trước, forward
- S: lùi, đi lùi, quay lại, về sau, backward  
- A: trái, rẽ trái, queo trái, sang trái, left
- D: phải, rẽ phải, queo phải, sang phải, right
- X: dừng, stop, đứng lại, ngừng, thôi

Người dùng nói: "{user_input}"

Hãy trả về CHÍNH XÁC một trong các ký tự: W, S, A, D, X
Nếu không rõ ràng, trả về X (dừng).
Chỉ trả về MỘT ký tự, không giải thích.
"""
            
            self.prompt = PromptTemplate(
                input_variables=["user_input"],
                template=template
            )
            
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
            
            print(" LangChain đã sẵn sàng (OpenAI GPT-3.5)")
        
        except Exception as e:
            print(f"  Lỗi khởi tạo LangChain: {e}")
            print("Chuyển sang chế độ simple matching")
            self.llm = None
    
    def calibrate_microphone(self):
        """Hiệu chỉnh microphone với ambient noise"""
        print("🎤 Đang hiệu chỉnh microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print(" Microphone đã sẵn sàng")
    
    def connect_arduino(self):
        """Kết nối Arduino"""
        try:
            port = COM_PORT if COM_PORT else auto_detect_port()
            if not port:
                print(" Không tìm thấy COM port")
                return False
            
            print(f" Đang kết nối {port}...")
            self.ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)
            
            # Chọn mode 3 (Python Keyboard Mode)
            self.ser.write(b'3')
            time.sleep(1)
            
            # Clear buffer
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            self.is_running = True
            print(f" Đã kết nối {port}")
            return True
        
        except Exception as e:
            print(f" Lỗi kết nối: {e}")
            return False
    
    def listen(self):
        """Lắng nghe và nhận diện giọng nói"""
        try:
            with self.microphone as source:
                print("\n🎤 Đang nghe... (nói lệnh)")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            print(" Đang nhận diện...")
            
            # Nhận diện tiếng Việt
            text = self.recognizer.recognize_google(audio, language='vi-VN')
            print(f" Nghe được: '{text}'")
            
            return text.lower()
        
        except sr.WaitTimeoutError:
            print("Timeout - không nghe thấy gì")
            return None
        
        except sr.UnknownValueError:
            print("Không nhận diện được")
            return None
        
        except sr.RequestError as e:
            print(f"Lỗi API: {e}")
            return None
    
    def parse_command_simple(self, text):
        """Phân tích lệnh bằng simple matching"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Kiểm tra từng command
        for cmd, keywords in COMMANDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return cmd
        
        return None
    
    def parse_command_langchain(self, text):
        """Phân tích lệnh bằng LangChain + OpenAI"""
        if not text or not self.llm:
            return self.parse_command_simple(text)
        
        try:
            # Gọi LangChain
            result = self.chain.run(user_input=text)
            
            # Lấy ký tự đầu tiên (W/S/A/D/X)
            cmd = result.strip().upper()[0]
            
            if cmd in ['W', 'S', 'A', 'D', 'X']:
                return cmd
            else:
                print(f"LLM trả về không hợp lệ: {result}")
                return self.parse_command_simple(text)
        
        except Exception as e:
            print(f"Lỗi LangChain: {e}")
            return self.parse_command_simple(text)
    
    def send_command(self, command):
        """Gửi lệnh đến Arduino"""
        if not self.is_running or not self.ser or not self.ser.is_open:
            return False
        
        try:
            self.ser.write(command.encode())
            self.current_command = command
            self.command_count += 1
            return True
        except Exception as e:
            print(f"Lỗi gửi lệnh: {e}")
            return False
    
    def run(self):
        """Chạy vòng lặp chính"""
        print("\n" + "=" * 60)
        print("SMARTCAR VOICE CONTROL - LANGCHAIN")
        print("=" * 60)
        print(f"Mode: {'LangChain + OpenAI' if self.llm else 'Simple Matching'}")
        print(f"Language: Tiếng Việt")
        print(f"Commands: TIẾN | LÙI | TRÁI | PHẢI | DỪNG")
        print("=" * 60)
        print()
        
        if not self.connect_arduino():
            print("\n Chạy ở chế độ demo (không có Arduino)")
            input("Nhấn Enter để bắt đầu...")
            self.is_running = True
        
        print("\n Sẵn sàng nhận lệnh giọng nói!")
        print("Nhấn Ctrl+C để thoát\n")
        
        try:
            while self.is_running:
                # Lắng nghe
                text = self.listen()
                
                if text:
                    # Phân tích lệnh
                    if self.llm:
                        command = self.parse_command_langchain(text)
                    else:
                        command = self.parse_command_simple(text)
                    
                    if command:
                        # Mapping tên lệnh
                        cmd_names = {
                            'W': 'TIẾN',
                            'S': 'LÙI', 
                            'A': 'TRÁI',
                            'D': 'PHẢI',
                            'X': 'DỪNG'
                        }
                        
                        print(f" Lệnh: {cmd_names[command]} ({command})")
                        
                        # Gửi lệnh
                        if self.ser:
                            self.send_command(command)
                            print(f" Đã gửi lệnh [{self.command_count}]")
                        else:
                            print(f" Demo mode: {cmd_names[command]}")
                    else:
                        print(" Không nhận diện được lệnh -> Dừng")
                        if self.ser:
                            self.send_command('X')
        
        except KeyboardInterrupt:
            print("\n\n Dừng chương trình...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        if self.ser and self.ser.is_open:
            print(" Gửi lệnh dừng...")
            self.ser.write(b'X')
            time.sleep(0.2)
            self.ser.close()
            print(" Đã đóng serial")
        
        print(f"\n Tổng số lệnh: {self.command_count}")
        print("👋 Tạm biệt!")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SmartCar Voice Control')
    parser.add_argument('--simple', action='store_true', 
                       help='Dùng simple matching (không cần OpenAI API)')
    parser.add_argument('--demo', action='store_true',
                       help='Chế độ demo (không cần Arduino)')
    
    args = parser.parse_args()
    
    # Kiểm tra API key nếu dùng LangChain
    use_langchain = not args.simple
    if use_langchain and not OPENAI_API_KEY:
        print(" Không tìm thấy OPENAI_API_KEY")
        print("Set environment variable:")
        print("  Windows: set OPENAI_API_KEY=your-api-key")
        print("  Linux: export OPENAI_API_KEY=your-api-key")
        print("\nChuyển sang chế độ simple matching...\n")
        use_langchain = False
    
    # Khởi tạo controller
    controller = VoiceController(use_langchain=use_langchain)
    
    # Chạy
    controller.run()


if __name__ == "__main__":
    main()
