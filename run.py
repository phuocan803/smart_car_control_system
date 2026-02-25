# -*- coding: utf-8 -*-
"""
run.py - Smart Car Control System Main Launcher
"""
import os
import sys

# Store root project directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def run_script(script_path, args=""):
    """Helper to run a Python script relative to project root."""
    os.chdir(PROJECT_ROOT)
    full_path = os.path.join(PROJECT_ROOT, script_path)
    cmd = f'"{sys.executable}" "{full_path}" {args}'.strip()
    return os.system(cmd)

def main():
    os.chdir(PROJECT_ROOT)
    print("=" * 70)
    print("  SMART CAR - CONTROL SYSTEM LAUNCHER")
    print("  Multi-Modal Smart Car Control System")
    print("=" * 70)
    print()
    print("LOCAL CONTROL MODES:")
    print("  [1] Test Camera        - Hand gesture detection test")
    print("  [2] OpenCV Mode        - Hand gesture steering control")
    print("  [3] Keyboard Mode      - Tkinter GUI keyboard control")
    print("  [4] Web Control        - Local LAN web interface control")
    print()
    print("CLOUD (AWS) & AI CONTROL MODES:")
    print("  [5] AWS Server Local   - Run local AWS server (dev test)")
    print("  [6] Bridge Client      - Connect remote AWS Cloud server with Arduino")
    print("  [7] Voice Control      - AI Voice control with LangChain + OpenAI")
    print()
    print("  [0] Exit")
    print()
    
    choice = input("Enter choice (0-7): ").strip()
    
    if choice == '1':
        print("\nMODE 1: Test Camera")
        print("Press 'q' in camera window to exit\n")
        run_script("vision/gesture_visualizer.py")
        
    elif choice == '2':
        print("\nMODE 2: OpenCV Mode")
        print("Arduino: Upload firmware/smart_car.ino, select Mode [1]")
        print("Press 'q' in camera window to exit\n")
        
        confirm = input("Is Arduino connected and ready? (y/n): ").strip().lower()
        if confirm == 'y':
            run_script("serial_bridge/gesture_serial_bridge.py")
        else:
            print("Cancelled!")
    
    elif choice == '3':
        print("\nMODE 3: Keyboard Mode")
        print("Arduino: Upload firmware/smart_car.ino, select Mode [3]")
        print("Press ESC to exit GUI\n")
        
        confirm = input("Is Arduino connected and ready? (y/n): ").strip().lower()
        if confirm == 'y':
            run_script("keyboard/keyboard_controller.py")
        else:
            print("Cancelled!")
    
    elif choice == '4':
        print("\nMODE 4: Web Control (LAN)")
        print("Arduino: Upload firmware/smart_car.ino, select Mode [3]")
        print("Press Ctrl+C to exit\n")
        
        confirm = input("Is Arduino connected and ready? (y/n): ").strip().lower()
        if confirm == 'y':
            run_script("web/local_server.py")
        else:
            print("Cancelled!")
    
    elif choice == '5':
        print("\nMODE 5: AWS Server Local (Development)")
        print("Run local server instance for development and testing\n")
        
        confirm = input("Run local AWS server? (y/n): ").strip().lower()
        if confirm == 'y':
            test_mode = input("Run in simulation mode without Arduino? (y/n): ").strip().lower()
            if test_mode == 'y':
                run_script("web/cloud_server.py", "--test")
            else:
                run_script("web/cloud_server.py")
        else:
            print("Cancelled!")
    
    elif choice == '6':
        print("\nMODE 6: Cloud Bridge Client")
        print("Connects remote AWS Cloud server with local Arduino serial port\n")
        print("Select operational mode:")
        print("  [1] Simulation Mode (Log viewer only - no Arduino required)")
        print("  [2] Hardware Mode   (Active Arduino serial connection)")
        mode = input("Enter choice (1-2): ").strip()
        
        if mode == '1':
            print("\nSimulation Mode started. Monitoring command events from cloud server...")
            run_script("web/cloud_bridge_client.py", "--test")
        elif mode == '2':
            confirm = input("\nIs Arduino connected and ready? (y/n): ").strip().lower()
            if confirm == 'y':
                run_script("web/cloud_bridge_client.py")
            else:
                print("Cancelled!")
        else:
            print("Invalid selection!")
            
    elif choice == '7':
        print("\nMODE 7: Voice Control (LangChain + OpenAI)")
        print("Recognizes spoken commands and processes natural language intent\n")
        run_script("voice/voice_controller.py")
        
    elif choice == '0':
        print("\nExiting Smart Car Launcher. Goodbye!")
        sys.exit(0)
        
    else:
        print("\nInvalid selection! Please enter a number between 0 and 7.")
        return main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
