import { motion, AnimatePresence } from 'framer-motion';
import { Volume2, ChevronDown, Check, Mic2 } from 'lucide-react';
import { useState } from 'react';
import type { VoiceInfo } from '../types';

interface VoiceSelectorProps {
  voices: VoiceInfo[];
  selectedVoice: string;
  onSelect: (voiceId: string) => void;
  compact?: boolean;
}

export default function VoiceSelector({
  voices,
  selectedVoice,
  onSelect,
  compact = false,
}: VoiceSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const femaleVoices = voices.filter(v => v.gender === 'female');
  const maleVoices = voices.filter(v => v.gender === 'male');
  const currentVoice = voices.find(v => v.id === selectedVoice);

  if (compact) {
    // Compact mode for sidebar/inline display
    return (
      <div className="space-y-2">
        {voices.map((voice) => (
          <button
            key={voice.id}
            onClick={() => onSelect(voice.id)}
            className={`
              w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left
              transition-all duration-200 text-sm
              ${selectedVoice === voice.id
                ? 'bg-accent-500/15 text-accent-300 border border-accent-500/30'
                : 'text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-transparent'
              }
            `}
          >
            <div className={`
              w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold
              ${voice.gender === 'female'
                ? 'bg-pink-500/20 text-pink-400'
                : 'bg-blue-500/20 text-blue-400'
              }
            `}>
              {voice.id}
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-medium truncate">{voice.name}</div>
              <div className="text-[11px] text-gray-500 truncate">{voice.description}</div>
            </div>
            {selectedVoice === voice.id && (
              <Check size={14} className="text-accent-400 flex-shrink-0" />
            )}
          </button>
        ))}
      </div>
    );
  }

  // Full dropdown mode
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-dark-200 border border-white/5
                   hover:border-white/10 transition-all duration-200 text-left"
      >
        <div className={`
          w-9 h-9 rounded-lg flex items-center justify-center text-xs font-bold
          ${currentVoice?.gender === 'female'
            ? 'bg-pink-500/20 text-pink-400'
            : 'bg-blue-500/20 text-blue-400'
          }
        `}>
          {selectedVoice}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-gray-200 truncate">
            {currentVoice?.name || 'Select Voice'}
          </div>
          <div className="text-xs text-gray-500 truncate">
            {currentVoice?.description || 'Choose a voice'}
          </div>
        </div>
        <ChevronDown
          size={16}
          className={`text-gray-500 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, y: -8, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.95 }}
              className="absolute left-0 right-0 top-full mt-2 z-20 glass rounded-2xl p-2 max-h-80 overflow-y-auto shadow-2xl"
            >
              {/* Female voices */}
              <div className="mb-2">
                <div className="px-3 py-1.5 text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                  Female Voices
                </div>
                {femaleVoices.map((voice) => (
                  <VoiceOption
                    key={voice.id}
                    voice={voice}
                    isSelected={selectedVoice === voice.id}
                    onSelect={() => {
                      onSelect(voice.id);
                      setIsOpen(false);
                    }}
                  />
                ))}
              </div>

              {/* Male voices */}
              <div>
                <div className="px-3 py-1.5 text-[10px] font-medium text-gray-500 uppercase tracking-wider">
                  Male Voices
                </div>
                {maleVoices.map((voice) => (
                  <VoiceOption
                    key={voice.id}
                    voice={voice}
                    isSelected={selectedVoice === voice.id}
                    onSelect={() => {
                      onSelect(voice.id);
                      setIsOpen(false);
                    }}
                  />
                ))}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}

function VoiceOption({
  voice,
  isSelected,
  onSelect,
}: {
  voice: VoiceInfo;
  isSelected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={`
        w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left
        transition-all duration-200
        ${isSelected
          ? 'bg-accent-500/15 text-accent-300'
          : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
        }
      `}
    >
      <div className={`
        w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0
        ${voice.gender === 'female'
          ? 'bg-pink-500/20 text-pink-400'
          : 'bg-blue-500/20 text-blue-400'
        }
      `}>
        {voice.id}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium truncate">{voice.name}</div>
        <div className="text-xs text-gray-500 truncate">{voice.description}</div>
      </div>
      {isSelected && <Check size={14} className="text-accent-400 flex-shrink-0" />}
    </button>
  );
}
