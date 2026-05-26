export class WebSocketService {
  private socket: WebSocket | null = null;

  async connect(host: string): Promise<boolean> {
    return new Promise((resolve) => {
      try {
        // ws://192.168.x.x:8765 などの形式
        const url = host.startsWith('ws://') ? host : `ws://${host}:8765`;
        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
          console.log("WebSocket connected to:", url);
          resolve(true);
        };

        this.socket.onerror = (error) => {
          console.error("WebSocket error:", error);
          resolve(false);
        };

        this.socket.onclose = () => {
          console.log("WebSocket connection closed");
        };
      } catch (e) {
        console.error("Connection attempt failed:", e);
        resolve(false);
      }
    });
  }

  async disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  sendCommand(command: object) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket not connected");
    }
    this.socket.send(JSON.stringify(command));
  }

  isConnected() {
    return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
  }
}
