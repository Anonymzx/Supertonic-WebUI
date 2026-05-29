import { useEffect, useRef, useState, useCallback } from 'react';
import {
  Play,
  Pause,
  Download,
  Copy,
  Clock,
  Zap,
  Trash2,
  Volume2,
} from 'lucide-react';
import type { TTSResponse } from '../types';

interface WaveformPlayerProps {
  audioUrl: string | null;
  response: TTSResponse | null;
  onClose?: () => void;
  onCopyText?: (text: string) => void;
}

export default function WaveformPlayer({
  audioUrl,
  response,
  onClose,
  onCopyText,
}: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const wavesurferRef = useRef<any>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize audio player
  useEffect(() => {
    if (!audioUrl) return;

    setIsLoading(true);

    // Create audio element
    const audio = new Audio(audioUrl);
    audio.volume = volume;
    audioRef.current = audio;

    const onLoaded = () => {
      setDuration(audio.duration);
      setIsLoading(false);
    };

    const onTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const onEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    audio.addEventListener('loadedmetadata', onLoaded);
    audio.addEventListener('timeupdate', onTimeUpdate);
    audio.addEventListener('ended', onEnded);

    // Cleanup
    return () => {
      audio.pause();
      audio.removeEventListener('loadedmetadata', onLoaded);
      audio.removeEventListener('timeupdate', onTimeUpdate);
      audio.removeEventListener('ended', onEnded);
      audioRef.current = null;
    };
  }, [audioUrl]);

  // Update volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  const togglePlay = useCallback(() => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const handleDownload = useCallback(() => {
    if (!audioUrl) return;
    const a = document.createElement('a');
    a.href = audioUrl;
    a.download = `supertonic-${Date.now()}.wav`;
    a.click();
  }, [audioUrl]);

  const handleCopyText = useCallback(() => {
    if (response?.text && onCopyText) {
      onCopyText(response.text);
    }
  }, [response, onCopyText]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!audioUrl || !response) return null;

  return (
    <div className="glass rounded-2xl p-5 space-y-4 animate-[fadeIn_0.3s_ease-out]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Volume2 size={16} className="text-accent-400" />
          <span className="text-sm font-medium text-gray-200">Generated Audio</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleCopyText}
            className="btn-ghost p-2 rounded-lg"
            title="Copy text"
          >
            <Copy size={14} />
          </button>
          <button
            onClick={handleDownload}
            className="btn-ghost p-2 rounded-lg"
            title="Download audio"
          >
            <Download size={14} />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="btn-ghost p-2 rounded-lg"
              title="Close"
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
      </div>

      {/* Simple waveform visualization */}
      <div
        ref={containerRef}
        className="h-16 rounded-xl bg-dark-200/50 flex items-center justify-center overflow-hidden"
      >
        {isLoading ? (
          <div className="flex items-center gap-1">
            {[...Array(32)].map((_, i) => (
              <div
                key={i}
                className="w-1 bg-accent-500/30 rounded-full animate-pulse"
                style={{
                  height: `${Math.random() * 40 + 10}px`,
                  animationDelay: `${i * 0.05}s`,
                }}
              />
            ))}
          </div>
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            {/* Waveform bars */}
            <div className="flex items-center gap-[2px] w-full px-2">
              {[...Array(48)].map((_, i) => {
                const isActive = (i / 48) * duration <= currentTime;
                return (
                  <div
                    key={i}
                    className={`flex-1 rounded-full transition-colors duration-100 ${
                      isActive ? 'bg-accent-500' : 'bg-dark-100'
                    }`}
                    style={{
                      height: `${Math.sin(i * 0.5) * 20 + 25}px`,
                      opacity: isActive ? 1 : 0.5,
                    }}
                  />
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        <button
          onClick={togglePlay}
          disabled={isLoading}
          className="w-10 h-10 rounded-full bg-accent-500 hover:bg-accent-600 
                     flex items-center justify-center transition-all duration-200
                     disabled:opacity-50 disabled:cursor-not-allowed
                     shadow-lg shadow-accent-500/25"
        >
          {isPlaying ? <Pause size={18} /> : <Play size={18} className="ml-0.5" />}
        </button>

        {/* Time */}
        <div className="flex items-center gap-2 text-xs text-gray-500 font-mono">
          <span>{formatTime(currentTime)}</span>
          <span className="text-gray-600">/</span>
          <span>{formatTime(duration)}</span>
        </div>

        {/* Volume slider */}
        <div className="flex items-center gap-2 ml-auto">
          <Volume2 size={14} className="text-gray-500" />
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
            className="w-20"
          />
        </div>
      </div>

      {/* Metadata */}
      <div className="flex flex-wrap gap-3 text-xs text-gray-500">
        <div className="flex items-center gap-1.5 badge bg-dark-200">
          <Clock size={10} />
          {response.duration_ms}ms
        </div>
        <div className="flex items-center gap-1.5 badge bg-dark-200">
          <Zap size={10} />
          {response.inference_ms}ms inference
        </div>
        <div className="flex items-center gap-1.5 badge bg-dark-200">
          Voice: {response.voice}
        </div>
        {response.language && (
          <div className="flex items-center gap-1.5 badge bg-dark-200">
            {response.language}
          </div>
        )}
      </div>
    </div>
  );
}
