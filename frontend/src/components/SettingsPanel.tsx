import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Cpu,
  Zap,
  HardDrive,
  Activity,
  RefreshCw,
  Download,
  Loader2,
  CheckCircle2,
  XCircle,
  Database,
  Clock,
  Layers,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { getSystemInfo, getModelStatus, downloadModel, loadModel, healthCheck } from '../api/client';
import type { SystemInfo } from '../types';

export default function SettingsPanel() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isLoadingModel, setIsLoadingModel] = useState(false);

  const fetchInfo = async () => {
    try {
      const info = await getSystemInfo();
      setSystemInfo(info);
    } catch {
      // Keep existing info
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInfo();
  }, []);

  const handleDownloadModel = async () => {
    setIsDownloading(true);
    try {
      await downloadModel();
      toast.success('Model download started! Check backend logs.');
    } catch (error) {
      toast.error('Failed to start download');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleLoadModel = async () => {
    setIsLoadingModel(true);
    try {
      await loadModel();
      toast.success('Model loaded successfully!');
      fetchInfo();
    } catch (error) {
      toast.error('Failed to load model. Place model in outputs/models/');
    } finally {
      setIsLoadingModel(false);
    }
  };

  const handleRefresh = () => {
    setIsLoading(true);
    fetchInfo();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 size={24} className="animate-spin text-accent-400" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Settings</h1>
          <p className="text-sm text-gray-500 mt-1">
            System configuration and model management
          </p>
        </div>
        <button onClick={handleRefresh} className="btn-ghost p-2 rounded-lg">
          <RefreshCw size={16} />
        </button>
      </div>

      {/* System Info */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-5">
          <Cpu size={18} className="text-accent-400" />
          <h2 className="text-lg font-semibold text-white">System Information</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <InfoCard
            icon={Zap}
            label="Execution Provider"
            value={systemInfo?.execution_provider || 'Unknown'}
            color="accent"
          />
          <InfoCard
            icon={Cpu}
            label="GPU Status"
            value={systemInfo?.gpu_available ? 'Available' : 'CPU Only'}
            color={systemInfo?.gpu_available ? 'green' : 'yellow'}
          />
          <InfoCard
            icon={Activity}
            label="GPU Name"
            value={systemInfo?.gpu_name || 'N/A'}
            color="blue"
          />
          <InfoCard
            icon={HardDrive}
            label="Audio Cache"
            value={`${systemInfo?.audio_cache_size || 0} files`}
            color="purple"
          />
          <InfoCard
            icon={Database}
            label="Model Status"
            value={systemInfo?.model_loaded ? 'Loaded' : 'Not Loaded'}
            color={systemInfo?.model_loaded ? 'green' : 'red'}
          />
          <InfoCard
            icon={Layers}
            label="ONNX Version"
            value={systemInfo?.onnx_version || 'Unknown'}
            color="gray"
          />
        </div>
      </div>

      {/* Model Management */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-5">
          <Download size={18} className="text-accent-400" />
          <h2 className="text-lg font-semibold text-white">Model Management</h2>
        </div>

        <div className="space-y-4">
          <p className="text-sm text-gray-400">
            The Supertonic 3 model file needs to be placed in{' '}
            <code className="text-accent-300 bg-dark-200 px-1.5 py-0.5 rounded text-xs">
              outputs/models/
            </code>
          </p>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleLoadModel}
              disabled={isLoadingModel || systemInfo?.model_loaded}
              className="btn-primary"
            >
              {isLoadingModel ? (
                <><Loader2 size={16} className="animate-spin" /> Loading...</>
              ) : (
                <><CheckCircle2 size={16} /> Load Model</>
              )}
            </button>

            <button
              onClick={handleDownloadModel}
              disabled={isDownloading || systemInfo?.model_loaded}
              className="btn-secondary"
            >
              {isDownloading ? (
                <><Loader2 size={16} className="animate-spin" /> Downloading...</>
              ) : (
                <><Download size={16} /> Download Model</>
              )}
            </button>
          </div>

          {systemInfo?.model_loaded && (
            <div className="flex items-center gap-2 text-sm text-green-400 mt-2">
              <CheckCircle2 size={16} />
              Model is loaded and ready for inference
            </div>
          )}
        </div>
      </div>

      {/* About */}
      <div className="card p-6">
        <div className="flex items-center gap-2 mb-5">
          <Activity size={18} className="text-accent-400" />
          <h2 className="text-lg font-semibold text-white">About</h2>
        </div>

        <div className="space-y-2 text-sm text-gray-400">
          <p>
            <strong className="text-gray-200">Supertonic TTS WebUI</strong> v1.0.0
          </p>
          <p>
            Local AI text-to-speech platform powered by Supertonic 3.
            Runs completely offline with AMD GPU acceleration via DirectML.
          </p>
          <div className="flex flex-wrap gap-2 mt-3">
            <span className="badge bg-dark-200">FastAPI</span>
            <span className="badge bg-dark-200">React + Vite</span>
            <span className="badge bg-dark-200">ONNX Runtime</span>
            <span className="badge bg-dark-200">DirectML</span>
            <span className="badge bg-dark-200">TailwindCSS</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: any;
  label: string;
  value: string;
  color: 'accent' | 'green' | 'yellow' | 'red' | 'blue' | 'purple' | 'gray';
}) {
  const colorClasses: Record<string, string> = {
    accent: 'bg-accent-500/10 text-accent-300',
    green: 'bg-green-500/10 text-green-400',
    yellow: 'bg-yellow-500/10 text-yellow-400',
    red: 'bg-red-500/10 text-red-400',
    blue: 'bg-blue-500/10 text-blue-400',
    purple: 'bg-purple-500/10 text-purple-400',
    gray: 'bg-dark-100 text-gray-300',
  };

  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-dark-200/50">
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${colorClasses[color] || colorClasses.gray}`}>
        <Icon size={16} />
      </div>
      <div>
        <div className="text-[11px] text-gray-500">{label}</div>
        <div className="text-sm font-medium text-gray-200">{value}</div>
      </div>
    </div>
  );
}
