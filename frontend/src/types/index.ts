/** Voice information from the API */
export interface VoiceInfo {
  id: string;
  name: string;
  gender: 'female' | 'male';
  description: string;
}

/** TTS generation request */
export interface TTSRequest {
  text: string;
  voice: string;
  speed: number;
  quality_steps: number;
  language: string;
  streaming?: boolean;
}

/** Batch TTS generation request */
export interface BatchTTSRequest {
  texts: string[];
  voice: string;
  speed: number;
  quality_steps: number;
  language: string;
}

/** TTS generation response */
export interface TTSResponse {
  id: string;
  text: string;
  voice: string;
  speed: number;
  quality_steps: number;
  duration_ms: number;
  inference_ms: number;
  audio_url: string;
  language: string;
  created_at: string;
}

/** History item */
export interface HistoryItem {
  id: string;
  text: string;
  voice: string;
  speed: number;
  quality_steps: number;
  duration_ms: number;
  inference_ms: number;
  audio_url: string;
  language: string;
  created_at: string;
}

/** Paginated history response */
export interface HistoryResponse {
  items: HistoryItem[];
  total: number;
}

/** System information */
export interface SystemInfo {
  gpu_available: boolean;
  gpu_name: string;
  execution_provider: string;
  onnx_version: string;
  model_loaded: boolean;
  audio_cache_size: number;
  queue_size: number;
}

/** Voice groups */
export interface VoiceGroups {
  female: Array<{ id: string; name: string; description: string }>;
  male: Array<{ id: string; name: string; description: string }>;
}

/** Queue status */
export interface QueueStatus {
  queue_size: number;
  processing: number;
  total_enqueued: number;
  items: Record<string, number>;
}

/** Generation settings stored locally */
export interface GenerationSettings {
  voice: string;
  speed: number;
  qualitySteps: number;
  language: string;
}

/** Supported languages */
export const SUPPORTED_LANGUAGES = [
  { code: 'na', name: 'Auto Detect', flag: '🌐' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'id', name: 'Indonesian', flag: '🇮🇩' },
  { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
  { code: 'ko', name: 'Korean', flag: '🇰🇷' },
  { code: 'zh', name: 'Chinese', flag: '🇨🇳' },
  { code: 'es', name: 'Spanish', flag: '🇪🇸' },
  { code: 'fr', name: 'French', flag: '🇫🇷' },
  { code: 'de', name: 'German', flag: '🇩🇪' },
] as const;

/** Available voices */
export const AVAILABLE_VOICES: VoiceInfo[] = [
  { id: 'F1', name: 'Female Voice 1', gender: 'female', description: 'Natural female voice' },
  { id: 'F2', name: 'Female Voice 2', gender: 'female', description: 'Soft female voice' },
  { id: 'F3', name: 'Female Voice 3', gender: 'female', description: 'Bright female voice' },
  { id: 'F4', name: 'Female Voice 4', gender: 'female', description: 'Deep female voice' },
  { id: 'F5', name: 'Female Voice 5', gender: 'female', description: 'Warm female voice' },
  { id: 'M1', name: 'Male Voice 1', gender: 'male', description: 'Deep male voice' },
  { id: 'M2', name: 'Male Voice 2', gender: 'male', description: 'Natural male voice' },
  { id: 'M3', name: 'Male Voice 3', gender: 'male', description: 'Soft male voice' },
  { id: 'M4', name: 'Male Voice 4', gender: 'male', description: 'Authoritative male voice' },
  { id: 'M5', name: 'Male Voice 5', gender: 'male', description: 'Warm male voice' },
];
