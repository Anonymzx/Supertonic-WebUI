/**
 * Supertonic TTS WebUI - API Client
 * Axios-based HTTP client for the backend API.
 */
import axios, { AxiosError } from 'axios';
import type {
  TTSRequest,
  TTSResponse,
  BatchTTSRequest,
  VoiceInfo,
  HistoryResponse,
  SystemInfo,
  QueueStatus,
} from '../types';

const API_BASE = '/api';

// Create Axios instance with defaults
const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes for TTS generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error: string; detail?: string }>) => {
    const message = error.response?.data?.detail
      || error.response?.data?.error
      || error.message
      || 'An unexpected error occurred';
    return Promise.reject(new Error(message));
  }
);

/**
 * Generate speech from text.
 */
export async function generateTTS(request: TTSRequest): Promise<TTSResponse> {
  const { data } = await api.post<TTSResponse>('/tts', request);
  return data;
}

/**
 * Generate speech with streaming response.
 * Returns the audio blob directly.
 */
export async function generateTTSStreaming(request: TTSRequest): Promise<Blob> {
  const response = await api.post('/tts/stream', request, {
    responseType: 'blob',
    timeout: 180000,
  });
  return response.data;
}

/**
 * Batch generate speech for multiple texts.
 */
export async function generateBatchTTS(request: BatchTTSRequest): Promise<{ items: TTSResponse[]; total: number }> {
  const { data } = await api.post('/tts/batch', request);
  return data;
}

/**
 * Get all available voices.
 */
export async function getVoices(): Promise<VoiceInfo[]> {
  const { data } = await api.get<VoiceInfo[]>('/voices');
  return data;
}

/**
 * Get voice groups.
 */
export async function getVoiceGroups(): Promise<{ female: VoiceInfo[]; male: VoiceInfo[] }> {
  const { data } = await api.get('/voices/groups/grouped');
  return data;
}

/**
 * Get generation history.
 */
export async function getHistory(page = 1, perPage = 20): Promise<HistoryResponse> {
  const { data } = await api.get<HistoryResponse>('/history', {
    params: { page, per_page: perPage },
  });
  return data;
}

/**
 * Delete a history item.
 */
export async function deleteHistoryItem(id: string): Promise<void> {
  await api.delete(`/history/${id}`);
}

/**
 * Clear all history.
 */
export async function clearHistory(): Promise<void> {
  await api.delete('/history');
}

/**
 * Get history statistics.
 */
export async function getHistoryStats(): Promise<Record<string, unknown>> {
  const { data } = await api.get('/history/stats');
  return data;
}

/**
 * Get system information.
 */
export async function getSystemInfo(): Promise<SystemInfo> {
  const { data } = await api.get<SystemInfo>('/system/info');
  return data;
}

/**
 * Get available execution providers.
 */
export async function getProviders(): Promise<{ providers: string[]; provider_info: Record<string, unknown> }> {
  const { data } = await api.get('/system/providers');
  return data;
}

/**
 * Get queue status.
 */
export async function getQueueStatus(): Promise<QueueStatus> {
  const { data } = await api.get<QueueStatus>('/system/queue');
  return data;
}

/**
 * Load the TTS model.
 */
export async function loadModel(): Promise<{ message: string; status: string }> {
  const { data } = await api.post('/model/load');
  return data;
}

/**
 * Start downloading the model.
 */
export async function downloadModel(): Promise<{ message: string; status: string }> {
  const { data } = await api.post('/model/download');
  return data;
}

/**
 * Get model status.
 */
export async function getModelStatus(): Promise<{ loaded: boolean; model_info: Record<string, unknown> }> {
  const { data } = await api.get('/model/status');
  return data;
}

/**
 * Health check.
 */
export async function healthCheck(): Promise<{ status: string; model_loaded: boolean; gpu_available: boolean }> {
  const { data } = await api.get('/health');
  return data;
}

export default api;
