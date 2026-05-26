export class UsbService {
  private device: USBDevice | null = null;
  private interfaceNumber: number = 0;
  private endpointOut: number = 1; // 多くのデバイスで1がOut

  async connect() {
    try {
      if (!navigator.usb) {
        throw new Error("Web USB API not supported in this browser.");
      }
      
      // デバイスを選択（フィルタなしで全て表示）
      this.device = await navigator.usb.requestDevice({ filters: [] });
      
      await this.device.open();
      
      // デフォルトの設定を選択
      if (this.device.configuration === null) {
        await this.device.selectConfiguration(1);
      }
      
      // インターフェースを要求
      await this.device.claimInterface(this.interfaceNumber);
      
      console.log("Connected to USB device:", this.device.productName);
      return true;
    } catch (error) {
      console.error("USB connection failed:", error);
      return false;
    }
  }

  async disconnect() {
    if (this.device) {
      await this.device.releaseInterface(this.interfaceNumber);
      await this.device.close();
      this.device = null;
    }
  }

  async sendCommand(command: object) {
    if (!this.device) {
      throw new Error("USB device not connected");
    }
    const jsonStr = JSON.stringify(command) + "\n";
    const data = new TextEncoder().encode(jsonStr);
    
    // バルク転送またはインタラプト転送で送信
    await this.device.transferOut(this.endpointOut, data);
  }

  isConnected() {
    return this.device !== null && this.device.opened;
  }
}
