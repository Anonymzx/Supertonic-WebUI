# 🎙️ Supertonic-3 TTS WebUI

A comprehensive local WebUI for the **Supertonic-3** text-to-speech model (~99M parameters). Supports 31 languages with expression tags, running entirely offline — no cloud connection required.

## Features

- 🎤 **Multi-Language TTS**: Support for 31+ languages including Indonesian, English, Japanese, Korean, and more
- 🎭 **Expression Tags**: Insert `<breath>`, `<laugh>`, `<sigh>`, and other prosody tags
- ⚙️ **Hardware Flexibility**: Choose between CPU, CUDA (NVIDIA GPU), DirectML (AMD Windows), or ROCm (AMD Linux)
- 🎨 **Custom Voice**: Upload custom voice embeddings from Supertonic Voice Builder
- 🖥️ **Clean Gradio UI**: Modern, responsive interface with quick examples

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/Anonymzx/Supertonic-WebUI.git
cd Supertonic-WebUI

# Install base dependencies
pip install -r requirements.txt
```

### 2. Install ONNX Runtime (Choose One)

Select the appropriate runtime based on your hardware:

| Hardware | Command |
|----------|---------|
| **NVIDIA GPU** | `pip install onnxruntime-gpu` |
| **AMD GPU (Windows)** | `pip install onnxruntime-directml` |
| **AMD GPU (Linux)** | `pip install onnxruntime-rocm` |
| **CPU / Apple Silicon** | `pip install onnxruntime` |

### 3. Run the WebUI

```bash
python app.py
```

The UI will open automatically at `http://localhost:7860`

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Dual-core | 4+ core |
| RAM | 4 GB | 8 GB |
| GPU | N/A | NVIDIA/AMD with 2GB+ VRAM |
| Disk | 500 MB | 1 GB (for model cache) |

## Usage Guide

### Basic Workflow

1. **Select Execution Provider** — Choose based on your hardware (click the ⚙️ accordion)
2. **Initialize Engine** — Click "Initialize / Reinitialize Engine" to load the model
3. **Enter Text** — Type or paste text in the input box
4. **Insert Expression Tags** — Click tag buttons to add natural prosody
5. **Select Language & Voice** — Choose language and voice style
6. **Generate** — Click "🚀 Generate Speech"

### Expression Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `<breath>` | Natural breath sound | Hello <breath> how are you? |
| `<laugh>` | Laugh sound | That's <laugh> hilarious! |
| `<sigh>` | Sigh sound | *sigh* I'm tired |
| `<ah>` | Ah interjection | <ah> I see |
| `<uh>` | Uh hesitation | Let me <uh> think |
| `[pause]` | Short pause | See you... [pause] tomorrow |

### Custom Voice

If you have a custom voice embedding from Supertonic Voice Builder:

1. Navigate to the "🎨 Custom Voice" tab
2. Upload your JSON file containing the `voice_embedding` field
3. Select your preferred voice style as fallback
4. Return to "🎤 Generate Speech" and the custom voice will be used

## Project Structure

```
Supertonic-WebUI/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Troubleshooting

### Model Download Fails
```bash
# The model is downloaded automatically on first run.
# If download fails, manually download from Hugging Face:
# https://huggingface.co/Supertone/supertonic-3
```

### GPU Not Detected
- Ensure you've installed the correct ONNX runtime for your hardware
- Check the console output for provider initialization messages
- The UI will fall back to CPU if GPU provider fails

### CUDA Errors
```bash
# For NVIDIA users, ensure CUDA toolkit matches:
# onnxruntime-gpu requires CUDA 12.x
pip install onnxruntime-gpu
```

## API Reference (Python)

```python
from supertonic import TTS

# Initialize (auto-downloads model)
tts = TTS(auto_download=True)

# Get voice style
style = tts.get_voice_style(voice_name="M1")

# Synthesize
wav, duration = tts.synthesize("Hello world", voice_style=style, lang="en")

# Save
tts.save_audio(wav, "output.wav")
```

## License

This project is released as open-source for local, personal use of the Supertonic-3 model.

## Links

- [Supertonic-3 on Hugging Face](https://huggingface.co/Supertone/supertonic-3)
- [Gradio Documentation](https://www.gradio.app/docs)

---

**Note**: This is a WebUI wrapper. The underlying TTS model is provided by the `supertonic` package.