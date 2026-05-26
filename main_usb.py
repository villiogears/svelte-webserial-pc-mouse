import usb.core
import usb.util
import json
import pyautogui
import sys

# もし特定のデバイスに固定したい場合はここにIDを入れますが、
# 空にすると接続されているデバイスから選択できるようになります。
VENDOR_ID = None
PRODUCT_ID = None

def find_potential_devices():
    """接続されているすべてのUSBデバイスをリストアップし、ユーザーに選択させる"""
    print("Enumerating USB devices...")
    devices = list(usb.core.find(find_all=True))
    
    if not devices:
        print("No USB devices found.")
        return None

    potential_devices = []
    print("\nAvailable USB Devices:")
    for i, dev in enumerate(devices):
        try:
            manufacturer = usb.util.get_string(dev, dev.iManufacturer)
            product = usb.util.get_string(dev, dev.iProduct)
            print(f"{i}: ID {hex(dev.idVendor)}:{hex(dev.idProduct)} - {manufacturer} {product}")
            potential_devices.append(dev)
        except:
            # ドライバのパーミッション等で情報が取れないデバイスはスキップ
            continue

    if not potential_devices:
        print("Could not retrieve info for any devices. (Try running with sudo/admin)")
        return None

    selection = input("\nSelect device index to listen to (default 0): ").strip()
    idx = int(selection) if selection else 0
    return potential_devices[idx]

def process_command(line):
    # (既存のロジックと同じ)
    try:
        data = json.loads(line)
        action = data.get("action")
        
        if action == "mouseMove":
            # 画面端に移動しすぎないよう制限
            pyautogui.moveTo(data["x"], data["y"])
        elif action == "mouseClick":
            pyautogui.click(button=data["button"])
        elif action == "keyTap":
            pyautogui.press(data["key"])
        elif action == "typeString":
            pyautogui.write(data["text"])
        
        print(f"Executed: {action} with args {data}")
    except Exception as e:
        print(f"Error processing command: {e}")

def main():
    print("Searching for USB device...")
    
    # デバイスを自動検知してユーザーに選択させる
    dev = find_potential_devices()
    
    if dev is None:
        print("No suitable device selected.")
        return

    try:
        product_name = usb.util.get_string(dev, dev.iProduct)
        print(f"Connected to {product_name} (ID {hex(dev.idVendor)}:{hex(dev.idProduct)})")
    except:
        print(f"Connected to ID {hex(dev.idVendor)}:{hex(dev.idProduct)}")

    # OSからインターフェースをデタッチ（占有解除）
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    
    dev.set_configuration()
    
    # エンドポイントの取得 (WebUSBのtransferOutに対応する読み取り口)
    cfg = dev.get_active_configuration()
    intf = cfg[(0,0)]
    
    # 読み取りエンドポイント (通常は In 方向)
    ep_in = usb.util.find_descriptor(
        intf,
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN
    )

    if not ep_in:
        print("Could not find In-Endpoint.")
        return

    print("Listening for Gemini commands via USB...")
    
    buffer = ""
    try:
        while True:
            try:
                # データを読み取り (タイムアウト時は例外が発生するのでキャッチする)
                data = dev.read(ep_in.bEndpointAddress, ep_in.wMaxPacketSize, timeout=1000)
                message = "".join([chr(x) for x in data])
                buffer += message
                
                if "\n" in buffer:
                    lines = buffer.split("\n")
                    for line in lines[:-1]:
                        if line.strip():
                            process_command(line)
                    buffer = lines[-1]
            except usb.core.USBError as e:
                # タイムアウト等の微細なエラーは無視して続行
                if e.errno == 60: # MacOS timeout
                    continue
                elif "timeout" in str(e):
                    continue
                else:
                    raise e
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"USB Error: {e}")
    finally:
        usb.util.dispose_resources(dev)

if __name__ == "__main__":
    main()
