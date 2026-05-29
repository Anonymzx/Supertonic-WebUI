# 🎙️ Supertonic-3 TTS WebUI

A comprehensive local WebUI for the **Supertonic-3** text-to-speech model (~99M parameters). Supports 31 languages with expression tags, language auto-detection, and advanced audio parameters. Runs entirely offline — no cloud connection required.

---

## ✨ Features

- 🎤 **Multi-Language & Auto-Detect**: Support for 31+ languages (Indonesian, English, Japanese, etc.) or use `Language Agnostic (na)` to let the engine auto-detect the language.
- 🎛️ **Advanced Audio Controls**: Adjustable Reading Speed (0.5x to 2.0x) and Synthesis Quality/Total Steps (5 to 12).
- 🎭 **Expression Tags Helper**: 1-click buttons to insert `<breath>`, `<laugh>`, `<sigh>`, and other natural prosody tags directly into your prompt.
- ⚙️ **Hardware Flexibility**: Choose execution providers dynamically from the UI: CPU, CUDA (NVIDIA), DirectML (AMD Windows), or ROCm (AMD Linux).
- 🎨 **Custom Voice Integration**: Upload custom voice JSON embeddings from Supertonic Voice Builder.
- 🖥️ **Clean Gradio Interface**: Modern, responsive UI with pre-configured example prompts.

---

## 🚀 Quick Start

### Option A: Windows (Recommended for AMD/NVIDIA Users)
We have provided batch scripts to automate the setup and prevent command prompt crashes.

1. Clone the repository:
   ```bash
   git clone https://github.com/Anonymzx/Supertonic-WebUI.git
   cd Supertonic-WebUI
   ```

2. Run `install.bat` (Double-click or run via terminal).  
   This will:
   - Create a virtual environment
   - Install base dependencies
   - Prompt you to select the correct ONNX runtime for your hardware

3. Run `run.bat` to launch the WebUI.

4. Open your browser to [http://localhost:7860](http://localhost:7860).

---

### Option B: Manual Setup (Linux / macOS / Advanced)

#### 1. Install Dependencies
```bash
git clone https://github.com/Anonymzx/Supertonic-WebUI.git
cd Supertonic-WebUI
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Install ONNX Runtime (Choose One)

| Hardware | Command |
|----------|---------|
| **NVIDIA GPU** (Requires CUDA 12.x) | `pip install onnxruntime-gpu` |
| **AMD GPU Windows** | `pip install onnxruntime-directml` |
| **AMD GPU Linux** | `pip install onnxruntime-rocm` |
| **CPU / Apple Silicon** | `pip install onnxruntime` |

#### 3. Run the Application
```bash
python main.py
```

---

## 💻 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | Dual-core | 4+ core |
| **RAM** | 4 GB | 8 GB |
| **GPU** | N/A | NVIDIA/AMD with 2GB+ VRAM (via CUDA/DirectML) |
| **Disk** | 500 MB | 1 GB (for ONNX model cache) |

---

## 📖 Usage Guide

### Basic Workflow

1. **Select Execution Provider** — Open the ⚙️ *Hardware Settings* accordion and choose your backend (e.g., DirectML for AMD GPUs on Windows).
2. **Initialize Engine** — Click *"Initialize / Reinitialize Engine"*.
3. **Configure Voice & Output** — Select your preferred Language (or Auto-Detect), Voice Style, Speed, and Quality.
4. **Enter Text** — Type or paste text into the input box.
5. **Insert Tags** — Use the 🎭 *Expression Tags Helper* to add emotion.
6. **Generate** — Click *"🚀 Generate Speech"*.

---

### Expression Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `<breath>` | Natural breath sound | `Hello <breath> how are you?` |
| `<laugh>` | Laugh sound | `That's <laugh> hilarious!` |
| `<sigh>` | Sigh sound | `<sigh> I'm tired` |
| `<ah>` | Ah interjection | `<ah> I see` |
| `<uh>` | Uh hesitation | `Let me <uh> think` |
| `[pause]` | Short pause | `See you... [pause] tomorrow` |

---

### Using Custom Voices

If you have exported a custom voice embedding from Supertonic:

1. Navigate to the **"🎨 Custom Voice"** tab.
2. Upload your generated `.json` file containing the `voice_embedding` array.
3. Return to the main tab; the engine will prioritize your uploaded JSON over the default voice style dropdown.

---

## 📂 Project Structure

```
Supertonic-WebUI/
├── main.py             # Main Gradio application (formerly app.py)
├── install.bat         # Automated setup script for Windows
├── run.bat             # Safe launcher script for Windows
├── requirements.txt    # Base Python dependencies
└── README.md           # This documentation
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| **Model Download Fails** | The ~99M parameter model is downloaded automatically on the first run. Ensure you have an active internet connection. |
| **GPU Not Detected / Fallback to CPU** | Ensure you installed the correct ONNX package (`onnxruntime-directml` for AMD on Windows, `onnxruntime-gpu` for NVIDIA). Check terminal logs for initialization errors. |
| **Script Force Closes (Windows)** | Do not double-click `main.py`. Always use `run.bat` or execute `python main.py` directly from the VS Code / Command Prompt terminal to view error logs. |

---

## 📄 License & Links

- **UI Repository**: [Anonymzx/Supertonic-WebUI](https://github.com/Anonymzx/Supertonic-WebUI)
- **Model Engine**: [Supertonic-3 on Hugging Face](https://huggingface.co) (OpenRAIL-M License)
- **Framework**: [Gradio](https://www.gradio.app/)

> **Note**: This project is a WebUI wrapper. The underlying TTS logic and models are powered by the official `supertonic` Python package.

---

<p align="center">
  <sub>Built with ❤️ for the local TTS community</sub>
</p>