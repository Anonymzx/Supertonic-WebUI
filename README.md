# 🎙️ Supertonic-3 TTS WebUI

> **Local, Offline, Expressive Text-to-Speech**  
> A powerful Gradio-based WebUI for the **Supertonic-3** TTS model (~99M parameters). Generate natural-sounding speech in 31+ languages with emotion tags, voice customization, and hardware-accelerated inference — **100% offline**.

<p align="center">
  <img src="https://img.shields.io/badge/Language-31%2B-brightgreen" alt="Languages">
  <img src="https://img.shields.io/badge/Offline-Yes-blue" alt="Offline">
  <img src="https://img.shields.io/badge/License-OpenRAIL--M-orange" alt="License">
  <img src="https://img.shields.io/badge/Model-~99M%20Params-lightgrey" alt="Model Size">
</p>

---

## ✨ Why Supertonic-3 WebUI?

| Feature | Benefit |
|---------|---------|
| 🌍 **31+ Languages + Auto-Detect** | Speak globally — or let the model detect language automatically |
| 🎭 **Expression Tags** | Add `<breath>`, `<laugh>`, `<sigh>` for human-like prosody |
| ⚡ **Hardware Agnostic** | Run on CPU, NVIDIA CUDA, AMD DirectML/ROCm — switch anytime |
| 🎨 **Custom Voice Support** | Import your own voice embeddings from Supertonic Voice Builder |
| 🔒 **100% Local & Private** | No cloud, no API keys, no data leaves your machine |
| 🖥️ **Polished Gradio UI** | Intuitive, responsive, with examples and one-click tag insertion |

---

## 🚀 Installation

### ▶️ Windows (One-Click Setup)
```bash
git clone https://github.com/Anonymzx/Supertonic-WebUI.git
cd Supertonic-WebUI
```
1. Double-click `install.bat` → auto-creates venv + installs dependencies + selects optimal ONNX runtime  
2. Double-click `run.bat` → launches the WebUI  
3. Open [http://localhost:7860](http://localhost:7860) in your browser  

### 🐧 Linux / macOS / Advanced Users
```bash
# Clone & setup
git clone https://github.com/Anonymzx/Supertonic-WebUI.git
cd Supertonic-WebUI
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install ONNX Runtime (pick ONE based on your hardware)
# ───────────────────────────────────────────────────────
# NVIDIA GPU (CUDA 12.x)   → pip install onnxruntime-gpu
# AMD GPU (Windows)        → pip install onnxruntime-directml
# AMD GPU (Linux)          → pip install onnxruntime-rocm
# CPU / Apple Silicon      → pip install onnxruntime

# Launch
python main.py
```

---

## 💻 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | Dual-core | Quad-core or better |
| **RAM** | 4 GB | 8 GB+ |
| **GPU** | None | NVIDIA/AMD with 2GB+ VRAM |
| **Storage** | 500 MB | 1 GB+ (for model cache) |
| **OS** | Windows 10 / Linux / macOS | Latest stable release |

> 💡 **Tip**: GPU acceleration (CUDA/DirectML/ROCm) significantly reduces inference time. CPU mode works great for testing and light usage.

---

## 🎯 Quick Start Guide

1. **Select Hardware Backend**  
   Expand ⚙️ *Hardware Settings* → choose your execution provider (e.g., `DirectML` for AMD on Windows).

2. **Initialize the Engine**  
   Click *"Initialize / Reinitialize Engine"* to load the model.

3. **Configure Output**  
   - 🌐 Language: Pick a language or use `Language Agnostic (na)` for auto-detect  
   - 🗣️ Voice Style: Choose from preset voices or upload a custom embedding  
   - ⚙️ Speed: 0.5x (slow) to 2.0x (fast)  
   - 🎚️ Quality: 5–12 synthesis steps (higher = better quality, slower)

4. **Enter & Enhance Text**  
   Type your script → use 🎭 *Expression Tags Helper* to insert natural prosody elements.

5. **Generate & Download**  
   Click *"🚀 Generate Speech"* → preview → save as WAV/MP3.

---

## 🎭 Expression Tags Reference

Inject emotion and natural pauses directly into your text:

| Tag | Effect | Example Usage |
|-----|--------|---------------|
| `<breath>` | Soft inhale/exhale | `Welcome <breath> to our channel` |
| `<laugh>` | Light chuckle or laugh | `That was <laugh> amazing!` |
| `<sigh>` | Expressive sigh | `<sigh> I guess we'll try again` |
| `<ah>` / `<uh>` | Natural hesitation | `<uh> let me think about that` |
| `[pause]` | Brief silence (~0.5s) | `Wait for it... [pause] boom!` |

> 💡 **Pro Tip**: Combine tags for ultra-realistic delivery:  
> `"I can't believe it <laugh> <breath> actually worked!"`

---

## 🎨 Custom Voice Integration

Bring your own voice:

1. Generate a voice embedding via **Supertonic Voice Builder** → export as `.json`  
2. In the WebUI, go to the *"🎨 Custom Voice"* tab  
3. Upload your `.json` file (must contain `voice_embedding` array)  
4. Return to main tab → your custom voice is now active  

> ⚠️ Custom voices override the preset voice selector. Upload a new file to switch voices.

---

## 🛠️ Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| ❌ Model won't download | No internet / firewall | Ensure connection on first run; model caches locally after |
| ⚠️ GPU not detected | Wrong ONNX package | Reinstall with correct runtime: `onnxruntime-gpu` / `directml` / `rocm` |
| 🪟 App closes instantly (Windows) | Launched via double-click | Always use `run.bat` or run `python main.py` from terminal to see errors |
| 🐌 Slow inference | CPU mode / low steps | Switch to GPU backend or increase *Quality* steps (max 12) |
| 🔊 Audio sounds robotic | Missing expression tags | Use `<breath>`, `[pause]`, etc. to add natural rhythm |

---

## 🔗 Resources & Credits

- **📦 Model**: [Supertonic-3 on Hugging Face](https://huggingface.co) *(OpenRAIL-M License)*  
- **🧠 Core Engine**: Official `supertonic` Python package  
- **🎨 UI Framework**: [Gradio](https://www.gradio.app/)  
- **🔧 ONNX Runtime**: [Microsoft ONNX](https://onnxruntime.ai/)  

```
⚠️ Disclaimer: This WebUI is a community wrapper. 
The Supertonic-3 model and its license terms are maintained by the original authors.
```

---

## 🤝 Contributing & Support

Found a bug? Have a feature idea?

1. 🐛 [Open an Issue](https://github.com/Anonymzx/Supertonic-WebUI/issues)  
2. 🔀 Submit a Pull Request with clear description  
3. 💬 Join discussions in the repo's *Discussions* tab  

> 🙏 Special thanks to the Supertonic team, ONNX community, and Gradio developers for making local AI accessible to everyone.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/Anonymzx">@Anonymzx</a> • For creators, developers, and privacy-first users</sub>
</p>