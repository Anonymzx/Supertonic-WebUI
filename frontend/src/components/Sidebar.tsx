import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  History,
  Settings,
  Download,
  Info,
  Menu,
  X,
  ChevronLeft,
  Music4,
  Zap,
  Cpu,
} from 'lucide-react';
import type { SystemInfo } from '../types';

interface SidebarProps {
  activeTab: 'generate' | 'history' | 'settings';
  onTabChange: (tab: 'generate' | 'history' | 'settings') => void;
  isOpen: boolean;
  onToggle: () => void;
  systemInfo: SystemInfo | null;
}

const navItems = [
  { id: 'generate' as const, label: 'Generate', icon: Sparkles },
  { id: 'history' as const, label: 'History', icon: History },
  { id: 'settings' as const, label: 'Settings', icon: Settings },
];

export default function Sidebar({
  activeTab,
  onTabChange,
  isOpen,
  onToggle,
  systemInfo,
}: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
            onClick={onToggle}
          />
        )}
      </AnimatePresence>

      {/* Mobile toggle */}
      <button
        onClick={onToggle}
        className="fixed top-4 left-4 z-50 lg:hidden btn-ghost p-2.5 rounded-xl glass"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          width: isOpen ? 280 : 72,
          x: 0,
        }}
        className={`
          fixed lg:relative z-50 h-screen
          bg-dark-200/90 backdrop-blur-xl border-r border-white/5
          flex flex-col overflow-hidden
          ${isOpen ? 'left-0' : '-left-full lg:left-0'}
          transition-[left] duration-300 lg:transition-none
        `}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 p-5 border-b border-white/5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-500 to-purple-600 flex items-center justify-center flex-shrink-0">
            <Music4 size={20} className="text-white" />
          </div>
          <AnimatePresence>
            {isOpen && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="overflow-hidden whitespace-nowrap"
              >
                <h1 className="font-semibold text-sm text-white">Supertonic</h1>
                <p className="text-[10px] text-gray-500">AI Voice Studio</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => onTabChange(id)}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 rounded-xl
                transition-all duration-200 text-sm font-medium
                ${activeTab === id
                  ? 'bg-accent-500/15 text-accent-300 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                }
              `}
            >
              <Icon size={18} className="flex-shrink-0" />
              <AnimatePresence>
                {isOpen && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    className="overflow-hidden whitespace-nowrap"
                  >
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          ))}
        </nav>

        {/* System Info */}
        {systemInfo && (
          <div className="p-4 border-t border-white/5">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-[11px] text-gray-500">
                <Cpu size={12} />
                <span className={isOpen ? '' : 'hidden'}>
                  {systemInfo.execution_provider || 'CPU'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-gray-500">
                <Zap size={12} className={systemInfo.gpu_available ? 'text-green-400' : 'text-yellow-400'} />
                <span className={isOpen ? '' : 'hidden'}>
                  {systemInfo.gpu_available ? 'GPU' : 'CPU'} Mode
                </span>
              </div>
              <div className="flex items-center gap-2 text-[11px] text-gray-500">
                <div className={`w-2 h-2 rounded-full ${systemInfo.model_loaded ? 'bg-green-400' : 'bg-yellow-400'}`} />
                <span className={isOpen ? '' : 'hidden'}>
                  {systemInfo.model_loaded ? 'Model Ready' : 'No Model'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Collapse button */}
        <button
          onClick={onToggle}
          className="hidden lg:flex items-center justify-center p-3 border-t border-white/5 hover:bg-white/5 transition-colors"
        >
          <ChevronLeft
            size={16}
            className={`text-gray-500 transition-transform ${!isOpen ? 'rotate-180' : ''}`}
          />
        </button>
      </motion.aside>
    </>
  );
}
