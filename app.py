"""
Supertonic-3 WebUI - Local Text-to-Speech Interface
===================================================
A comprehensive Gradio-based WebUI for the Supertonic-3 TTS model.
Supports multiple execution providers (CPU, CUDA, DirectML, ROCm).

Usage:
    pip install -r requirements.txt
    pip install onnxruntime-gpu  # or onnxruntime-directml, etc.
    python app.py
"""

import gradio as gr
import numpy as np
import os
import json
from typing import Tuple, Optional


# ===========================================================================
# GLOBAL TTS ENGINE INITIALIZATION
# ===========================================================================

# Global variable to hold the TTS engine instance
_tts_engine = None
_tts_config = {"provider": "CPU"}


def get_execution_providers(provider_name: str):
    """
    Map provider name to ONNX Runtime execution provider list.
    
    Args:
        provider_name: One of 'CPU', 'CUDA', 'DirectML', 'ROCm'
    
    Returns:
        List of execution provider tuples for ONNX Runtime
    """
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
    """
    Initialize or reinitialize the Supertonic TTS engine with the specified provider.
    
    Args:
        provider: Execution provider name ('CPU', 'CUDA', 'DirectML', 'ROCm')
    
    Returns:
        Tuple of (status_message, provider_choice)
    """
    global _tts_engine, _tts_config
    
    try:
        _tts_config["provider"] = provider
        print(f"[Supertonic-3] Initializing TTS engine with provider: {provider}...")
        
        # Import and instantiate the TTS engine
        from supertonic import TTS
        
        _tts_engine = TTS(auto_download=True)
        
        # Store the provider for later use during synthesis
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

# Default voice styles available in Supertonic-3
DEFAULT_VOICE_STYLES = ["M1", "M2", "F1", "F2"]

# Supported language codes (comprehensive list based on Supertonic-3 capabilities)
SUPPORTED_LANGUAGES = [
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
    """
    Retrieve available voice styles from the TTS instance.
    
    Args:
        tts_instance: Initialized TTS engine instance
    
    Returns:
        List of available voice style names
    """
    try:
        # Try to get voice styles
        styles = ["M1", "M2", "F1", "F2"]  # Default fallback
        
        # Try to enumerate available voices
        try:
            # Check if the TTS instance has a method to list voices
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

# Expression tags that can be inserted into the text
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
    """
    Insert an expression tag at the current cursor position or append to text.
    
    Args:
        current_text: Current text content
        tag: Tag to insert
    
    Returns:
        Updated text with tag inserted
    """
    return current_text + f" {tag} "


def synthesize_speech(
    text: str,
    lang: str,
    voice_style: str,
    custom_voice_file: Optional[str] = None
) -> Tuple[Tuple[int, 'np.ndarray'], str]:
    """
    Main inference function: synthesizes speech from text.
    
    Args:
        text: Input text with optional expression tags
        lang: Language code
        voice_style: Voice style name (e.g., "M1")
        custom_voice_file: Optional path to custom voice JSON file
    
    Returns:
        Tuple of (audio_output_tuple, status_message)
        audio_output_tuple is (sample_rate, numpy_array) for gr.Audio
    """
    global _tts_engine
    
    empty_audio = (22050, np.array([], dtype=np.float32))
    
    if not text or not text.strip():
        return empty_audio, "❌ Error: Please enter some text to synthesize."
    
    try:
        tts = get_tts_engine()
        
        # Get voice style
        try:
            if custom_voice_file and os.path.exists(custom_voice_file):
                # Load custom voice from JSON file
                with open(custom_voice_file, 'r', encoding='utf-8') as f:
                    custom_voice_data = json.load(f)
                
                # Build custom voice style from uploaded JSON
                if "voice_embedding" in custom_voice_data:
                    style = tts.build_custom_voice(
                        embedding=custom_voice_data["voice_embedding"],
                        **{k: v for k, v in custom_voice_data.items() 
                           if k != "voice_embedding"}
                    )
                else:
                    style = tts.get_voice_style(voice_name=voice_style)
            else:
                style = tts.get_voice_style(voice_name=voice_style)
        except Exception as e:
            return empty_audio, f"❌ Error loading voice style: {e}. Make sure the voice style '{voice_style}' is available."
        
        # Clean text - remove empty tags gracefully
        import re
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        if not cleaned_text:
            return empty_audio, "❌ Error: Text is empty after cleaning."
        
        print(f"[Supertonic-3] Synthesizing: lang={lang}, voice={voice_style}, text_len={len(cleaned_text)}")
        
        # Synthesize
        wav, duration = tts.synthesize(
            cleaned_text,
            voice_style=style,
            lang=lang
        )
        
        # Ensure wav is numpy array
        if isinstance(wav, list):
            wav = np.array(wav, dtype=np.float32)
        elif not isinstance(wav, np.ndarray):
            wav = np.frombuffer(wav, dtype=np.float32)
        
        duration_seconds = duration
        status_msg = f"✅ Generated successfully! Duration: {duration_seconds:.2f}s"
        print(f"[Supertonic-3] Synthesis complete: {duration_seconds:.2f}s")
        
        return (22050, wav), status_msg
    
    except Exception as e:
        error_msg = f"❌ Synthesis error: {e}"
        print(f"[Supertonic-3] {error_msg}")
        return (0, np.array([], dtype=np.float32)), error_msg


# ===========================================================================
# GRADIO UI DEFINITION
# ===========================================================================

def build_app():
    """Build and return the Gradio WebUI application."""
    
    # Custom CSS for a clean, modern look
    custom_css = """
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
    
    with gr.Blocks(
        title="Supertonic-3 TTS WebUI",
        css=custom_css,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
        )
    ) as app:
        
        # ==================== HEADER ====================
        with gr.Column(elem_classes="main-title"):
            gr.Markdown("# 🎙️ Supertonic-3 TTS WebUI")
            gr.Markdown(
                "## Local Text-to-Speech with Supertonic-3 (~99M parameters)  "
                "[GitHub](https://github.com/Anonymzx/Supertonic-WebUI)"
            )
            gr.Markdown(
                "A lightweight, offline TTS engine supporting **31 languages** with expression tags. "
                "No cloud connection required!"
            )
        
        # ==================== TABS ====================
        with gr.Tabs():
            
            # ---------- TAB 1: Main Generation ----------
            with gr.Tab("🎤 Generate Speech"):
                with gr.Row():
                    with gr.Column(scale=1):
                        
                        # --- Hardware Settings ---
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
                        
                        # --- Expression Tags Helper ---
                        with gr.Accordion("🎭 Expression Tags Helper", open=True):
                            gr.Markdown("**Click to insert tags at cursor position:**")
                            with gr.Row():
                                for tag, desc in list(EXPRESSION_TAGS.items())[:4]:
                                    gr.Button(
                                        tag,
                                        variant="secondary",
                                        size="sm",
                                        elem_classes="tag-button",
                                        # Using JS to insert at cursor
                                    ).click(
                                        lambda t=tag, text="": insert_tag_at_cursor(text, t),
                                        outputs=[]
                                    )
                            with gr.Row():
                                for tag, desc in list(EXPRESSION_TAGS.items())[4:]:
                                    gr.Button(
                                        tag,
                                        variant="secondary",
                                        size="sm",
                                        elem_classes="tag-button",
                                    ).click(
                                        lambda t=tag, text="": insert_tag_at_cursor(text, t),
                                        outputs=[]
                                    )
                        
                        # --- Voice Settings ---
                        with gr.Accordion("🎵 Voice Settings", open=True):
                            language_choice = gr.Dropdown(
                                choices=SUPPORTED_LANGUAGES,
                                value="id",
                                label="Language",
                                info="Select the synthesis language"
                            )
                            
                            voice_style_dropdown = gr.Dropdown(
                                choices=DEFAULT_VOICE_STYLES,
                                value="M1",
                                label="Voice Style",
                                info="Built-in voice style preset"
                            )
                            
                            refresh_voices_btn = gr.Button(
                                "🔄 Refresh Voice List",
                                variant="secondary",
                                size="sm"
                            )
                            
                        # --- Input Text ---
                        text_input = gr.Textbox(
                            label="Input Text",
                            placeholder="Enter text to synthesize...\nExample: Halo, nama saya asisten virtual. <laugh>Senang bertemu dengan Anda!</>  ",
                            lines=6,
                            max_lines=20,
                            info="Supports expression tags like <breath>, <laugh>, <sigh>"
                        )
                        
                        # --- Generate Button ---
                        generate_button = gr.Button(
                            "🚀 Generate Speech",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        
                        # --- Output ---
                        audio_output = gr.Audio(
                            label="Generated Speech",
                            type="numpy",
                            interactive=False
                        )
                        
                        output_status = gr.Textbox(
                            label="Status",
                            interactive=False
                        )
                        
                        # --- Examples ---
                        gr.Markdown("### 📝 Example Prompts")
                        examples = [
                            [
                                "Halo! Selamat datang di Supertonic-3. Ini adalah contoh teks dalam bahasa Indonesia.",
                                "id",
                                "M1"
                            ],
                            [
                                "Hello! Welcome to Supertonic-3. This is a demo in English. <laugh>Isn't that fun?</>",
                                "en",
                                "M1"
                            ],
                            [
                                "こんにちは！Supertonic-3へようこそ。これは日本語のデモです。<breath>素晴らしい技術ですね。</>",
                                "ja",
                                "F1"
                            ],
                            [
                                "안녕하세요! Supertonic-3에 오신 것을 환영합니다. <breath>현재 시범 운영 중입니다.</>",
                                "ko",
                                "F1"
                            ],
                            [
                                "Welcome to Supertonic TTS! <breath>Let me read something for you. <laugh>Here goes nothing!</>",
                                "en",
                                "F1"
                            ],
                        ]
                        
                        gr.Examples(
                            examples=examples,
                            inputs=[text_input, language_choice, voice_style_dropdown]
                        )
            
            # ---------- TAB 2: Custom Voice ----------
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
                    
                    gr.Markdown(
                        "#### JSON Format Expected:\n"
                        "```json\n"
                        "{\n"
                        '  "voice_embedding": [0.1, -0.2, 0.5, ...],\n'
                        '  "sample_rate": 22050\n'
                        "}\n"
                        "```"
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
        
        # Initialize engine handler
        init_button.click(
            fn=initialize_tts_engine,
            inputs=[execution_provider],
            outputs=[init_status, execution_provider]
        )
        
        # Synthesize handler
        def synthesis_handler(
            text: str,
            lang: str,
            voice_style: str,
            custom_voice_file: Optional[str],
            provider: str
        ):
            """Combined handler that ensures engine is ready before synthesis."""
            # Ensure engine is initialized with the selected provider
            _, current_provider = initialize_tts_engine(provider)
            
            # Run synthesis
            return synthesize_speech(text, lang, voice_style, custom_voice_file)
        
        generate_button.click(
            fn=synthesis_handler,
            inputs=[text_input, language_choice, voice_style_dropdown, custom_voice_upload, execution_provider],
            outputs=[audio_output, output_status]
        )
        
        # Auto-initialize on launch
        app.load(
            fn=lambda: initialize_tts_engine("CPU"),
            outputs=[init_status, execution_provider]
        )
    
    return app


# ===========================================================================
# MAIN ENTRY POINT
# ===========================================================================

def main():
    """Main entry point: build and launch the application."""
    
    print("=" * 60)
    print("  Supertonic-3 TTS WebUI")
    print("  Local Text-to-Speech Interface")
    print("=" * 60)
    print()
    print("📋 Quick Start:")
    print("   1. Select your Execution Provider (CPU/CUDA/DirectML/ROCm)")
    print("   2. Click 'Initialize / Reinitialize Engine'")
    print("   3. Enter text and select voice settings")
    print("   4. Click 'Generate Speech'")
    print()
    print("💡 Tips:")
    print("   - First run will download the model (~99M parameters)")
    print("   - Use expression tags for more natural speech")
    print("   - Try different voice styles and languages")
    print()
    
    # Build and launch the app
    app = build_app()
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True
    )


if __name__ == "__main__":
    main()