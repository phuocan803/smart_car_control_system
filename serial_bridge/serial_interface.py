# -*- coding: utf-8 -*-
"""
UART.py - Simple UART Controller for SmartCar
NGÀY: 19/11/2025
"""
import serial
import time

class UARTController:
    def __init__(self, port='COM3', baud_rate=9600, timeout=1):
        """Initialize UART connection"""
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None
        self.is_connected = False
        self.command_count = 0
        self.last_command = None
        
    def __enter__(self):
        """Connect when entering context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect when exiting context manager"""
        # Send stop command before closing
        if self.is_connected:
            self.send_command('X')
            time.sleep(0.1)
        self.disconnect()
        return False
    
    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)
            self.is_connected = True
            print(f"Connected to {self.port} @ {self.baud_rate} baud")
            return True
        except Exception as e:
            print(f"Failed to connect to {self.port}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.is_connected = False
            print(f"Disconnected from {self.port}")
    
    def send_command(self, command):
        if not self.is_connected or not self.serial:
            return False
        
        try:
            self.serial.write(command.encode())
            self.command_count += 1
            self.last_command = command
            return True
        except Exception as e:
            print(f"Error sending command: {e}")
            return False
    
    def read_response(self):
        if not self.is_connected or not self.serial:
            return None
        
        try:
            if self.serial.in_waiting > 0:
                response = self.serial.readline().decode('utf-8').strip()
                return response
        except Exception as e:
            print(f"Error reading response: {e}")
        
        return None
    
    def get_stats(self):
        return {
            'port': self.port,
            'baud_rate': self.baud_rate,
            'is_connected': self.is_connected,
            'command_count': self.command_count,
            'last_command': self.last_command or 'None'
        }
