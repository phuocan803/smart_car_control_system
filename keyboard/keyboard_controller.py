# -*- coding: utf-8 -*-
"""
keyboard_controller.py - Smart Car Graphical Desktop Keyboard Controller
"""
import serial
import time
import sys
import os
import tkinter as tk
from tkinter import ttk
import threading

COM_PORT = 'COM8'
BAUD_RATE = 9600

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

class KeyboardControlGUI:
    def __init__(self, test_mode=False):
        self.root = tk.Tk()
        self.root.title("Smart Car - Keyboard Controller" + (" [SIMULATION MODE]" if test_mode else ""))
        self.root.geometry("420x570")
        self.root.resizable(False, False)
        
        self.test_mode = test_mode
        self.ser = None
        self.current_command = 'X'
        self.is_running = False
        self.command_count = 0
        self.test_log = []
        
        self.setup_ui()
        self.setup_keyboard()
        
        if not test_mode:
            self.root.after(0, self.connect_arduino)
        
    def setup_ui(self):
        title = tk.Label(self.root, text="SMART CAR KEYBOARD CONTROLLER", 
                         font=("Arial", 14, "bold"), fg="#2196F3")
        title.pack(pady=10)
        
        if self.test_mode:
            self.status_label = tk.Label(self.root, text="SIMULATION MODE - Running without hardware", 
                                         font=("Arial", 11), fg="green")
        else:
            self.status_label = tk.Label(self.root, text="Disconnected", 
                                         font=("Arial", 11), fg="orange")
        self.status_label.pack(pady=5)
        
        self.counter_label = tk.Label(self.root, text="Commands Dispatched: 0", 
                                      font=("Arial", 10))
        self.counter_label.pack(pady=5)
        
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=15)
        
        button_style = {
            'width': 9,
            'height': 3,
            'font': ("Arial", 12, "bold")
        }
        
        self.buttons = {}
        
        # W Button (Forward)
        self.buttons['W'] = tk.Button(control_frame, text="W\nFORWARD", 
                                      bg="#4CAF50", fg="white", **button_style)
        self.buttons['W'].grid(row=0, column=1, padx=5, pady=5)
        
        # A S D Buttons (Left / Reverse / Right)
        self.buttons['A'] = tk.Button(control_frame, text="A\nLEFT", 
                                      bg="#2196F3", fg="white", **button_style)
        self.buttons['A'].grid(row=1, column=0, padx=5, pady=5)
        
        self.buttons['S'] = tk.Button(control_frame, text="S\nREVERSE", 
                                      bg="#f44336", fg="white", **button_style)
        self.buttons['S'].grid(row=1, column=1, padx=5, pady=5)
        
        self.buttons['D'] = tk.Button(control_frame, text="D\nRIGHT", 
                                      bg="#FF9800", fg="white", **button_style)
        self.buttons['D'].grid(row=1, column=2, padx=5, pady=5)
        
        # X Button (Stop)
        self.buttons['X'] = tk.Button(control_frame, text="X\nSTOP", 
                                      bg="#9E9E9E", fg="white", **button_style)
        self.buttons['X'].grid(row=2, column=1, padx=5, pady=5)
        
        self.command_display = tk.Label(self.root, text="Active Command: STOP (X)", 
                                        font=("Arial", 13, "bold"), 
                                        fg="white", bg="#9E9E9E", 
                                        width=28, height=2)
        self.command_display.pack(pady=15)
        
        instructions = tk.Label(self.root, 
                                text="Press keys W / A / S / D / X or click buttons\nPress ESC to exit",
                                font=("Arial", 10), fg="gray")
        instructions.pack(pady=5)
        
        if not self.test_mode:
            self.connect_btn = tk.Button(self.root, text="CONNECT ARDUINO", 
                                         command=self.connect_arduino,
                                         bg="#4CAF50", fg="white", 
                                         font=("Arial", 11, "bold"),
                                         width=22, height=2)
            self.connect_btn.pack(pady=10)
        else:
            self.is_running = True
            test_label = tk.Label(self.root, text="Simulation Mode Active - Use keyboard to test",
                                  font=("Arial", 10, "bold"), fg="blue")
            test_label.pack(pady=10)
            
            self.send_thread = threading.Thread(target=self.continuous_send, daemon=True)
            self.send_thread.start()
        
    def setup_keyboard(self):
        self.root.bind('<KeyPress-w>', lambda e: self.send_command('W'))
        self.root.bind('<KeyPress-W>', lambda e: self.send_command('W'))
        self.root.bind('<KeyPress-s>', lambda e: self.send_command('S'))
        self.root.bind('<KeyPress-S>', lambda e: self.send_command('S'))
        self.root.bind('<KeyPress-a>', lambda e: self.send_command('A'))
        self.root.bind('<KeyPress-A>', lambda e: self.send_command('A'))
        self.root.bind('<KeyPress-d>', lambda e: self.send_command('D'))
        self.root.bind('<KeyPress-D>', lambda e: self.send_command('D'))
        self.root.bind('<KeyPress-x>', lambda e: self.send_command('X'))
        self.root.bind('<KeyPress-X>', lambda e: self.send_command('X'))
        self.root.bind('<space>', lambda e: self.send_command('X'))
        self.root.bind('<Escape>', lambda e: self.quit_app())
        
        for key, btn in self.buttons.items():
            btn.config(command=lambda k=key: self.send_command(k))
    
    def connect_arduino(self):
        try:
            port = COM_PORT if COM_PORT else auto_detect_port()
            if not port:
                self.status_label.config(text="Serial COM port not found", fg="red")
                return
            
            self.status_label.config(text=f"Connecting to {port}...", fg="orange")
            self.root.update()
            
            self.ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)
            
            self.ser.write(b'3')
            time.sleep(1)
            
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            self.is_running = True
            self.status_label.config(text=f"Connected on {port}", fg="green")
            self.connect_btn.config(state='disabled', bg='gray')
            
            self.send_thread = threading.Thread(target=self.continuous_send, daemon=True)
            self.send_thread.start()
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)[:30]}", fg="red")
    
    def send_command(self, command):
        if not self.is_running:
            return
        
        self.current_command = command
        self.update_display(command)
        
        if self.test_mode:
            timestamp = time.strftime("%H:%M:%S")
            log_msg = f"[{timestamp}] Command: {command}"
            self.test_log.append(log_msg)
            print(log_msg)
    
    def continuous_send(self):
        while self.is_running:
            try:
                if self.test_mode:
                    self.command_count += 1
                    self.counter_label.config(text=f"Commands Dispatched: {self.command_count}")
                elif self.ser and self.ser.is_open:
                    self.ser.write(self.current_command.encode())
                    self.command_count += 1
                    self.counter_label.config(text=f"Commands Dispatched: {self.command_count}")
                time.sleep(0.05)
            except Exception:
                break
    
    def update_display(self, command):
        command_names = {
            'W': ('FORWARD', '#4CAF50'),
            'S': ('REVERSE', '#f44336'),
            'A': ('LEFT', '#2196F3'),
            'D': ('RIGHT', '#FF9800'),
            'X': ('STOP', '#9E9E9E')
        }
        
        name, color = command_names.get(command, ('UNKNOWN', 'gray'))
        self.command_display.config(text=f"Active Command: {name} ({command})", bg=color)
        
        for key, btn in self.buttons.items():
            if key == command:
                btn.config(relief='sunken')
            else:
                btn.config(relief='raised')
    
    def quit_app(self):
        self.is_running = False
        if self.ser and self.ser.is_open:
            self.ser.write(b'X')
            time.sleep(0.2)
            self.ser.close()
        self.root.destroy()
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

if __name__ == "__main__":
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    
    if test_mode:
        print("=" * 50)
        print("SMART CAR KEYBOARD CONTROL - SIMULATION MODE")
        print("=" * 50)
        print("Running in simulation mode without active serial hardware.")
        print("Press keys W/A/S/D/X or click buttons to test UI.")
        print("Press ESC to exit.")
        print("=" * 50)
    
    app = KeyboardControlGUI(test_mode=test_mode)
    app.run()
