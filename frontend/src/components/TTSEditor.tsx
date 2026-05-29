import { useState, useCallback, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  Send,
  Loader2,
  StopCircle,
  AlignLeft,
  Volume2,
  Sliders,
  Globe,
  Zap,
  Play,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { generateTTS } from '../api/client';
import VoiceSelector from './VoiceSelector';
import WaveformPlayer from './WaveformPlayer';
import type { VoiceInfo, TTSResponse, GenerationSettings } from '../types';
import { SUPPORTED_LANGUAGES } from '../types';

interface TTSEditorProps {
  voices: VoiceInfo[];
  settings: GenerationSettings;
  onUpdateSetting: <K extends keyof GenerationSettings>(key: K, value: GenerationSettings[K]) => void;
}

export default function TTSEditor({ voices, settings, onUpdateSetting }: TTSEditorProps) {
  const [text, setText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [response, setResponse] = useState<TTSResponse | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [text]);

  const handleGenerate = useCallback(async () => {
    const trimmedText = text.trim();
    if (!trimmedText) {
      toast.error('Please enter some text to generate');
      return;
    }

    if (trimmedText.length < 3) {
      toast.error('Text must be at least 3 characters');
      return;
    }

    setIsGenerating(true);
    setAudioUrl(null);
    setResponse(null);

    try {
      const result = await generateTTS({
        text: trimmedText,
        voice: settings.voice,
        speed: settings.speed,
        quality_steps: settings.qualitySteps,
        language: settings.language,
      });

      setAudioUrl(result.audio_url);
      setResponse(result);
      toast.success(`Generated ${result.duration_ms}ms audio in ${result.inference_ms}ms`);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Generation failed';
      toast.error(message);
    } finally {
      setIsGenerating(false);
    }
  }, [text, settings]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      // Ctrl+Enter to generate
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleGenerate();
      }
    },
    [handleGenerate]
  );

  const handleCopyText = useCallback((textToCopy: string) => {
    navigator.clipboard.writeText(textToCopy);
    toast.success('Text copied to clipboard');
  }, []);

  const characterCount = text.length;
  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Text to Speech</h1>
        <p className="text-sm text-gray-500 mt-1">
          Transform your text into natural-sounding speech
        </p>
      </div>

      {/* Voice selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <label className="label">Voice</label>
          <VoiceSelector
            voices={voices}
            selectedVoice={settings.voice}
            onSelect={(voice) => onUpdateSetting('voice', voice)}
          />
        </div>

        {/* Language selector */}
        <div>
          <label className="label">Language</label>
          <select
            value={settings.language}
            onChange={(e) => onUpdateSetting('language', e.target.value)}
            className="input-field"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.flag} {lang.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Parameters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Speed slider */}
        <div>
          <label className="label">
            Speed: {settings.speed.toFixed(1)}x
          </label>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.1"
            value={settings.speed}
            onChange={(e) => onUpdateSetting('speed', parseFloat(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-[10px] text-gray-500 mt-1">
            <span>0.5x</span>
            <span>1.0x</span>
            <span>2.0x</span>
          </div>
        </div>

        {/* Quality steps */}
        <div>
          <label className="label">
            Quality: {settings.qualitySteps} steps
          </label>
          <input
            type="range"
            min="8"
            max="64"
            step="8"
            value={settings.qualitySteps}
            onChange={(e) => onUpdateSetting('qualitySteps', parseInt(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-[10px] text-gray-500 mt-1">
            <span>Draft</span>
            <span>Standard</span>
            <span>Premium</span>
          </div>
        </div>
      </div>

      {/* Text input */}
      <div className="relative">
        <label className="label">Text to synthesize</label>
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter the text you want to convert to speech...&#10;&#10;Supported expression tags:&#10;<laugh> <breath> <sigh>"
            className="input-field min-h-[160px] py-4 pr-20"
            rows={5}
            maxLength={5000}
          />
          <div className="absolute bottom-3 right-3 text-[10px] text-gray-500 text-right">
            <div>{characterCount}/5000</div>
            <div>{wordCount} words</div>
          </div>
        </div>

        {/* Tags hint */}
        <div className="flex flex-wrap gap-2 mt-3">
          <button
            onClick={() => setText(prev => prev + '<laugh> ')}
            className="tag"
            type="button"
          >
            {'<laugh>'}
          </button>
          <button
            onClick={() => setText(prev => prev + '<breath> ')}
            className="tag"
            type="button"
          >
            {'<breath>'}
          </button>
          <button
            onClick={() => setText(prev => prev + '<sigh> ')}
            className="tag"
            type="button"
          >
            {'<sigh>'}
          </button>
        </div>
      </div>

      {/* Generate button */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !text.trim()}
          className="btn-primary px-8 py-3 text-base"
        >
          {isGenerating ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles size={18} />
              Generate Speech
            </>
          )}
        </button>

        {isGenerating && (
          <button
            onClick={() => {
              // Abort generation (handled by timeout)
              setIsGenerating(false);
              toast('Generation cancelled');
            }}
            className="btn-secondary"
          >
            <StopCircle size={16} />
            Cancel
          </button>
        )}

        <span className="text-[11px] text-gray-500 ml-auto">
          Ctrl+Enter to generate
        </span>
      </div>

      {/* Audio player */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={audioUrl ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.3 }}
      >
        {audioUrl && response && (
          <WaveformPlayer
            audioUrl={audioUrl}
            response={response}
            onClose={() => {
              setAudioUrl(null);
              setResponse(null);
            }}
            onCopyText={handleCopyText}
          />
        )}
      </motion.div>

      {/* Empty state */}
      {!audioUrl && !isGenerating && (
        <div className="text-center py-12">
          <div className="w-16 h-16 rounded-2xl bg-dark-200 flex items-center justify-center mx-auto mb-4">
            <Volume2 size={28} className="text-gray-500" />
          </div>
          <p className="text-sm text-gray-500">
            Enter text above and click Generate to create speech
          </p>
          <p className="text-xs text-gray-600 mt-1">
            Use Ctrl+Enter for quick generation
          </p>
        </div>
      )}

      {/* Loading skeleton */}
      {isGenerating && (
        <div className="glass rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-dark-200 animate-pulse" />
            <div className="space-y-2 flex-1">
              <div className="h-3 bg-dark-200 rounded animate-pulse w-1/3" />
              <div className="h-2 bg-dark-200 rounded animate-pulse w-1/4" />
            </div>
          </div>
          <div className="h-16 bg-dark-200 rounded-xl animate-pulse" />
          <div className="flex gap-2">
            <div className="h-6 bg-dark-200 rounded w-20 animate-pulse" />
            <div className="h-6 bg-dark-200 rounded w-24 animate-pulse" />
          </div>
        </div>
      )}
    </div>
  );
}
