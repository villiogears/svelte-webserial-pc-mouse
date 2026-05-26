<script lang="ts">
  import { onMount } from 'svelte';
  import { GeminiService } from './lib/gemini';
  import { UsbService } from './lib/usb';

  let apiKey = $state(localStorage.getItem('gemini_api_key') || '');
  let prompt = $state('');
  let logs = $state<{type: 'info' | 'error' | 'command', message: string}[]>([]);
  let isConnected = $state(false);
  let isProcessing = $state(false);

  const usb = new UsbService();
  let gemini: GeminiService | null = null;

  $effect(() => {
    localStorage.setItem('gemini_api_key', apiKey);
    if (apiKey) {
      gemini = new GeminiService(apiKey);
    }
  });

  function addLog(type: 'info' | 'error' | 'command', message: string) {
    logs = [...logs, { type, message }];
    // Keep only last 50 logs
    if (logs.length > 50) logs = logs.slice(-50);
  }

  async function handleConnect() {
    const success = await usb.connect();
    if (success) {
      isConnected = true;
      addLog('info', 'USB device connected');
    } else {
      addLog('error', 'Failed to connect to USB device');
    }
  }

  async function handleDisconnect() {
    await usb.disconnect();
    isConnected = false;
    addLog('info', 'USB device disconnected');
  }

  async function handleSubmit() {
    if (!gemini || !prompt) return;
    if (!isConnected) {
      addLog('error', 'Please connect USB device first');
      return;
    }

    isProcessing = true;
    addLog('info', `Gemini is thinking: ${prompt}`);
    
    try {
      const result = await gemini.processPrompt(prompt);
      addLog('info', `Gemini says: ${result.text}`);
      
      for (const call of result.calls) {
        addLog('command', `Sending command: ${call.name}(${JSON.stringify(call.args)})`);
        await usb.sendCommand({
          action: call.name,
          ...call.args
        });
      }
      prompt = '';
    } catch (error: any) {
      addLog('error', `Error: ${error.message}`);
    } finally {
      isProcessing = false;
    }
  }
</script>

<main class="container">
  <h1>Gemini Mirroring (PC Control)</h1>

  <section class="config">
    <div class="field">
      <label for="api-key">Gemini API Key</label>
      <input type="password" id="api-key" bind:value={apiKey} placeholder="Enter your API Key" />
    </div>

    <div class="actions">
      {#if !isConnected}
        <button onclick={handleConnect}>Connect USB</button>
      {:else}
        <button class="secondary" onclick={handleDisconnect}>Disconnect USB</button>
        <span class="status-badge connected">Connected</span>
      {/if}
    </div>
  </section>

  <section class="chat">
    <div class="input-group">
      <input 
        type="text" 
        bind:value={prompt} 
        placeholder="e.g., Open Notepad and type HelloWorld"
        onkeydown={(e) => e.key === 'Enter' && handleSubmit()}
        disabled={isProcessing || !isConnected}
      />
      <button onclick={handleSubmit} disabled={isProcessing || !isConnected || !prompt}>
        {isProcessing ? 'Thinking...' : 'Send'}
      </button>
    </div>
  </section>

  <section class="logs">
    <div class="log-header">
      <h2>Activity Log</h2>
      <button class="text-btn" onclick={() => logs = []}>Clear</button>
    </div>
    <div class="log-window">
      {#each logs as log}
        <div class="log-entry {log.type}">
          <span class="timestamp">[{new Date().toLocaleTimeString()}]</span>
          <span class="message">{log.message}</span>
        </div>
      {/each}
      {#if logs.length === 0}
        <p class="empty-log">Connecting to a device to see activity...</p>
      {/if}
    </div>
  </section>
</main>

<style>
  :global(body) {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  .container {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  h1 {
    font-size: 1.5rem;
    text-align: center;
    color: #38bdf8;
    margin: 0;
  }

  section {
    background: #1e293b;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  label {
    font-size: 0.875rem;
    color: #94a3b8;
  }

  input {
    background: #0f172a;
    border: 1px solid #334155;
    color: white;
    padding: 0.75rem;
    border-radius: 8px;
    font-size: 1rem;
  }

  button {
    background: #0ea5e9;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  button:hover:not(:disabled) {
    background: #0284c7;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  button.secondary {
    background: #334155;
  }

  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .status-badge.connected {
    background: #064e3b;
    color: #34d399;
    border: 1px solid #059669;
  }

  .input-group {
    display: flex;
    gap: 0.5rem;
  }

  .input-group input {
    flex: 1;
  }

  .log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  h2 {
    font-size: 1rem;
    margin: 0;
    color: #94a3b8;
  }

  .text-btn {
    background: none;
    color: #64748b;
    font-size: 0.75rem;
    padding: 0.25rem;
  }

  .log-window {
    height: 300px;
    overflow-y: auto;
    background: #0f172a;
    border-radius: 8px;
    padding: 0.5rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.85rem;
  }

  .log-entry {
    margin-bottom: 0.25rem;
    line-height: 1.4;
    word-break: break-all;
  }

  .timestamp {
    color: #475569;
    margin-right: 0.5rem;
  }

  .info { color: #94a3b8; }
  .error { color: #f87171; }
  .command { color: #fbbf24; }

  .empty-log {
    text-align: center;
    color: #475569;
    margin-top: 2rem;
  }
</style>
