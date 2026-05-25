export class SerialService {
  private port: SerialPort | null = null;
  private writer: WritableStreamDefaultWriter<string> | null = null;
  private encoder = new TextEncoder();

  async connect() {
    try {
      this.port = await navigator.serial.requestPort();
      await this.port.open({ baudRate: 115200 });
      
      const textEncoder = new TextEncoderStream();
      textEncoder.readable.pipeTo(this.port.writable!);
      this.writer = textEncoder.writable.getWriter();
      
      return true;
    } catch (error) {
      console.error("Serial connection failed:", error);
      return false;
    }
  }

  async disconnect() {
    if (this.writer) {
      await this.writer.close();
      this.writer = null;
    }
    if (this.port) {
      await this.port.close();
      this.port = null;
    }
  }

  async sendCommand(command: object) {
    if (!this.writer) {
      throw new Error("Serial port not connected");
    }
    const jsonStr = JSON.stringify(command) + "\n";
    await this.writer.write(jsonStr);
  }

  isConnected() {
    return this.port !== null;
  }
}
