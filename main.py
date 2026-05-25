import serial
import json
import pyautogui
import sys

# Change this to your Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
SERIAL_PORT = 'COM1' 
BAUD_RATE = 115200

# Security: Disable fail-safe if you want, but be careful!
# pyautogui.FAILSAFE = False 

def process_command(line):
    try:
        data = json.loads(line)
        action = data.get("action")
        
        if action == "mouseMove":
            pyautogui.moveTo(data["x"], data["y"])
        elif action == "mouseClick":
            pyautogui.click(button=data["button"])
        elif action == "keyTap":
            pyautogui.press(data["key"])
        elif action == "typeString":
            pyautogui.write(data["text"])
        
        print(f"Executed: {action}")
    except Exception as e:
        print(f"Error processing line: {line.strip()} - {e}")

def main():
    print(f"Listening on {SERIAL_PORT}...")
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1) as ser:
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    process_command(line)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Serial Error: {e}")

if __name__ == "__main__":
    main()