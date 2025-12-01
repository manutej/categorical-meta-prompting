/**
 * MedX Pro - Voice Capture Module
 *
 * Real-time voice transcription using Deepgram API
 * with WebSocket streaming for <500ms latency.
 */

import { TranscriptionResult, VoiceCaptureConfig } from './types';

// ============================================================================
// DEEPGRAM REAL-TIME TRANSCRIPTION
// ============================================================================

export interface TranscriptionCallbacks {
  onTranscript: (result: TranscriptionResult) => void;
  onError: (error: Error) => void;
  onClose: () => void;
}

export class DeepgramTranscriber {
  private config: VoiceCaptureConfig;
  private ws: WebSocket | null = null;
  private callbacks: TranscriptionCallbacks;
  private _isConnected = false;

  constructor(config: VoiceCaptureConfig, callbacks: TranscriptionCallbacks) {
    this.config = config;
    this.callbacks = callbacks;
  }

  get isConnected(): boolean {
    return this._isConnected;
  }

  /**
   * Connect to Deepgram WebSocket API
   */
  async connect(): Promise<void> {
    const params = new URLSearchParams({
      model: 'nova-2',
      language: this.config.language,
      punctuate: 'true',
      smart_format: 'true',
      encoding: 'linear16',
      sample_rate: String(this.config.sampleRate),
      channels: '1',
      interim_results: 'true',
      endpointing: '300'
    });

    const url = `wss://api.deepgram.com/v1/listen?${params}`;

    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);

      // Add authorization header via subprotocol workaround
      // In production, use a proxy or the Deepgram SDK
      this.ws.onopen = () => {
        console.log('[Deepgram] Connected');
        this._isConnected = true;
        resolve();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onerror = (error) => {
        console.error('[Deepgram] Error:', error);
        this.callbacks.onError(new Error('WebSocket error'));
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('[Deepgram] Disconnected');
        this._isConnected = false;
        this.callbacks.onClose();
      };
    });
  }

  private handleMessage(data: string): void {
    try {
      const msg = JSON.parse(data);

      if (msg.type === 'Results' && msg.channel?.alternatives?.[0]) {
        const alt = msg.channel.alternatives[0];
        const transcript = alt.transcript?.trim();

        if (transcript) {
          this.callbacks.onTranscript({
            text: transcript,
            confidence: alt.confidence || 0.9,
            language: this.config.language,
            isFinal: msg.is_final || false,
            timestamp: Date.now()
          });
        }
      }
    } catch (e) {
      console.error('[Deepgram] Parse error:', e);
    }
  }

  /**
   * Send audio chunk
   */
  sendAudio(audioData: ArrayBuffer): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(audioData);
    }
  }

  /**
   * Disconnect
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this._isConnected = false;
  }
}

// ============================================================================
// BROWSER MICROPHONE CAPTURE
// ============================================================================

export class MicrophoneCapture {
  private stream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private onAudioData: (data: ArrayBuffer) => void;

  constructor(onAudioData: (data: ArrayBuffer) => void) {
    this.onAudioData = onAudioData;
  }

  /**
   * Start capturing from microphone
   */
  async start(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      this.audioContext = new AudioContext({ sampleRate: 16000 });
      const source = this.audioContext.createMediaStreamSource(this.stream);
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      this.processor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0);
        const audioBuffer = this.convertToInt16(inputData);
        this.onAudioData(audioBuffer.buffer as ArrayBuffer);
      };

      source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);

      console.log('[Microphone] Started');
    } catch (error) {
      console.error('[Microphone] Error:', error);
      throw error;
    }
  }

  private convertToInt16(float32: Float32Array): Int16Array {
    const int16 = new Int16Array(float32.length);
    for (let i = 0; i < float32.length; i++) {
      const s = Math.max(-1, Math.min(1, float32[i]));
      int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16;
  }

  /**
   * Stop capturing
   */
  stop(): void {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.stream) {
      this.stream.getTracks().forEach(t => t.stop());
      this.stream = null;
    }
    console.log('[Microphone] Stopped');
  }
}

// ============================================================================
// SIMULATED TRANSCRIBER (for testing without API key)
// ============================================================================

export class SimulatedTranscriber {
  private callbacks: TranscriptionCallbacks;
  private _isConnected = false;
  private testPhrases = [
    'Paciente masculino de 55 años',
    'Presenta hipertensión y diabetes tipo 2',
    'Toma metformina 500 mg dos veces al día',
    'Presión arterial 140/90 mmHg',
    'Frecuencia cardíaca 78 lpm',
    'Plan: continuar tratamiento actual',
    'Solicitar electrocardiograma'
  ];
  private phraseIndex = 0;

  constructor(callbacks: TranscriptionCallbacks) {
    this.callbacks = callbacks;
  }

  get isConnected(): boolean {
    return this._isConnected;
  }

  async connect(): Promise<void> {
    this._isConnected = true;
    console.log('[Simulated] Connected');
  }

  /**
   * Simulate receiving a transcription
   */
  simulateTranscription(text?: string): void {
    const transcript = text || this.testPhrases[this.phraseIndex % this.testPhrases.length];
    this.phraseIndex++;

    this.callbacks.onTranscript({
      text: transcript,
      confidence: 0.95,
      language: 'es-MX',
      isFinal: true,
      timestamp: Date.now()
    });
  }

  disconnect(): void {
    this._isConnected = false;
    this.callbacks.onClose();
  }
}

// ============================================================================
// FACTORY
// ============================================================================

export function createVoiceCapture(
  apiKey: string | null,
  callbacks: TranscriptionCallbacks,
  language: 'es-MX' | 'es-ES' | 'en-US' = 'es-MX'
): DeepgramTranscriber | SimulatedTranscriber {

  if (!apiKey) {
    console.log('[VoiceCapture] No API key - using simulator');
    return new SimulatedTranscriber(callbacks);
  }

  return new DeepgramTranscriber(
    { apiKey, language, sampleRate: 16000 },
    callbacks
  );
}
