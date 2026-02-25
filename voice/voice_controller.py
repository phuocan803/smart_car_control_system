# -*- coding: utf-8 -*-
"""
voice_controller.py - Natural Language Voice Command Recognition for Smart Car using LangChain
"""
import speech_recognition as sr
import serial
import time
import sys
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI

# Configuration defaults
COM_PORT = 'COM8'
BAUD_RATE = 9600
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Supported command dictionary
COMMANDS = {
    'W': ['forward', 'go forward', 'drive ahead', 'move forward', 'ahead'],
    'S': ['reverse', 'move back', 'go backward', 'backward', 'back'],
    'A': ['left', 'turn left', 'steer left', 'go left'],
    'D': ['right', 'turn right', 'steer right', 'go right'],
    'X': ['stop', 'halt', 'brake', 'emergency stop']
}

def auto_detect_port():
    """Auto-detect connected USB COM port."""
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
        
        if use_langchain and OPENAI_API_KEY:
            self.setup_langchain()
        else:
            print("Using simple keyword matching mode (LangChain offline).")
            self.llm = None
        
        self.calibrate_microphone()
    
    def setup_langchain(self):
        """Configure LangChain with OpenAI LLM model."""
        try:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                openai_api_key=OPENAI_API_KEY
            )
            
            template = """You are a smart vehicle voice command recognition agent.

Valid command codes:
- W: forward, drive ahead, move forward, ahead
- S: reverse, move back, backward, back
- A: left, turn left, steer left, go left
- D: right, turn right, steer right, go right
- X: stop, halt, brake, emergency stop

User input: "{user_input}"

Return EXACTLY one character: W, S, A, D, or X.
If ambiguous or unclear, return X (stop).
Do not include any explanation.
"""
            self.prompt = PromptTemplate(
                input_variables=["user_input"],
                template=template
            )
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
            print("LangChain AI Voice Agent initialized (OpenAI GPT-3.5).")
        
        except Exception as e:
            print(f"LangChain setup failed: {e}")
            print("Falling back to simple keyword matching mode.")
            self.llm = None
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient background noise."""
        print("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Microphone calibration complete.")
    
    def connect_arduino(self):
        """Establish serial connection to Arduino microcontroller."""
        try:
            port = COM_PORT if COM_PORT else auto_detect_port()
            if not port:
                print("Error: Serial COM port not found.")
                return False
            
            print(f"Connecting to serial port {port}...")
            self.ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)
            
            # Select Python Keyboard Mode on firmware
            self.ser.write(b'3')
            time.sleep(1)
            
            # Flush buffer
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            self.is_running = True
            print(f"Connected to Arduino on port {port}.")
            return True
        
        except Exception as e:
            print(f"Serial connection error: {e}")
            return False
    
    def listen(self):
        """Capture microphone input and transcribe speech to text."""
        try:
            with self.microphone as source:
                print("\nListening for voice command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            print("Processing voice audio...")
            text = self.recognizer.recognize_google(audio)
            print(f"Transcribed audio text: '{text}'")
            return text.lower()
        
        except sr.WaitTimeoutError:
            print("Listening timeout - no audio detected.")
            return None
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return None
    
    def parse_command_simple(self, text):
        """Parse command using keyword matching."""
        if not text:
            return None
        
        text_lower = text.lower()
        for cmd, keywords in COMMANDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return cmd
        return None
    
    def parse_command_langchain(self, text):
        """Parse command using LangChain LLM intent classification."""
        if not text or not self.llm:
            return self.parse_command_simple(text)
        
        try:
            result = self.chain.run(user_input=text)
            cmd = result.strip().upper()[0]
            
            if cmd in ['W', 'S', 'A', 'D', 'X']:
                return cmd
            else:
                print(f"Invalid LLM response: {result}")
                return self.parse_command_simple(text)
        
        except Exception as e:
            print(f"LangChain processing error: {e}")
            return self.parse_command_simple(text)
    
    def send_command(self, command):
        """Transmit command character to Arduino over serial link."""
        if not self.is_running or not self.ser or not self.ser.is_open:
            return False
        
        try:
            self.ser.write(command.encode())
            self.current_command = command
            self.command_count += 1
            return True
        except Exception as e:
            print(f"Serial transmission error: {e}")
            return False
    
    def run(self):
        """Main event loop for voice command controller."""
        print("\n" + "=" * 60)
        print("SMART CAR AI VOICE CONTROL SERVICE")
        print("=" * 60)
        print(f"Mode: {'LangChain + OpenAI' if self.llm else 'Keyword Matcher'}")
        print(f"Commands: FORWARD | REVERSE | LEFT | RIGHT | STOP")
        print("=" * 60)
        print()
        
        if not self.connect_arduino():
            print("\nRunning in simulation mode (no serial hardware).")
            input("Press Enter to begin...")
            self.is_running = True
        
        print("\nVoice control ready. Speak commands into your microphone.")
        print("Press Ctrl+C to terminate.\n")
        
        try:
            while self.is_running:
                text = self.listen()
                
                if text:
                    if self.llm:
                        command = self.parse_command_langchain(text)
                    else:
                        command = self.parse_command_simple(text)
                    
                    if command:
                        cmd_names = {
                            'W': 'FORWARD',
                            'S': 'REVERSE',
                            'A': 'LEFT',
                            'D': 'RIGHT',
                            'X': 'STOP'
                        }
                        print(f"Action: {cmd_names[command]} ({command})")
                        
                        if self.ser:
                            self.send_command(command)
                            print(f"Sent command #{self.command_count}")
                        else:
                            print(f"Simulation Mode: {cmd_names[command]}")
                    else:
                        print("Unrecognized command -> Executing STOP")
                        if self.ser:
                            self.send_command('X')
        
        except KeyboardInterrupt:
            print("\nTerminating voice control service...")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Release resources on termination."""
        if self.ser and self.ser.is_open:
            print("Transmitting stop command...")
            self.ser.write(b'X')
            time.sleep(0.2)
            self.ser.close()
            print("Serial connection closed.")
        
        print(f"\nTotal commands dispatched: {self.command_count}")
        print("Service stopped cleanly.")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Car AI Voice Controller')
    parser.add_argument('--simple', action='store_true', 
                       help='Use simple keyword matching without OpenAI API')
    parser.add_argument('--demo', action='store_true',
                       help='Run in demonstration mode without serial hardware')
    
    args = parser.parse_args()
    
    use_langchain = not args.simple
    if use_langchain and not OPENAI_API_KEY:
        print("Environment variable OPENAI_API_KEY not found.")
        print("To enable LangChain AI mode, export OPENAI_API_KEY=your-api-key")
        print("Defaulting to simple keyword matching mode...\n")
        use_langchain = False
    
    controller = VoiceController(use_langchain=use_langchain)
    controller.run()

if __name__ == "__main__":
    main()
