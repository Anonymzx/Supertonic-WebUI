# ️  🎙️Supertonic-3 TTS WebUI

**Local, Offline, Expressive Text-to-Speech**  

 A powerful Gradio-based WebUI for the **Supertonic-3** TTS model (~99M parameters). Generate natural-sounding speech in 31+ languages with emotion tags, advanced audio post-processing, voice customization, and hardware-accelerated inference — **100% offline**.

<p align="center">
  <img src="https://img.shields.io/badge/Language-31%2B-brightgreen" alt="Languages">
  <img src="https://img.shields.io/badge/🇮🇩_Indonesian-Supported-red" alt="Indonesian">
  <img src="https://img.shields.io/badge/Audio_Pipeline-Librosa-yellow" alt="Librosa">
  <img src="https://img.shields.io/badge/Offline-Yes-blue" alt="Offline">
  <img src="https://img.shields.io/badge/License-OpenRAIL--M-orange" alt="License">
</p>

---

## 🖼️ UI Preview

<p align="center">
  <img width="1191" height="1035" alt="Supertonic-3 WebUI Interface" src="https://github.com/user-attachments/assets/c366cc55-025a-4659-b607-2115b3076bd2" />
</p>

**Interface Overview:**
- **Native AI Generation**: Large text input area with quick-access expression tag buttons (10 official emotions).
- **Advanced Audio Post-Processing**: Built-in Librosa pipeline for pitch shifting, auto-trimming, volume normalization, and special effects.
- **Hardware Selection**: Seamlessly switch between CUDA, DirectML, ROCm, and CPU on the fly.

---

## ✨ Key Features

| Feature | Benefit |
|---------|---------|
|  **31+ Languages + Auto-Detect** | Speak globally — or let the model detect language automatically. |
| 🎭 **10 Official Expression Tags** | Add `<breath>`, `<laugh>`, `<scream>`, `<angry>`, etc., for human-like prosody. |
| ️ **Audio Post-Processing** | Built-in pitch shifting, silence trimming, clarity boost, and chorus effects via Librosa. |
| ⚡ **Hardware Agnostic** | Run on CPU, NVIDIA CUDA, AMD DirectML/ROCm — switch anytime. |
| 🎨 **Custom Voice Support** | Import your own voice embeddings from Supertonic Voice Builder. |
| 🔒 **100% Local & Private** | No cloud, no API keys, no data leaves your machine. |

---

##  Audio Samples & Usage Examples

See how Supertonic-3 handles different languages and emotions using expression tags. You can copy these examples directly into the WebUI to test them.

| Language | Context / Style | Input Text with Tags | Sample Output |
|----------|-----------------|----------------------|---------------|
| 🇩 **Indonesian** | **Introduction (Perkenalan)** | `Halo, nama saya Thoriq. Senang bertemu denganmu! <breath> Saya kuliah di Universitas Pamulang, di jurusan Sistem Informasi.` | [▶️ Play](https://github.com/user-attachments/files/28419480/1.wav) |
| 🇮🇩 **Indonesian** | Emotional / Sighing | `<sigh> Aku sudah bilang berkali-kali, jangan lupa kunci pintunya.` | [▶️ Play](https://github.com/user-attachments/files/28419485/2.wav) |
| 🇮🇩 **Indonesian** | Casual / Laughing | `Wah <laugh> kamu bisa juga! <breath> Aku nggak nyangka lho.` | [▶️ Play](https://github.com/user-attachments/files/28419491/3.wav) |
| 🇩 **Indonesian** | Formal / Pause | `Selamat datang [pause] terima kasih telah bergabung dengan kami.` | [▶️ Play](https://github.com/user-attachments/files/28419504/4.wav) |
| 🇺🇸 **English** | Casual / Laughing | `I can't believe you did that <laugh> it's so funny!` | [▶️ Play](https://github.com/user-attachments/files/28419511/5.wav) |
| 🇯🇵 **Japanese** | Polite / Hesitant | `Ano... <uh> chotto matte kudasai [pause] arigato gozaimasu.` | [▶️ Play](https://github.com/user-attachments/files/28419515/6.wav) |
| 🇪🇸 **Spanish** | Narrative / Breathing | `Hola <breath> bienvenidos a nuestro canal de YouTube.` | [▶️ Play](https://github.com/user-attachments/files/28419523/7.wav) |

> 💡 **Tip**: For best results, always add `[pause]` or `<breath>` between long sentences to prevent the AI from rushing.

---

## 🎭 Expression Tags Reference

Supertonic-3 natively supports **10 specific emotion tags**. Use them to inject emotion directly into your text.

| Tag | Effect | Example Usage (English) |
|-----|--------|------------------------|
| `<breath>` | Soft inhale/exhale | `Hello <breath> good morning everyone.` |
| `<laugh>` | Light chuckle/laugh | `Wow <laugh> that's so funny!` |
| `<sigh>` | Expressive sigh | `<sigh> Oh well, it's okay.` |
| `<surprise>` | Surprised tone | `<surprise> What? Did he really say that?` |
| `<scream>` | Yelling/Loud tone | `<scream> Watch out ahead!` |
| `<throatclear>` | Clearing throat | `<throatclear> Let's start the presentation.` |
| `<sad>` | Somber/Sad tone | `<sad> It's such a shame we lost today.` |
| `<angry>` | Aggressive/Angry | `<angry> Don't touch that!` |
| `<cough>` | Coughing sound | `Excuse me <cough> just a moment.` |
| `<yawn>` | Yawning sound | `Whoa <yawn> I'm so sleepy.` |

> 💡 **Pro Tip**: Combine tags for ultra-realistic delivery:  
> `"Wow <laugh> <breath> it actually worked!"`

---

## 🚀 Installation

### ▶️ Windows (One-Click Setup)
```bash
git clone https://github.com/Anonymzx/Supertonic-WebUI.git
cd Supertonic-WebUI
```

1. Double-click `install.bat` → auto-creates venv + installs dependencies + selects optimal ONNX runtime.
2. Double-click `run.bat` → launches the WebUI.
3. Open [http://localhost:7860](http://localhost:7860) in your browser.

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

## 🎛️ Audio Post-Processing Guide

This WebUI includes a built-in Librosa pipeline that processes the audio **after** the AI generates it.

| Feature | Description | Best For |
|---------|-------------|----------|
| ✂️ **Auto-Trim Silence** | Removes dead air at start/end automatically | Clean cuts for Shorts/Reels |
|  **Normalize Volume** | Boosts audio to -1dB peak safely | YouTube voiceovers, podcasts |
| 🎙️ **Clarity Boost** | Pre-emphasis filter for sharper consonants | Gaming commentary, tutorials |
| 🎵 **Pitch Shift** | Adjust pitch in semitones (-12 to +12) | Character voices, deep narration |
| 🤖 **Chorus Effect** | Layers detuned copy for robotic texture | Horror content, creative effects |

> ⚙️ All post-processing is optional and can be toggled per generation.

---

## 🎨 Custom Voice Integration (Experimental)

> ⚠️ **Note**: This feature is currently **untested/experimental**. The developer has not yet verified the output quality of custom voice embeddings. Results may vary, and the voice might sound distorted or fail to load depending on the embedding format. Use at your own risk and please report any issues!

If you want to try importing your own voice:

1. Generate a voice embedding via **Supertonic Voice Builder** → export as `.json`.
2. In the WebUI, go to the *"🎨 Custom Voice"* tab.
3. Upload your `.json` file (must contain the `voice_embedding` array).
4. Return to the main tab → the engine will attempt to use your custom voice.

> 💡 **Feedback Wanted**: If you successfully generate good audio with a custom voice, please share your results in the [Issues](https://github.com/Anonymzx/Supertonic-WebUI/issues) or [Discussions](https://github.com/Anonymzx/Supertonic-WebUI/discussions) tab to help improve this feature!

---

## 🛠️ Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| ❌ Model won't download | No internet / firewall | Ensure connection on first run; model caches locally after |
| ⚠️ GPU not detected | Wrong ONNX package | Reinstall with correct runtime: `onnxruntime-gpu` / `directml` / `rocm` |
| 🪟 App closes instantly | Launched via double-click | Always use `run.bat` or run `python main.py` from terminal to see errors |
| 🐌 Slow inference | CPU mode / low steps | Switch to GPU backend or increase *Quality* steps (max 12) |
| 🔊 Audio sounds robotic | Missing expression tags | Use `<breath>`, `<laugh>`, etc., to add natural rhythm |
| 🎚️ Post-processing not applied | Librosa not installed | Run `pip install librosa` in your virtual environment |

---

##  Resources & Credits

- **📦 Model**: [Supertonic-3 on Hugging Face](https://huggingface.co) *(OpenRAIL-M License)*
- **🧠 Core Engine**: Official `supertonic` Python package
- ** UI Framework**: [Gradio](https://www.gradio.app/)
- **🔧 Audio Processing**: [Librosa](https://librosa.org/)
- **⚙️ ONNX Runtime**: [Microsoft ONNX](https://onnxruntime.ai/)

```
⚠️ Disclaimer: This WebUI is a community wrapper. 
The Supertonic-3 model and its license terms are maintained by the original authors.
```

---

## ☕ Support the Project

If you find this tool useful, consider supporting the development!

<p align="center">
  <a href="https://ko-fi.com/anonymzx" target="_blank">
    <img src="https://storage.ko-fi.com/cdn/kofi3.png?v=3" alt="Buy Me a Coffee" height="40">
  </a>
</p>

---

## 🤝 Contributing & Support

Found a bug? Have a feature idea? Want to add support for more languages?

1. 🐛 [Open an Issue](https://github.com/Anonymzx/Supertonic-WebUI/issues) — Describe the problem clearly
2. 🔀 Submit a Pull Request — Include a description of your changes
3. 💬 Join discussions in the repo's *Discussions* tab
4.  Star the repo if you find it useful!

**Ways to Contribute:**
- 🌐 Add translation support for new languages
- 🎨 Improve UI/UX with Gradio components
- 🎛️ Extend audio post-processing features
- 📝 Write tutorials or usage guides
- 🧪 Test on different hardware configurations

> 🙏 Special thanks to the Supertonic team, ONNX community, Librosa developers, and Gradio contributors for making local AI accessible to everyone.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/Anonymzx">@Anonymzx</a> • For creators, developers, and privacy-first users</sub>
</p>

<p align="center">
  <a href="https://github.com/Anonymzx/Supertonic-WebUI/stargazers">
    <img src="https://img.shields.io/github/stars/Anonymzx/Supertonic-WebUI?style=social" alt="GitHub Stars">
  </a>
  <a href="https://github.com/Anonymzx/Supertonic-WebUI/network/members">
    <img src="https://img.shields.io/github/forks/Anonymzx/Supertonic-WebUI?style=social" alt="GitHub Forks">
  </a>
</p>