import serial
import time

PORT = "COM8"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

while True:
    ser.write(b"Hello ESP32/Arduino!\n")
    print("Sent.")
    time.sleep(1)   