import asyncio
import websockets
import json
import pyautogui
import socket

def get_local_ip():
    """USBテザリング等で割り当てられたローカルIPを取得する"""
    try:
        # ダミーの接続を作って自分のIPを確認する
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "0.0.0.0"

async def handler(websocket):
    print(f"Phone connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action")
                
                if action == "mouseMove":
                    pyautogui.moveTo(data["x"], data["y"])
                elif action == "mouseClick":
                    pyautogui.click(button=data["button"])
                elif action == "keyTap":
                    pyautogui.press(data["key"])
                elif action == "typeString":
                    pyautogui.write(data["text"])
                
                print(f"Executed command: {action}")
            except Exception as e:
                print(f"Error processing message: {e}")
    except websockets.ConnectionClosed:
        print("Phone disconnected")

async def main():
    ip = get_local_ip()
    port = 8765
    print("-" * 40)
    print(f"WebSocket Server starting...")
    print(f"Local IP address: {ip}")
    print(f"If you are using USB Tethering, use this IP in your phone app.")
    print(f"URL: ws://{ip}:{port}")
    print("-" * 40)
    
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
