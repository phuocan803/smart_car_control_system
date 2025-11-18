# -*- coding: utf-8 -*-
"""
test_car.py - SmartCar Serial Test
NGÀY: 19/11/2025
"""
import serial
import time

COM_PORT = ''
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

def test_car():
    print("=" * 50)
    print("  TEST SMARTCAR - SERIAL CONTROL")
    print("=" * 50)
    
    try:
        port = COM_PORT if COM_PORT else auto_detect_port()
        if not port:
            print("\nKhong tim thay COM port")
            return
        
        print(f"\nKet noi toi {port}...")
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)
        print("Ket noi thanh cong!\n")
        
        print("Arduino output:")
        for _ in range(15):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"  {line}")
            time.sleep(0.1)
        
        print("\nGui lenh '1' - Chon OpenCV Mode")
        ser.write(b'1')
        time.sleep(1)
        
        print("\nArduino response:")
        for _ in range(5):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"  {line}")
            time.sleep(0.1)
        
        print("\n" + "=" * 50)
        print("  BAT DAU TEST CHUYEN DONG")
        print("=" * 50)
        
        commands = [
            ('W', 'TIEN', 2),
            ('X', 'DUNG', 1),
            ('S', 'LUI', 2),
            ('X', 'DUNG', 1),
            ('A', 'TRAI', 2),
            ('X', 'DUNG', 1),
            ('D', 'PHAI', 2),
            ('X', 'DUNG', 1),
        ]
        
        for cmd, name, duration in commands:
            print(f"\nLenh: {cmd} ({name}) - {duration}s")
            ser.write(cmd.encode())
            
            for i in range(duration):
                print(f"  [{i+1}/{duration}s]", end='\r')
                time.sleep(1)
            print()
        
        print("\nGui lenh dung")
        ser.write(b'X')
        time.sleep(0.5)
        
        print("\n" + "=" * 50)
        print("  TEST HOAN THANH")
        print("=" * 50)
        
        ser.close()
        print("\nDa dong ket noi Serial")
        
    except serial.SerialException as e:
        print(f"\nLoi Serial: {e}")
        print("Kiem tra:")
        print("  - Arduino da ket noi chua?")
        print("  - COM port dung chua?")
        print("  - Serial Monitor da dong chua?")
    except KeyboardInterrupt:
        print("\n\nDung boi nguoi dung")
        if 'ser' in locals() and ser.is_open:
            ser.write(b'X')
            ser.close()
    except Exception as e:
        print(f"\nLoi: {e}")

if __name__ == "__main__":
    print("\nSMARTCAR TEST SCRIPT")
    print("Chu y: Arduino phai duoc upload SmartCar.ino\n")
    
    input("Nhan Enter de bat dau test...")
    test_car()
