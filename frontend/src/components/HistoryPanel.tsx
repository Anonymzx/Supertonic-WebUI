import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Clock,
  Trash2,
  Play,
  Download,
  RotateCcw,
  Loader2,
  Volume2,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { getHistory, deleteHistoryItem, clearHistory as clearHistoryApi } from '../api/client';
import WaveformPlayer from './WaveformPlayer';
import type { HistoryItem, HistoryResponse } from '../types';

export default function HistoryPanel() {
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedAudio, setSelectedAudio] = useState<HistoryItem | null>(null);
  const [page, setPage] = useState(1);

  const fetchHistory = useCallback(async () => {
    try {
      const data = await getHistory(page);
      setHistory(data);
    } catch (error) {
      toast.error('Failed to load history');
    } finally {
      setIsLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleDelete = useCallback(async (id: string) => {
    try {
      await deleteHistoryItem(id);
      setHistory(prev => prev ? {
        ...prev,
        items: prev.items.filter(item => item.id !== id),
        total: prev.total - 1,
      } : null);
      toast.success('Deleted from history');
    } catch {
      toast.error('Failed to delete');
    }
  }, []);

  const handleClearAll = useCallback(async () => {
    try {
      await clearHistoryApi();
      setHistory({ items: [], total: 0 });
      toast.success('History cleared');
    } catch {
      toast.error('Failed to clear history');
    }
  }, []);

  const handleCopyText = useCallback((text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Text copied');
  }, []);

  const formatDate = (isoDate: string) => {
    const date = new Date(isoDate);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);

    if (hours < 1) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 size={24} className="animate-spin text-accent-400" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">History</h1>
          <p className="text-sm text-gray-500 mt-1">
            {history?.total || 0} generations total
          </p>
        </div>
        {history && history.total > 0 && (
          <button onClick={handleClearAll} className="btn-ghost text-red-400 hover:text-red-300">
            <Trash2 size={14} />
            Clear All
          </button>
        )}
      </div>

      {!history || history.items.length === 0 ? (
        <div className="text-center py-20">
          <div className="w-16 h-16 rounded-2xl bg-dark-200 flex items-center justify-center mx-auto mb-4">
            <Clock size={28} className="text-gray-500" />
          </div>
          <p className="text-sm text-gray-500">No generation history yet</p>
          <p className="text-xs text-gray-600 mt-1">
            Generated audio files will appear here
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {history.items.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03 }}
              className="glass rounded-2xl p-4 hover:border-white/10 transition-all duration-200"
            >
              <div className="flex items-start gap-3">
                {/* Play button */}
                <button
                  onClick={() => setSelectedAudio(
                    selectedAudio?.id === item.id ? null : item
                  )}
                  className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200 ${
                    selectedAudio?.id === item.id
                      ? 'bg-accent-500 text-white'
                      : 'bg-dark-200 text-gray-400 hover:text-accent-300'
                  }`}
                >
                  {selectedAudio?.id === item.id ? (
                    <ChevronUp size={16} />
                  ) : (
                    <ChevronDown size={16} />
                  )}
                </button>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-300 line-clamp-2 mb-2">
                    {item.text}
                  </p>
                  <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
                    <span className="badge bg-dark-200">{item.voice}</span>
                    <span className="badge bg-dark-200">{item.duration_ms}ms</span>
                    <span className="badge bg-dark-200">{item.inference_ms}ms</span>
                    {item.language && (
                      <span className="badge bg-dark-200">{item.language}</span>
                    )}
                    <span className="text-gray-600">{formatDate(item.created_at)}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1 flex-shrink-0">
                  <button
                    onClick={() => handleCopyText(item.text)}
                    className="btn-ghost p-2 rounded-lg"
                    title="Copy text"
                  >
                    <RotateCcw size={14} />
                  </button>
                  <a
                    href={item.audio_url}
                    download
                    className="btn-ghost p-2 rounded-lg"
                    title="Download"
                  >
                    <Download size={14} />
                  </a>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="btn-ghost p-2 rounded-lg text-red-400 hover:text-red-300"
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              {/* Audio player (expandable) */}
              <AnimatePresence>
                {selectedAudio?.id === item.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden mt-3"
                  >
                    <WaveformPlayer
                      audioUrl={item.audio_url}
                      response={{
                        id: item.id,
                        text: item.text,
                        voice: item.voice,
                        speed: item.speed,
                        quality_steps: item.quality_steps,
                        duration_ms: item.duration_ms,
                        inference_ms: item.inference_ms,
                        audio_url: item.audio_url,
                        language: item.language,
                        created_at: item.created_at,
                      }}
                      onCopyText={handleCopyText}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
