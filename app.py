"""
Supertonic-3 WebUI - Local Text-to-Speech Interface
===================================================
A comprehensive Gradio-based WebUI for the Supertonic-3 TTS model.
Supports multiple execution providers (CPU, CUDA, DirectML, ROCm).
"""

import gradio as gr
import numpy as np
import os
import json
import re
from typing import Tuple, Optional


# ===========================================================================
# GLOBAL TTS ENGINE INITIALIZATION
# ===========================================================================

_tts_engine = None
_tts_config = {"provider": "CPU"}


def get_execution_providers(provider_name: str):
    """Map provider name to ONNX Runtime execution provider list."""
    if provider_name == "CUDA":
        try:
            import onnxruntime
            providers = [("CUDAExecutionProvider", {"device_id": 0, "arena_extend_strategy": "kSameAsRequested"})]
            print("[Supertonic-3] CUDA ExecutionProvider enabled")
            return providers
        except Exception as e:
            print(f"[Supertonic-3] CUDA not available, falling back to CPU: {e}")
            return ["CPUExecutionProvider"]
    
    elif provider_name == "DirectML":
        try:
            import onnxruntime
            providers = [("DirectMLExecutionProvider", {"device_id": 0})]
            print("[Supertonic-3] DirectML ExecutionProvider enabled")
            return providers
        except Exception as e:
            print(f"[Supertonic-3] DirectML not available, falling back to CPU: {e}")
            return ["CPUExecutionProvider"]
    
    elif provider_name == "ROCm":
        try:
            import onnxruntime
            providers = [("ROCMExecutionProvider", {"device_id": 0})]
            print("[Supertonic-3] ROCm ExecutionProvider enabled")
            return providers
        except Exception as e:
            print(f"[Supertonic-3] ROCm not available, falling back to CPU: {e}")
            return ["CPUExecutionProvider"]
    
    else:  # CPU
        print("[Supertonic-3] Using CPUExecutionProvider")
        return ["CPUExecutionProvider"]


def initialize_tts_engine(provider: str = "CPU"):
    """Initialize or reinitialize the Supertonic TTS engine with the specified provider."""
    global _tts_engine, _tts_config
    
    try:
        _tts_config["provider"] = provider
        print(f"[Supertonic-3] Initializing TTS engine with provider: {provider}...")
        
        from supertonic import TTS
        
        _tts_engine = TTS(auto_download=True)
        _tts_engine._provider = provider
        
        print(f"[Supertonic-3] TTS engine initialized successfully!")
        return f"✅ Engine initialized successfully with {provider} provider.", provider
    
    except ImportError as e:
        error_msg = f"❌ Failed to import supertonic: {e}\nPlease ensure supertonic is installed."
        print(error_msg)
        return error_msg, provider
    except Exception as e:
        error_msg = f"❌ Failed to initialize TTS engine: {e}"
        print(error_msg)
        return error_msg, provider


def get_tts_engine():
    """Get the current TTS engine instance, initializing if needed."""
    global _tts_engine
    if _tts_engine is None:
        initialize_tts_engine(_tts_config["provider"])
    return _tts_engine


# ===========================================================================
# VOICE STYLE & LANGUAGE HELPERS
# ===========================================================================

DEFAULT_VOICE_STYLES = ["M1", "M2", "F1", "F2", "M3", "M4", "M5", "F3", "F4", "F5"]

SUPPORTED_LANGUAGES = [
    ("Auto-Detect (Language Agnostic)", "na"),
    ("Indonesian (id)", "id"),
    ("English (en)", "en"),
    ("Japanese (ja)", "ja"),
    ("Korean (ko)", "ko"),
    ("Chinese (zh)", "zh"),
    ("Mandarin (cmn)", "cmn"),
    ("Cantonese (yue)", "yue"),
    ("Javanese (jav)", "jav"),
    ("Sundanese (su)", "su"),
    ("Madurese (mad)", "mad"),
    ("Tagalog (tl)", "tl"),
    ("Bengali (ben)", "ben"),
    ("Hindi (hi)", "hi"),
    ("Arabic (ar)", "ar"),
    ("French (fr)", "fr"),
    ("German (de)", "de"),
    ("Spanish (es)", "es"),
    ("Portuguese (pt)", "pt"),
    ("Russian (ru)", "ru"),
    ("Dutch (nl)", "nl"),
    ("Italian (it)", "it"),
    ("Turkish (tr)", "tr"),
    ("Polish (pl)", "pl"),
    ("Romanian (ro)", "ro"),
    ("Greek (el)", "el"),
    ("Thai (th)", "th"),
    ("Vietnamese (vi)", "vi"),
    ("Hungarian (hu)", "hu"),
    ("Czech (cs)", "cs"),
    ("Finnish (fi)", "fi"),
    ("Norwegian (no)", "no"),
    ("Swedish (sv)", "sv"),
]


def get_available_voices(tts_instance):
    """Retrieve available voice styles from the TTS instance."""
    try:
        styles = DEFAULT_VOICE_STYLES
        try:
            if hasattr(tts_instance, 'list_voices'):
                styles = tts_instance.list_voices()
        except Exception:
            pass
        return styles
    except Exception:
        return DEFAULT_VOICE_STYLES


# ===========================================================================
# TEXT PROCESSING & EXPRESSION TAGS
# ===========================================================================

EXPRESSION_TAGS = {
    "<breath>": "Breath sound",
    "<laugh>": "Laugh sound",
    "<sigh>": "Sigh sound",
    "<ah>": "Ah interjection",
    "<uh>": "Uh hesitation",
    "[pause]": "Short pause",
    "[breath]": "Breath pause",
}


def insert_tag_at_cursor(current_text: str, tag: str) -> str:
    """Append an expression tag to the current text."""
    safe_text = current_text if current_text else ""
    return safe_text + f" {tag} "


def synthesize_speech(
    text: str,
    lang: str,
    voice_style: str,
    speed: float,
    quality_steps: int,
    custom_voice_file: Optional[str] = None
) -> Tuple[Tuple[int, 'np.ndarray'], str]:
    """Main inference function: synthesizes speech from text."""
    global _tts_engine
    
    empty_audio = (22050, np.array([], dtype=np.float32))
    
    if not text or not text.strip():
        return empty_audio, "❌ Error: Please enter some text to synthesize."
    
    try:
        tts = get_tts_engine()
        
        try:
            if custom_voice_file and os.path.exists(custom_voice_file):
                with open(custom_voice_file, 'r', encoding='utf-8') as f:
                    custom_voice_data = json.load(f)
                
                if "voice_embedding" in custom_voice_data:
                    style = tts.build_custom_voice(
                        embedding=custom_voice_data["voice_embedding"],
                        **{k: v for k, v in custom_voice_data.items() if k != "voice_embedding"}
                    )
                else:
                    style = tts.get_voice_style(voice_name=voice_style)
            else:
                style = tts.get_voice_style(voice_name=voice_style)
        except Exception as e:
            return empty_audio, f"❌ Error loading voice style: {e}. Make sure the voice style '{voice_style}' is available."
        
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        if not cleaned_text:
            return empty_audio, "❌ Error: Text is empty after cleaning."
        
        print(f"[Supertonic-3] Synthesizing: lang={lang}, voice={voice_style}, speed={speed}, quality={quality_steps}")
        
        wav, duration = tts.synthesize(
            text=cleaned_text,
            voice_style=style,
            lang=lang,
            speed=speed,
            total_steps=quality_steps
        )
        
        if isinstance(wav, list):
            wav = np.array(wav, dtype=np.float32)
        elif not isinstance(wav, np.ndarray):
            wav = np.frombuffer(wav, dtype=np.float32)
            
        if len(wav.shape) > 1:
            wav = wav.flatten()

        if wav.dtype == np.float32 or wav.dtype == np.float64:
            wav = np.int16(wav * 32767.0)
            
        if isinstance(duration, np.ndarray):
            duration_seconds = float(duration.flatten()[0])
        else:
            duration_seconds = float(duration)
            
        status_msg = f"✅ Generated successfully! Duration: {duration_seconds:.2f}s"
        print(f"[Supertonic-3] Synthesis complete: {duration_seconds:.2f}s")
        
        return (44100, wav), status_msg
    
    except Exception as e:
        error_msg = f"❌ Synthesis error: {e}"
        print(f"[Supertonic-3] {error_msg}")
        return (0, np.array([], dtype=np.float32)), error_msg


# ===========================================================================
# GRADIO UI DEFINITION
# ===========================================================================

CUSTOM_CSS = """
.main-title {
    text-align: center;
    padding: 10px 0;
}
.subtitle {
    text-align: center;
    font-size: 14px;
    color: #666;
}
.info-box {
    padding: 10px;
    border-radius: 8px;
    margin: 10px 0;
}
.tag-button {
    margin: 2px;
}
"""

def build_app():
    """Build and return the Gradio WebUI application."""
    
    with gr.Blocks(title="Supertonic-3 TTS WebUI") as app:
        
        with gr.Column(elem_classes="main-title"):
            gr.Markdown("# 🎙️ Supertonic-3 TTS WebUI")
            gr.Markdown(
                "## Local Text-to-Speech with Supertonic-3 (~99M parameters)  \n"
                "[GitHub Repository](https://github.com/Anonymzx/Supertonic-WebUI)"
            )
            gr.Markdown(
                "A lightweight, offline TTS engine supporting **31 languages** with expression tags. "
                "No cloud connection required!"
            )
        
        with gr.Tabs():
            
            with gr.Tab("🎤 Generate Speech"):
                with gr.Row():
                    with gr.Column(scale=1):
                        
                        with gr.Accordion("⚙️ Hardware Settings", open=False):
                            execution_provider = gr.Dropdown(
                                choices=["CPU", "CUDA", "DirectML", "ROCm"],
                                value="CPU",
                                label="Execution Provider",
                                info="Select your hardware accelerator"
                            )
                            init_button = gr.Button("Initialize / Reinitialize Engine", variant="secondary")
                            init_status = gr.Textbox(
                                label="Engine Status",
                                interactive=False,
                                info="Click 'Initialize' to load the model"
                            )
                        
                        with gr.Accordion("🎵 Voice & Output Settings", open=True):
                            with gr.Row():
                                language_choice = gr.Dropdown(
                                    choices=SUPPORTED_LANGUAGES,
                                    value="na",
                                    label="Language",
                                    info="Select language or Auto-Detect"
                                )
                                voice_style_dropdown = gr.Dropdown(
                                    choices=DEFAULT_VOICE_STYLES,
                                    value="M1",
                                    label="Voice Style",
                                    info="Built-in voice style preset"
                                )
                            
                            with gr.Row():
                                speed_slider = gr.Slider(
                                    minimum=0.5, 
                                    maximum=2.0, 
                                    value=1.0, 
                                    step=0.05, 
                                    label="Reading Speed",
                                    info="0.7 (Slow) to 2.0 (Fast)"
                                )
                                quality_slider = gr.Slider(
                                    minimum=5, 
                                    maximum=12, 
                                    value=8, 
                                    step=1, 
                                    label="Quality (Total Steps)",
                                    info="5 (Fast/Low) to 12 (Slow/High)"
                                )
                        
                        # Define Text Input FIRST so buttons can target it
                        text_input = gr.Textbox(
                            label="Input Text",
                            placeholder="Enter text to synthesize...\nExample: Halo, nama saya asisten virtual. <laugh>Senang bertemu dengan Anda!</>  ",
                            lines=6,
                            max_lines=20,
                            info="Supports expression tags like <breath>, <laugh>, <sigh>"
                        )
                        
                        with gr.Accordion("🎭 Expression Tags Helper", open=True):
                            gr.Markdown("**Click a tag to append it to your text:**")
                            with gr.Row():
                                for tag, desc in list(EXPRESSION_TAGS.items())[:4]:
                                    gr.Button(
                                        tag,
                                        variant="secondary",
                                        size="sm",
                                        elem_classes="tag-button",
                                    ).click(
                                        fn=lambda current, t=tag: insert_tag_at_cursor(current, t),
                                        inputs=[text_input],
                                        outputs=[text_input]
                                    )
                            with gr.Row():
                                for tag, desc in list(EXPRESSION_TAGS.items())[4:]:
                                    gr.Button(
                                        tag,
                                        variant="secondary",
                                        size="sm",
                                        elem_classes="tag-button",
                                    ).click(
                                        fn=lambda current, t=tag: insert_tag_at_cursor(current, t),
                                        inputs=[text_input],
                                        outputs=[text_input]
                                    )
                        
                        generate_button = gr.Button(
                            "🚀 Generate Speech",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        
                        audio_output = gr.Audio(
                            label="Generated Speech",
                            type="numpy",
                            interactive=False
                        )
                        
                        output_status = gr.Textbox(
                            label="Status",
                            interactive=False
                        )
                        
            with gr.Tab("🎨 Custom Voice"):
                with gr.Column():
                    gr.Markdown(
                        "### Custom Voice Upload\n"
                        "Upload a JSON file containing a custom voice embedding from Supertonic Voice Builder. "
                        "The JSON file should contain a `voice_embedding` field."
                    )
                    
                    custom_voice_upload = gr.File(
                        label="Upload Custom Voice JSON",
                        file_types=[".json"],
                        type="filepath"
                    )
                    
                    custom_voice_info = gr.Textbox(
                        label="Custom Voice Info",
                        interactive=False,
                        info="Upload a JSON file to use a custom voice"
                    )
                    
                    gr.Markdown("### 📚 Additional Information")
                    gr.Markdown(
                        "#### Expression Tags Guide:\n"
                        "| Tag | Description | Example |\n"
                        "|-----|-------------|--------|\n"
                        "| `<breath>` | Natural breath sound | Hello <breath> how are you? |\n"
                        "| `<laugh>` | Laugh sound | That's <laugh> hilarious! |\n"
                        "| `<sigh>` | Sigh sound | *sigh* I'm tired |\n"
                        "| `[pause]` | Short pause | See you... [pause] tomorrow |\n"
                        "\n"
                        "💡 **Tip**: Use expression tags to add natural prosody and emotion to your speech synthesis."
                    )
        
        # ==================== EVENT HANDLERS ====================
        
        init_button.click(
            fn=initialize_tts_engine,
            inputs=[execution_provider],
            outputs=[init_status, execution_provider]
        )
        
        def synthesis_handler(
            text: str,
            lang: str,
            voice_style: str,
            speed: float,
            quality: int,
            custom_voice_file: Optional[str],
            provider: str
        ):
            _, current_provider = initialize_tts_engine(provider)
            return synthesize_speech(text, lang, voice_style, speed, quality, custom_voice_file)
        
        generate_button.click(
            fn=synthesis_handler,
            inputs=[text_input, language_choice, voice_style_dropdown, speed_slider, quality_slider, custom_voice_upload, execution_provider],
            outputs=[audio_output, output_status]
        )
        
        app.load(
            fn=lambda: initialize_tts_engine("CPU"),
            outputs=[init_status, execution_provider]
        )
    
    return app


# ===========================================================================
# MAIN ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Supertonic-3 TTS WebUI")
    print("  Local Text-to-Speech Interface")
    print("=" * 60)
    
    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True,
        css=CUSTOM_CSS,
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="gray")
    )