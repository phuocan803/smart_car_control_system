# -*- coding: utf-8 -*-
"""
serial_interface.py - Serial UART Hardware Controller Wrapper for Smart Car
"""
import serial
import time

class UARTController:
    def __init__(self, port='COM3', baud_rate=9600, timeout=1):
        """Initialize serial connection parameters."""
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None
        self.is_connected = False
        self.command_count = 0
        self.last_command = None
        
    def __enter__(self):
        """Establish serial connection on context entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect serial port safely on context exit."""
        if self.is_connected:
            self.send_command('X')
            time.sleep(0.1)
        self.disconnect()
        return False
    
    def connect(self):
        """Connect to target serial port."""
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)
            self.is_connected = True
            print(f"Connected to serial port {self.port} at {self.baud_rate} baud rate.")
            return True
        except Exception as e:
            print(f"Failed to open serial port {self.port}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close active serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.is_connected = False
            print(f"Disconnected from serial port {self.port}.")
    
    def send_command(self, command):
        """Send command character code over serial line."""
        if not self.is_connected or not self.serial:
            return False
        
        try:
            self.serial.write(command.encode())
            self.command_count += 1
            self.last_command = command
            return True
        except Exception as e:
            print(f"Error transmitting command over serial line: {e}")
            return False

def test_serial(port='COM3', baud_rate=9600):
    """Test serial transmission sequence."""
    print("Initializing serial interface test...")
    with UARTController(port, baud_rate) as car:
        if car.is_connected:
            print("Transmitting test command sequence: W -> X")
            car.send_command('W')
            time.sleep(1)
            car.send_command('X')
            print("Serial test sequence complete.")

if __name__ == '__main__':
    test_serial()
