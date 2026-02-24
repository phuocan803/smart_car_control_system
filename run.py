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
    print("  SmartCar Control System - 6 Modes")
    print("=" * 70)
    print()
    print("CHE DO LOCAL:")
    print("  [1] Test Camera        - Test nhan dien tay")
    print("  [2] OpenCV Mode        - Dieu khien bang cu chi tay")
    print("  [3] Keyboard Mode      - Dieu khien bang phim GUI")
    print("  [4] Web Control        - Dieu khien qua LAN")
    print()
    print("CHE DO CLOUD (AWS):")
    print("  [5] AWS Server Local   - Chay server local (dev only)")
    print("  [6] Bridge Client      - Ket noi voicecar.pngha.io.vn voi Arduino")
    print("                           (Xu dung de dieu khien qua internet)")
    print()
    print("  [0] Thoat")
    print()
    
    choice = input("Nhap lua chon (0-6): ").strip()
    
    if choice == '1':
        print("\nCHE DO 1: Test Camera")
        print("Nhan 'q' de thoat\n")
        os.chdir('Hand')
        os.system(f'"{sys.executable}" openCV.py')
        
    elif choice == '2':
        print("\nCHE DO 2: OpenCV Mode")
        print("Arduino: Upload SmartCar.ino, chon Mode [1]")
        print("Nhan 'q' de thoat\n")
        
        confirm = input("Arduino da san sang? (y/n): ").strip().lower()
        if confirm == 'y':
            os.chdir('UART')
            os.system(f'"{sys.executable}" transfer_UART.py')
        else:
            print("Huy bo!")
    
    elif choice == '3':
        print("\nCHE DO 3: Keyboard Mode")
        print("Arduino: Upload SmartCar.ino, chon Mode [3]")
        print("Nhan ESC de thoat\n")
        
        confirm = input("Arduino da san sang? (y/n): ").strip().lower()
        if confirm == 'y':
            os.system(f'"{sys.executable}" Keyboard/keyboard_control.py')
        else:
            print("Huy bo!")
    
    elif choice == '4':
        print("\nCHE DO 4: Web Control")
        print("Arduino: Upload SmartCar.ino, chon Mode [3]")
        print("Nhan Ctrl+C de thoat\n")
        
        confirm = input("Arduino da san sang? (y/n): ").strip().lower()
        if confirm == 'y':
            os.system(f'"{sys.executable}" Web/web_control.py')
        else:
            print("Huy bo!")
    
    elif choice == '5':
        print("\nCHE DO 5: AWS Server Local (Dev Only)")
        print("Chay AWS server tren may local de test/development")
        print("Luu y: Server da chay san tren EC2 (voicecar.pngha.io.vn)")
        print("Chi dung neu ban muon test server local!\n")
        
        confirm = input("Ban chac chan muon chay server local? (y/n): ").strip().lower()
        if confirm == 'y':
            test_mode = input("Test mode (khong can Arduino)? (y/n): ").strip().lower()
            if test_mode == 'y':
                os.system(f'"{sys.executable}" Web/aws_web_voice_control.py --test')
            else:
                os.system(f'"{sys.executable}" Web/aws_web_voice_control.py')
        else:
            print("Huy bo!")
    
    elif choice == '6':
        print("\nCHE DO 6: Bridge Client")
        print("Ket noi AWS Server (voicecar.pngha.io.vn) voi Arduino local")
        print()
        print("Sau khi chay Bridge Client:")
        print("  1. Mo browser: https://voicecar.pngha.io.vn/")
        print("  2. Dung voice/button/keyboard de dieu khien xe")
        print("  3. Lenh tu web se tu dong forward xuong Arduino")
        print()
        print("Arduino: Upload SmartCar.ino, chon Mode [3]")
        print("Nhan Ctrl+C de thoat\n")
        
        print("Chon che do:")
        print("  [1] Test Mode (khong can Arduino - chi xem log)")
        print("  [2] Arduino Mode (ket noi that)")
        mode = input("Nhap lua chon (1-2): ").strip()
        
        if mode == '1':
            print("\nTest Mode - chi hien thi log, khong dieu khien Arduino")
            print("Mo browser: https://voicecar.pngha.io.vn/ va thu dieu khien")
            print("Ban se thay log hien thi o day\n")
            os.system(f'"{sys.executable}" Web/local_bridge_client.py --test')
        elif mode == '2':
            confirm = input("\nArduino da san sang? (y/n): ").strip().lower()
            if confirm == 'y':
                print("\nBridge Client dang chay...")
                print("Mo browser: https://voicecar.pngha.io.vn/ de dieu khien\n")
                os.system(f'"{sys.executable}" Web/local_bridge_client.py')
            else:
                print("Huy bo!")
        else:
            print("Lua chon khong hop le!")
            
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
