# Supertonic TTS WebUI

A production-ready local AI text-to-speech web application inspired by ElevenLabs, powered by **Supertonic 3** running entirely offline on your hardware with AMD GPU acceleration via DirectML.

![Tech Stack](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)
![Tech Stack](https://img.shields.io/badge/React-20232A?logo=react)
![Tech Stack](https://img.shields.io/badge/TailwindCSS-06B6D4?logo=tailwindcss)
![Tech Stack](https://img.shields.io/badge/ONNX_Runtime-005CED?logo=onnx)
![Tech Stack](https://img.shields.io/badge/AMD_GPU-DirectML-ED1C24?logo=amd)

## ✨ Features

- **Fully Local & Offline** - No cloud APIs, no data leaves your machine
- **AMD GPU Acceleration** - DirectML support for AMD Radeon RX 7800 XT and other GPUs
- **10 Premium Voices** - 5 Female (F1-F5) and 5 Male (M1-M5) voices
- **Modern UI** - Premium dark glassmorphism design like ElevenLabs
- **Audio Waveform Player** - Visual playback with controls
- **Generation History** - Persistent history with search and replay
- **Batch Processing** - Generate multiple texts at once
- **Streaming Audio** - Real-time audio streaming support
- **Expression Tags** - Support for `<laugh>`, `<breath>`, `<sigh>` tags
- **Auto Language Detection** - Indonesian and English optimized
- **Speed & Quality Controls** - Adjustable speed (0.5x-2.0x) and quality steps
- **Audio Caching** - Smart caching to avoid regeneration
- **Keyboard Shortcuts** - Quick access with `Ctrl+Enter`, `Alt+1/2/3`
- **Settings Persistence** - Save your preferences locally
- **Responsive Design** - Desktop and mobile friendly

## 🎯 System Requirements

- **OS**: Windows 11 (primary), Linux/macOS supported
- **Python**: 3.10+
- **Node.js**: 18+
- **GPU**: AMD Radeon RX 7800 XT recommended (DirectML compatible)
- **RAM**: 8GB+ recommended
- **Storage**: 2GB+ for model files

## 🚀 Quick Start (Windows)

### One-Click Setup

#### Step 1: Install Dependencies

Double-click **`install.bat`** or run in terminal:
```
install.bat
```

This script will:
- ✅ Check that Python 3.10+ is installed
- ✅ Check that Node.js 18+ and npm are installed
- ✅ Create a Python virtual environment (`venv/`)
- ✅ Activate the virtual environment automatically
- ✅ Upgrade pip to the latest version
- ✅ Install all backend Python packages from `requirements.txt`
- ✅ Install ONNX Runtime with DirectML (AMD GPU acceleration)
- ✅ Install all frontend npm packages
- ✅ Create the `outputs/` directory structure

> **Troubleshooting**: If you have multiple Python versions, the script uses the default `python` command. Make sure your Python 3.10+ is set as the default.

#### Step 2: Start the Full Application

Double-click **`runWebUI.bat`** or run in terminal:
```
runWebUI.bat
```

This will:
- ✅ Activate the virtual environment
- ✅ Start the FastAPI backend in a new CMD window (port 8000)
- ✅ Start the Vite frontend in a new CMD window (port 5173)
- ✅ Automatically open http://localhost:5173 in your browser

#### Step 3: Use the Application

1. **Load the Model**: Go to **Settings > Model Management** and click **Load Model** or **Download Model**
2. **Generate Speech**: Type text in the editor, select a voice, and click **Generate** (or press `Ctrl+Enter`)
3. **Listen & Download**: Use the audio player to play, download, or copy your generated speech

---

### Alternative: Run Services Separately

If you prefer to run backend and frontend in separate windows:

#### Start Backend Only

Double-click **`runBackend.bat`** or run:
```
runBackend.bat
```

This activates the virtual environment and starts the FastAPI server on `http://localhost:8000`.

#### Start Frontend Only

Double-click **`runFrontend.bat`** or run:
```
runFrontend.bat
```

This starts the Vite development server on `http://localhost:5173`.

> **Note**: The frontend needs the backend to be running for TTS generation to work.

---

### Update Dependencies

Double-click **`update.bat`** or run:
```
update.bat
```

This will:
- ✅ Update all Python packages to latest versions
- ✅ Update all npm packages to latest versions
- ✅ Upgrade pip
- ✅ Show outdated package list before updating

---

### Manual Setup (Alternative)

#### Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Linux/Mac)
# source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install ONNX Runtime with DirectML (AMD GPU)
pip install onnxruntime-directml

# OR for CPU-only mode
pip install onnxruntime

# Install Supertonic SDK (optional)
pip install supertonic

# Start the backend
cd backend
python main.py
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 🔧 AMD GPU Setup (DirectML)

For optimal performance with AMD Radeon RX 7800 XT:

1. **Install AMD Adrenalin Drivers** (latest from amd.com)
2. **DirectML is installed automatically** by `install.bat`, or manually:
   ```bash
   pip install onnxruntime-directml
   ```
3. **Verify GPU detection:**
   ```bash
   python -c "import onnxruntime as ort; print(ort.get_available_providers())"
   ```
   Should show `DmlExecutionProvider` in the list.
4. **Model file**: Place your Supertonic 3 ONNX model in:
   ```
   outputs/models/supertonic-3.onnx
   ```
   Or use the **Download Model** button in Settings > Model Management.

### 🔄 CPU Fallback

The application automatically falls back to CPU if DirectML is unavailable. No configuration changes needed.

---

### Windows CMD Unicode Fix

The backend automatically sets UTF-8 encoding on Windows startup:
```python
os.system("chcp 65001 > nul")
```
This prevents crashes from Unicode characters in Windows Command Prompt. All log messages use ASCII-safe `[OK]`, `[WARNING]`, `[FAIL]` prefixes instead of Unicode symbols.

---

### Diagnostics Endpoint

Once the backend is running, visit:
```
GET http://localhost:8000/api/debug/providers
```

This returns detailed diagnostics including:
- Python executable path and version
- Active virtual environment path
- ONNX Runtime version and available providers
- Whether DirectML (AMD GPU) is detected
- Whether supertonic SDK is installed
- Detailed DirectML provider info

Use this to verify your installation is correct.

## 📁 Project Structure

```
supertonic-tts-webui/
├── backend/           # FastAPI Python backend
│   ├── config.py      # Configuration & environment
│   ├── models.py      # Pydantic API models
│   ├── main.py        # FastAPI application & routes
│   ├── tts_engine.py  # Core TTS engine (Supertonic 3)
│   ├── voice_manager.py  # Voice management
│   ├── history_manager.py # Generation history
│   ├── queue_manager.py   # Async generation queue
│   └── execution_providers.py  # ONNX provider detection
├── frontend/          # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/  # React components
│   │   ├── hooks/     # Custom hooks
│   │   └── types/     # TypeScript types
│   └── ...config files
├── outputs/           # Generated audio & cache
│   ├── models/        # Supertonic model files
│   ├── cache/         # Audio cache
│   └── history/       # Generation history JSON
├── scripts/           # Utility scripts
├── install.bat        # Windows installer
├── start.bat          # Windows launcher
├── requirements.txt   # Python dependencies
└── package.json       # Root package.json
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tts` | Generate speech from text |
| POST | `/api/tts/stream` | Generate speech with streaming |
| POST | `/api/tts/batch` | Batch generate multiple texts |
| GET | `/api/voices` | List all available voices |
| GET | `/api/voices/{id}` | Get voice details |
| GET | `/api/history` | Get generation history |
| DELETE | `/api/history/{id}` | Delete history item |
| GET | `/api/system/info` | Get system information |
| POST | `/api/model/load` | Load the TTS model |
| POST | `/api/model/download` | Download model from HuggingFace |
| GET | `/api/health` | Health check |

## 🎨 UI Features

- **Dark Theme** - Premium dark glassmorphism design
- **Sidebar** - Collapsible navigation with GPU status
- **Voice Selector** - Dropdown with grouped voices (female/male)
- **Speed Control** - Slider from 0.5x to 2.0x
- **Quality Control** - Steps from Draft (8) to Premium (64)
- **Language Selector** - Auto-detect, English, Indonesian, and more
- **Expression Tags** - Quick insert `<laugh>`, `<breath>`, `<sigh>`
- **Audio Player** - Play/pause, volume, waveform visualization
- **Toast Notifications** - Success/error feedback
- **Loading States** - Skeleton loading animations
- **Empty States** - Helpful placeholders
- **Keyboard Shortcuts** - See shortcuts below

### ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Generate speech |
| `Alt + 1` | Switch to Generate tab |
| `Alt + 2` | Switch to History tab |
| `Alt + 3` | Switch to Settings tab |

## 🐛 Troubleshooting

### Model not loading
- Ensure model file is in `outputs/models/` directory
- Check backend logs for detailed error
- Use Settings > Model Management > Download Model

### GPU not detected
- Run `python -c "import onnxruntime as ort; print(ort.get_available_providers())"`
- Ensure you installed `onnxruntime-directml` not `onnxruntime`
- Update AMD drivers to latest version
- Check Windows DirectML support

### No audio output
- Check that the audio file URL is accessible
- Verify the output WAV file exists in `outputs/`
- Check browser console for CORS errors

### Port already in use
- Change ports in `.env` file
- Default: Backend=8000, Frontend=5173

## 🏗️ Building for Production

```bash
# Build frontend
cd frontend
npm run build

# Frontend built to frontend/dist/

# For production deployment, serve built frontend from FastAPI
# or use a web server like nginx
```

## 📦 Dependencies

### Backend
- **fastapi** - Modern web framework
- **uvicorn** - ASGI server
- **onnxruntime-directml** - AMD GPU inference
- **supertonic** - TTS model SDK
- **soundfile** - Audio file I/O
- **numpy** - Numerical processing
- **pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Utility CSS
- **Framer Motion** - Animations
- **Axios** - HTTP client
- **Lucide React** - Icons
- **Wavesurfer.js** - Audio waveforms
- **React Hot Toast** - Notifications

## 📄 License

MIT

## 🙏 Acknowledgments

- Supertonic team for the TTS model
- ElevenLabs for UI inspiration
- ONNX Runtime team for GPU acceleration
</write_to_file>