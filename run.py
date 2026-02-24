# -*- coding: utf-8 -*-
"""
run.py - SmartCar Control System (4 Modes)
NGÀY: 19/11/2025
"""
import os
import sys

def main():
    print("=" * 70)
    print("  SMARTCAR - HE THONG DIEU KHIEN")
    print("  SmartCar Control System - 4 Modes")
    print("=" * 70)
    print()
    print("CHE DO:")
    print("  [1] Test Camera        - Test nhan dien tay")
    print("  [2] OpenCV Mode        - Dieu khien bang cu chi tay")
    print("  [3] Keyboard Mode      - Dieu khien bang phim GUI")
    print("  [4] Web Control        - Dieu khien qua LAN")
    print("  [5] AWS Web Control    - Dieu khien AI (Amazon Nova Sonic 2)")
    print()
    print("  [0] Thoat")
    print()
    
    choice = input("Nhap lua chon (0-5): ").strip()
    
    if choice == '1':
        print("\nCHE DO 1: Test Camera")
        print("Nhan 'q' de thoat\n")
        os.chdir('Hand')
        os.system(f'{sys.executable} openCV.py')
        
    elif choice == '2':
        print("\nCHE DO 2: OpenCV Mode")
        print("Arduino: Upload SmartCar.ino, chon Mode [1]")
        print("Nhan 'q' de thoat\n")
        
        confirm = input("Arduino da san sang? (y/n): ").strip().lower()
        if confirm == 'y':
            os.chdir('UART')
            os.system(f'{sys.executable} transfer_UART.py')
        else:
            print("Huy bo!")
    
    elif choice == '3':
        print("\nCHE DO 3: Keyboard Mode")
        print("Arduino: Upload SmartCar.ino, chon Mode [3]")
        print("Nhan ESC de thoat\n")
        
        confirm = input("Arduino da san sang? (y/n): ").strip().lower()
        if confirm == 'y':
            os.system(f'{sys.executable} Keyboard/keyboard_control.py')
        else:
            print("Huy bo!")
    
    elif choice == '4':
        print("\nCHE DO 4: Web Control")
        print("Arduino: Upload SmartCar.ino, chon Mode [3]")
        print("Nhan Ctrl+C de thoat\n")
        
        confirm = input("Arduino da san sang? (y/n): ").strip().lower()
        if confirm == 'y':
            os.system(f'{sys.executable} Web/web_control.py')
        else:
            print("Huy bo!")
    
    elif choice == '5':
        print("\nCHE DO 5: AWS Web Control (AI)")
        print("Amazon Nova Sonic 2 - Natural Language Control")
        print("Arduino: Upload SmartCar.ino, chon Mode [3]")
        print("Nhan Ctrl+C de thoat\n")
        
        confirm = input("Arduino da san sang? (y/n): ").strip().lower()
        if confirm == 'y':
            os.system(f'{sys.executable} Web/aws_web_control.py')
        else:
            print("Huy bo!")
            
    elif choice == '0':
        print("\nTam biet!")
        sys.exit(0)
        
    else:
        print("\nLua chon khong hop le!")
        return main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nChuong trinh da dung!")
    except Exception as e:
        print(f"\n\nLoi: {e}")
