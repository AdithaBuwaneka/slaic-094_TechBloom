import { API_CONFIG } from '../api/config';

type VoiceClientEvents = {
  onReady?: () => void;
  onPartial?: (text: string) => void;
  onFinal?: (text: string) => void;
  onTTSChunk?: (opusBase64: string) => void;
  onTTSEnd?: () => void;
  onError?: (message: string) => void;
};

export class VoiceClient {
  private ws?: WebSocket;
  private url: string;
  private token?: string;
  private language: string;
  private sampleRate: number;
  private events: VoiceClientEvents;

  constructor(params: { token?: string; language?: string; sampleRate?: number; events?: VoiceClientEvents }) {
    const { token, language = 'en-US', sampleRate = 16000, events = {} } = params;
    const baseHttp = API_CONFIG.BASE_URL; // e.g., http://10.0.2.2:8000
    const scheme = baseHttp.startsWith('https') ? 'wss' : 'ws';
    const host = baseHttp.replace(/^https?:\/\//, '');
    this.url = `${scheme}://${host}${API_CONFIG.API_VERSION}/ws/voice?token=${encodeURIComponent(token || '')}&language=${encodeURIComponent(language)}&sample_rate=${sampleRate}`;
    this.token = token;
    this.language = language;
    this.sampleRate = sampleRate;
    this.events = events;
  }

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => {};
    this.ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        const type = data?.type;
        if (type === 'ready') this.events.onReady?.();
        else if (type === 'partial') this.events.onPartial?.(data.text || '');
        else if (type === 'final') this.events.onFinal?.(data.text || '');
        else if (type === 'tts_chunk') this.events.onTTSChunk?.(data.data || '');
        else if (type === 'tts_end') this.events.onTTSEnd?.();
        else if (type === 'error') this.events.onError?.(data.message || 'Unknown error');
      } catch (_) {
        // ignore non-JSON (we don't expect binary text from server)
      }
    };
    this.ws.onerror = () => {
      this.events.onError?.('WebSocket error');
    };
    this.ws.onclose = () => {};
  }

  sendPCM16(pcm: ArrayBuffer) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(pcm);
    }
  }

  stop() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'stop' }));
    }
    this.ws?.close();
  }
}


