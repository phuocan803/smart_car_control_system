# -*- coding: utf-8 -*-
"""
motor_test.py - Smart Car Serial Motor Driver Test Script
"""
import serial
import time

COM_PORT = ''
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

def test_car():
    print("=" * 50)
    print("  SMART CAR SERIAL MOTOR DRIVER TEST")
    print("=" * 50)
    
    try:
        port = COM_PORT if COM_PORT else auto_detect_port()
        if not port:
            print("\nError: Serial COM port not found.")
            return
        
        print(f"\nConnecting to {port} at {BAUD_RATE} baud...")
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)
        print("Connected successfully!\n")
        
        print("Arduino initial boot telemetry:")
        for _ in range(15):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"  {line}")
            time.sleep(0.1)
        
        print("\nSending command '1' - Selecting OpenCV Mode...")
        ser.write(b'1')
        time.sleep(1)
        
        test_sequence = [
            ('W', "FORWARD", 2),
            ('S', "REVERSE", 2),
            ('A', "LEFT", 1.5),
            ('D', "RIGHT", 1.5),
            ('X', "STOP", 1)
        ]
        
        print("\nExecuting test sequence:")
        for cmd, name, duration in test_sequence:
            print(f"  Command: {cmd} ({name}) - Duration: {duration}s")
            ser.write(cmd.encode())
            
            start_time = time.time()
            while time.time() - start_time < duration:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"    Arduino response: {line}")
                time.sleep(0.1)
        
        print("\nTest sequence complete! Closing serial port...")
        ser.close()
        print("Serial port closed cleanly.")
        
    except Exception as e:
        print(f"\nSerial test failed: {e}")

if __name__ == "__main__":
    test_car()
