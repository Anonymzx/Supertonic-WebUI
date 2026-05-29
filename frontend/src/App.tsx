import { useState, useEffect, useCallback } from 'react';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import TTSEditor from './components/TTSEditor';
import HistoryPanel from './components/HistoryPanel';
import SettingsPanel from './components/SettingsPanel';
import { useSettings } from './hooks/useSettings';
import { getSystemInfo, getVoices } from './api/client';
import type { VoiceInfo, SystemInfo } from './types';

export default function App() {
  const [activeTab, setActiveTab] = useState<'generate' | 'history' | 'settings'>('generate');
  const [sidebarOpen, setSidebarOpen] = useState(window.innerWidth >= 1024);
  const [voices, setVoices] = useState<VoiceInfo[]>([]);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const { settings, updateSetting } = useSettings();

  // Fetch system info and voices on mount
  useEffect(() => {
    const init = async () => {
      try {
        const [fetchedVoices, info] = await Promise.all([
          getVoices(),
          getSystemInfo(),
        ]);
        setVoices(fetchedVoices);
        setSystemInfo(info);
      } catch {
        // Use default voices if API fails
        setVoices([
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
        ]);
      }
    };
    init();
  }, []);

  // Handle window resize for sidebar
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(true);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Alt+1: Generate tab, Alt+2: History tab, Alt+3: Settings tab
      if (e.altKey) {
        switch (e.key) {
          case '1': setActiveTab('generate'); break;
          case '2': setActiveTab('history'); break;
          case '3': setActiveTab('settings'); break;
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-dark-300">
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1e1e2e',
            color: '#e2e8f0',
            border: '1px solid rgba(255,255,255,0.05)',
            borderRadius: '12px',
            fontSize: '14px',
          },
          success: {
            iconTheme: { primary: '#6c28d9', secondary: '#fff' },
          },
          error: {
            iconTheme: { primary: '#ef4444', secondary: '#fff' },
          },
        }}
      />

      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
        systemInfo={systemInfo}
      />

      {/* Main content */}
      <main className="flex-1 overflow-y-auto p-4 lg:p-8 pt-16 lg:pt-8">
        <div className="max-w-5xl mx-auto">
          {activeTab === 'generate' && (
            <TTSEditor
              voices={voices}
              settings={settings}
              onUpdateSetting={updateSetting}
            />
          )}
          {activeTab === 'history' && <HistoryPanel />}
          {activeTab === 'settings' && <SettingsPanel />}
        </div>
      </main>
    </div>
  );
}
