# -*- coding: utf-8 -*-
"""
keyboard_control.py - SmartCar Python Keyboard Control (Mode 3)
NGÀY: 19/11/2025
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
        self.root.title("SmartCar - Keyboard Control" + (" [TEST MODE]" if test_mode else ""))
        self.root.geometry("400x550")
        self.root.resizable(False, False)
        
        self.test_mode = test_mode
        self.ser = None
        self.current_command = 'X'
        self.is_running = False
        self.command_count = 0
        self.test_log = []
        
        self.setup_ui()
        self.setup_keyboard()
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="SMARTCAR KEYBOARD CONTROL", 
                        font=("Arial", 16, "bold"), fg="#2196F3")
        title.pack(pady=10)
        
        # Status
        if self.test_mode:
            self.status_label = tk.Label(self.root, text="TEST MODE - Khong can Arduino", 
                                        font=("Arial", 12), fg="green")
        else:
            self.status_label = tk.Label(self.root, text="Chua ket noi", 
                                        font=("Arial", 12), fg="orange")
        self.status_label.pack(pady=5)
        
        # Command counter
        self.counter_label = tk.Label(self.root, text="Lenh da gui: 0", 
                                     font=("Arial", 10))
        self.counter_label.pack(pady=5)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20)
        
        # Button style
        button_style = {
            'width': 8,
            'height': 3,
            'font': ("Arial", 14, "bold")
        }
        
        # Create buttons in grid
        self.buttons = {}
        
        # W button (top)
        self.buttons['W'] = tk.Button(control_frame, text="W\nTIEN", 
                                      bg="#4CAF50", fg="white", **button_style)
        self.buttons['W'].grid(row=0, column=1, padx=5, pady=5)
        
        # A S D buttons (middle row)
        self.buttons['A'] = tk.Button(control_frame, text="A\nTRAI", 
                                      bg="#2196F3", fg="white", **button_style)
        self.buttons['A'].grid(row=1, column=0, padx=5, pady=5)
        
        self.buttons['S'] = tk.Button(control_frame, text="S\nLUI", 
                                      bg="#f44336", fg="white", **button_style)
        self.buttons['S'].grid(row=1, column=1, padx=5, pady=5)
        
        self.buttons['D'] = tk.Button(control_frame, text="D\nPHAI", 
                                      bg="#FF9800", fg="white", **button_style)
        self.buttons['D'].grid(row=1, column=2, padx=5, pady=5)
        
        # X button (bottom)
        self.buttons['X'] = tk.Button(control_frame, text="X\nDUNG", 
                                      bg="#9E9E9E", fg="white", **button_style)
        self.buttons['X'].grid(row=2, column=1, padx=5, pady=5)
        
        # Current command display
        self.command_display = tk.Label(self.root, text="Lenh hien tai: DUNG (X)", 
                                       font=("Arial", 14, "bold"), 
                                       fg="white", bg="#9E9E9E", 
                                       width=25, height=2)
        self.command_display.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="Nhan phim W/A/S/D/X hoac click nut\nNhan ESC de thoat",
                               font=("Arial", 10), fg="gray")
        instructions.pack(pady=10)
        
        # Connect button
        if not self.test_mode:
            self.connect_btn = tk.Button(self.root, text="KET NOI ARDUINO", 
                                        command=self.connect_arduino,
                                        bg="#4CAF50", fg="white", 
                                        font=("Arial", 12, "bold"),
                                        width=20, height=2)
            self.connect_btn.pack(pady=10)
        else:
            # Auto-start in test mode
            self.is_running = True
            test_label = tk.Label(self.root, text="Che do test - Nhan phim de thu nghiem",
                                 font=("Arial", 10, "bold"), fg="blue")
            test_label.pack(pady=10)
            
            # Start sending thread for test mode
            self.send_thread = threading.Thread(target=self.continuous_send, daemon=True)
            self.send_thread.start()
        
    def setup_keyboard(self):
        # Bind keyboard events
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
        
        # Bind button clicks
        for key, btn in self.buttons.items():
            btn.config(command=lambda k=key: self.send_command(k))
    
    def connect_arduino(self):
        try:
            port = COM_PORT if COM_PORT else auto_detect_port()
            if not port:
                self.status_label.config(text="Khong tim thay COM port", fg="red")
                return
            
            self.status_label.config(text=f"Dang ket noi {port}...", fg="orange")
            self.root.update()
            
            self.ser = serial.Serial(port, BAUD_RATE, timeout=1)
            time.sleep(2)
            
            self.ser.write(b'3')
            time.sleep(1)
            
            while self.ser.in_waiting > 0:
                self.ser.readline()
            
            self.is_running = True
            self.status_label.config(text=f"Da ket noi {port}", fg="green")
            self.connect_btn.config(state='disabled', bg='gray')
            
            # Start sending thread
            self.send_thread = threading.Thread(target=self.continuous_send, daemon=True)
            self.send_thread.start()
            
        except Exception as e:
            self.status_label.config(text=f"Loi: {str(e)[:30]}", fg="red")
    
    def send_command(self, command):
        if not self.is_running:
            return
        
        self.current_command = command
        self.update_display(command)
        
        # Test mode: log command
        if self.test_mode:
            timestamp = time.strftime("%H:%M:%S")
            log_msg = f"[{timestamp}] Lenh: {command}"
            self.test_log.append(log_msg)
            print(log_msg)  # Print to console
    
    def continuous_send(self):
        """Continuously send current command to Arduino"""
        while self.is_running:
            try:
                if self.test_mode:
                    # Test mode: just count
                    self.command_count += 1
                    self.counter_label.config(text=f"Lenh da gui: {self.command_count}")
                elif self.ser and self.ser.is_open:
                    self.ser.write(self.current_command.encode())
                    self.command_count += 1
                    self.counter_label.config(text=f"Lenh da gui: {self.command_count}")
                time.sleep(0.05)  # 20Hz
            except:
                break
    
    def update_display(self, command):
        command_names = {
            'W': ('TIEN', '#4CAF50'),
            'S': ('LUI', '#f44336'),
            'A': ('TRAI', '#2196F3'),
            'D': ('PHAI', '#FF9800'),
            'X': ('DUNG', '#9E9E9E')
        }
        
        name, color = command_names.get(command, ('UNKNOWN', 'gray'))
        self.command_display.config(text=f"Lenh hien tai: {name} ({command})", bg=color)
        
        # Highlight button
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
    # Check for test mode argument
    test_mode = '--test' in sys.argv or '-t' in sys.argv
    
    if test_mode:
        print("=" * 50)
        print("SMARTCAR KEYBOARD CONTROL - TEST MODE")
        print("=" * 50)
        print("Che do test: Khong can Arduino")
        print("Nhan phim W/A/S/D/X hoac click nut de test")
        print("Nhan ESC de thoat")
        print("=" * 50)
    
    app = KeyboardControlGUI(test_mode=test_mode)
    app.run()
