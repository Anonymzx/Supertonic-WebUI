import { useState, useEffect, useCallback } from 'react';
import type { GenerationSettings } from '../types';

const STORAGE_KEY = 'supertonic-tts-settings';

const DEFAULT_SETTINGS: GenerationSettings = {
  voice: 'F1',
  speed: 1.0,
  qualitySteps: 32,
  language: 'na',
};

export function useSettings() {
  const [settings, setSettings] = useState<GenerationSettings>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  }, [settings]);

  const updateSetting = useCallback(<K extends keyof GenerationSettings>(
    key: K,
    value: GenerationSettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  }, []);

  return { settings, updateSetting };
}
