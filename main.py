import serial
import serial.tools.list_ports
import json
import pyautogui
import sys

# PC側で待ち受けるポートの設定
# Macの場合は '/dev/cu.usbmodemXXX' などになります
# 空にすると利用可能なポートを表示します
SERIAL_PORT = '' 
BAUD_RATE = 115200

def list_available_ports():
    ports = serial.tools.list_ports.comports()
    print("Available ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} ({port.description})")
    return ports

def process_command(line):
    # (既存のロジックと同じ)
    try:
        data = json.loads(line)
        action = data.get("action")
        # ...
        
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
    global SERIAL_PORT
    ports = list_available_ports()
    
    if not SERIAL_PORT:
        if not ports:
            print("No serial ports found.")
            return
        # 自動で最初のポートを選択するか、入力を待つ
        SERIAL_PORT = ports[0].device
        print(f"Automatically selected {SERIAL_PORT}")

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