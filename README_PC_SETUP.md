# PC Setup for Gemini Mirroring

To allow your PC to be controlled by the smartphone via Serial, you need a listener script on the PC.

## Prerequisites

1.  **Python 3** installed.
2.  Install required libraries:
    ```bash
    pip install pyserial pyautogui
    ```
3.  **Virtual Serial Port (optional)**: If you are testing on the same PC (Smartphone connected to PC via USB), your PC needs to act as a Serial device. Usually, this is done via a microcontroller (like Arduino) or a software like "com0com". However, if you're using a smartphone, it will connect to a USB-to-Serial converter or an Arduino.

## Listener Script (listener.py)

Save the following code as `listener.py` and run it:

```python
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
```

## How to use

1.  Connect your Smartphone to the PC via USB.
2.  Enable "USB Debugging" is NOT needed, but you might need an **OTG adapter** on the phone side to connect a USB-to-Serial converter, OR use a software bridge if you are using a network-to-serial bridge.
3.  On Chrome (Android), open the Svelte app.
4.  Click **Connect Serial** and select the port.
5.  Type instructions for Gemini!
