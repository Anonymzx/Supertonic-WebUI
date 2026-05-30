"""
Supertonic-3 WebUI - Local Text-to-Speech Interface
===================================================
A comprehensive Gradio-based WebUI for the Supertonic-3 TTS model.
Supports multiple execution providers (CPU, CUDA, DirectML, ROCm).
Includes Advanced Audio Post-Processing via Librosa.
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
    ("Arabic (ar)", "ar"),
    ("Bulgarian (bg)", "bg"),
    ("Croatian (hr)", "hr"),
    ("Czech (cs)", "cs"),
    ("Danish (da)", "da"),
    ("Dutch (nl)", "nl"),
    ("English (en)", "en"),
    ("Estonian (et)", "et"),
    ("Finnish (fi)", "fi"),
    ("French (fr)", "fr"),
    ("German (de)", "de"),
    ("Greek (el)", "el"),
    ("Hindi (hi)", "hi"),
    ("Hungarian (hu)", "hu"),
    ("Indonesian (id)", "id"),
    ("Italian (it)", "it"),
    ("Japanese (ja)", "ja"),
    ("Korean (ko)", "ko"),
    ("Latvian (lv)", "lv"),
    ("Lithuanian (lt)", "lt"),
    ("Polish (pl)", "pl"),
    ("Portuguese (pt)", "pt"),
    ("Romanian (ro)", "ro"),
    ("Russian (ru)", "ru"),
    ("Slovak (sk)", "sk"),
    ("Slovenian (sl)", "sl"),
    ("Spanish (es)", "es"),
    ("Swedish (sv)", "sv"),
    ("Turkish (tr)", "tr"),
    ("Ukrainian (uk)", "uk"),
    ("Vietnamese (vi)", "vi")
]

EXPRESSION_TAGS = {
    "<laugh>": "Laugh",
    "<breath>": "Breath",
    "<surprise>": "Surprise",
    "<sigh>": "Sigh",
    "<scream>": "Scream",
    "<throatclear>": "Throat Clear",
    "<sad>": "Sad",
    "<angry>": "Angry",
    "<cough>": "Cough",
    "<yawn>": "Yawn",
}


def insert_tag_at_cursor(current_text: str, tag: str) -> str:
    """Append an expression tag to the current text."""
    safe_text = current_text if current_text else ""
    return safe_text + f" {tag} "


# ===========================================================================
# MAIN SYNTHESIS & POST-PROCESSING LOGIC
# ===========================================================================

def synthesize_speech(
    text: str,
    lang: str,
    voice_style: str,
    speed: float,
    quality_steps: int,
    # Post-Processing Params
    trim_silence: bool,
    normalize_vol: bool,
    clarity_boost: bool,
    pitch_semitones: float,
    post_time_stretch: float,
    chorus_effect: bool,
    # System
    custom_voice_file: Optional[str] = None
) -> Tuple[Tuple[int, 'np.ndarray'], str]:
    """Main inference function with Librosa Audio Post-Processing."""
    global _tts_engine
    
    empty_audio = (22050, np.array([], dtype=np.float32))
    sr = 44100 # Default Supertonic-3 Sample Rate
    
    if not text or not text.strip():
        return empty_audio, "❌ Error: Please enter some text to synthesize."
    
    try:
        tts = get_tts_engine()
        
        # 1. Load Voice Style
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
            return empty_audio, f"❌ Error loading voice style: {e}."
        
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        if not cleaned_text:
            return empty_audio, "❌ Error: Text is empty after cleaning."
        
        print(f"\n[Supertonic-3] Synthesizing: lang={lang}, voice={voice_style}, AI_speed={speed}, quality={quality_steps}")
        
        # 2. Native AI Synthesis
        wav, duration = tts.synthesize(
            text=cleaned_text,
            voice_style=style,
            lang=lang,
            speed=speed,
            total_steps=quality_steps
        )
        
        # Ensure 1D Numpy Array Float32 for Librosa
        if isinstance(wav, list):
            wav = np.array(wav, dtype=np.float32)
        elif not isinstance(wav, np.ndarray):
            wav = np.frombuffer(wav, dtype=np.float32)
            
        if len(wav.shape) > 1:
            wav = wav.flatten()
            
        # 3. Audio Post-Processing Pipeline (Librosa)
        status_addon = ""
        librosa_used = trim_silence or normalize_vol or clarity_boost or (pitch_semitones != 0) or (post_time_stretch != 1.0) or chorus_effect
        
        if librosa_used:
            try:
                import librosa
                print("[Librosa] Post-processing pipeline started...")
                
                # A. Trim Silence
                if trim_silence:
                    wav, _ = librosa.effects.trim(wav, top_db=25)
                    print("  -> Trimmed silence")
                
                # B. Voice Clarity / Pre-emphasis (Sharpen High Frequencies)
                if clarity_boost:
                    wav = librosa.effects.preemphasis(wav, coef=0.97)
                    print("  -> Clarity boost applied")
                    
                # C. Pitch Shift
                if pitch_semitones != 0:
                    wav = librosa.effects.pitch_shift(y=wav, sr=sr, n_steps=float(pitch_semitones))
                    print(f"  -> Pitch shifted by {pitch_semitones} semitones")
                    
                # D. Time Stretch (Post-Processing)
                if post_time_stretch != 1.0:
                    wav = librosa.effects.time_stretch(y=wav, rate=post_time_stretch)
                    print(f"  -> Time stretched by {post_time_stretch}x")
                    
                # E. Chorus / Sci-Fi Layering Effect
                if chorus_effect:
                    wav_pitch_shifted = librosa.effects.pitch_shift(y=wav, sr=sr, n_steps=-2)
                    delay_samples = int(sr * 0.03) # 30ms delay
                    wav_delayed = np.pad(wav_pitch_shifted, (delay_samples, 0), mode='constant')
                    
                    min_len = min(len(wav), len(wav_delayed))
                    wav = (wav[:min_len] * 0.7) + (wav_delayed[:min_len] * 0.5)
                    print("  -> Chorus effect applied")
                
                # F. Audio Normalization (Do this last to prevent clipping)
                if normalize_vol:
                    wav = librosa.util.normalize(wav)
                    print("  -> Audio normalized")
                
                status_addon = "\n✨ Post-processing applied successfully."
                
            except ImportError:
                warning_msg = "WARNING: 'librosa' is not installed. All post-processing bypassed. Run 'pip install librosa'."
                print(f"[Librosa] {warning_msg}")
                status_addon = "\n⚠️ Post-processing ignored (librosa not installed)."

        # 4. Final Conversions for Gradio Output
        if wav.dtype == np.float32 or wav.dtype == np.float64:
            # Ensure it fits into int16 range to avoid struct.error 'H' format
            wav_clipped = np.clip(wav, -1.0, 1.0)
            wav = np.int16(wav_clipped * 32767.0)
            
        final_duration_seconds = len(wav) / sr
            
        status_msg = f"✅ Synthesis Complete!\nFinal Duration: {final_duration_seconds:.2f}s{status_addon}"
        print(f"[Pipeline] Final audio ready ({final_duration_seconds:.2f}s)")
        
        return (sr, wav), status_msg
    
    except Exception as e:
        error_msg = f"❌ Pipeline error: {e}"
        print(f"[Pipeline Error] {error_msg}")
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
.section-header {
    margin-top: 15px;
    margin-bottom: 5px;
    font-weight: bold;
    color: #3b82f6;
    font-size: 1.1em;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 5px;
}
"""

def build_app():
    """Build and return the Gradio WebUI application."""
    
    with gr.Blocks(title="Supertonic-3 TTS WebUI", css=CUSTOM_CSS) as app:
        
        with gr.Column(elem_classes="main-title"):
            gr.Markdown("# 🎙️ Supertonic-3 TTS WebUI")
            gr.Markdown(
                "## Local Text-to-Speech with Advanced Audio Pipeline  \n"
                "[GitHub Repository](https://github.com/Anonymzx/Supertonic-WebUI)"
            )
        
        with gr.Tabs():
            
            # ---------------------------------------------------------
            # TAB 1: GENERATION & PROCESSING
            # ---------------------------------------------------------
            with gr.Tab("🎤 Generate & Process"):
                with gr.Row():
                    
                    # LEFT COLUMN - ALL CONTROLS
                    with gr.Column(scale=1):
                        
                        with gr.Accordion("⚙️ Engine & Hardware", open=False):
                            execution_provider = gr.Dropdown(
                                choices=["CPU", "CUDA", "DirectML", "ROCm"],
                                value="CPU",
                                label="Execution Provider"
                            )
                            init_button = gr.Button("Initialize / Reinitialize Engine", variant="secondary")
                            init_status = gr.Textbox(label="Engine Status", interactive=False)
                        
                        gr.Markdown("<div class='section-header'>Native AI Parameters</div>")
                        
                        with gr.Row():
                            language_choice = gr.Dropdown(
                                choices=SUPPORTED_LANGUAGES,
                                value="na",
                                label="Language",
                                info="Source language"
                            )
                            voice_style_dropdown = gr.Dropdown(
                                choices=DEFAULT_VOICE_STYLES,
                                value="M1",
                                label="Voice Style",
                                info="Preset AI model"
                            )
                        
                        with gr.Row():
                            speed_slider = gr.Slider(
                                minimum=0.5, maximum=2.0, value=1.0, step=0.05, 
                                label="AI Reading Speed",
                                info="Controls how fast the AI naturally speaks"
                            )
                            quality_slider = gr.Slider(
                                minimum=5, maximum=12, value=8, step=1, 
                                label="AI Quality (Total Steps)",
                                info="Higher = Better quality but slower to generate"
                            )
                        
                        text_input = gr.Textbox(
                            label="Input Text",
                            placeholder="Enter text to synthesize...\nExample: Halo, ini suara saya! <laugh> Keren kan? <surprise>",
                            lines=4,
                            max_lines=20
                        )
                        
                        with gr.Accordion("🎭 Expression Tags Helper", open=False):
                            tag_items = list(EXPRESSION_TAGS.items())
                            with gr.Row():
                                for tag, desc in tag_items[:5]:
                                    gr.Button(tag, variant="secondary", size="sm", elem_classes="tag-button").click(
                                        fn=lambda current, t=tag: insert_tag_at_cursor(current, t), inputs=[text_input], outputs=[text_input]
                                    )
                            with gr.Row():
                                for tag, desc in tag_items[5:]:
                                    gr.Button(tag, variant="secondary", size="sm", elem_classes="tag-button").click(
                                        fn=lambda current, t=tag: insert_tag_at_cursor(current, t), inputs=[text_input], outputs=[text_input]
                                    )
                                    
                        # --- POST PROCESSING SECTION IN MAIN TAB ---
                        with gr.Accordion("🎛️ Audio Post-Processing (Librosa)", open=True):
                            gr.Markdown("*These effects are applied after the AI generates the raw audio.*")
                            
                            with gr.Row():
                                with gr.Column():
                                    trim_silence_cb = gr.Checkbox(label="✂️ Auto-Trim Silence", value=True)
                                    normalize_vol_cb = gr.Checkbox(label="🔊 Normalize Volume", value=True)
                                    clarity_boost_cb = gr.Checkbox(label="🎙️ Clarity Boost (Pre-emphasis)", value=False)
                                    chorus_cb = gr.Checkbox(label="🤖 Sci-Fi / Chorus Effect", value=False)
                                
                                with gr.Column():
                                    pitch_slider = gr.Slider(minimum=-12, maximum=12, value=0, step=1, label="Pitch Shift (Semitones)", info="Negative = Deeper, Positive = Higher")
                                    post_time_stretch = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.05, label="Post-Time Stretch", info="Speeds up/slows down without affecting reading rhythm")
                        
                        generate_button = gr.Button("🚀 Generate Speech", variant="primary", size="lg")
                        
                    # RIGHT COLUMN - OUTPUT
                    with gr.Column(scale=1):
                        gr.Markdown("<div class='section-header'>Final Output</div>")
                        
                        audio_output = gr.Audio(
                            label="Final Rendered Speech",
                            type="numpy",
                            interactive=False
                        )
                        output_status = gr.Textbox(label="Processing Status", interactive=False, lines=2)
                        
            # ---------------------------------------------------------
            # TAB 2: CUSTOM VOICE
            # ---------------------------------------------------------
            with gr.Tab("🎨 Custom Voice"):
                with gr.Column():
                    gr.Markdown("### Custom Voice Upload")
                    custom_voice_upload = gr.File(label="Upload Custom Voice JSON", file_types=[".json"])
        
        # ==================== EVENT HANDLERS ====================
        
        init_button.click(
            fn=initialize_tts_engine,
            inputs=[execution_provider],
            outputs=[init_status, execution_provider]
        )
        
        def pipeline_handler(
            # Native
            text, lang, voice_style, ai_speed, quality,
            # Post Pro
            trim, norm, clarify, pitch, stretch, chorus,
            # Voice
            custom_voice, provider
        ):
            _, current_provider = initialize_tts_engine(provider)
            return synthesize_speech(
                text, lang, voice_style, ai_speed, quality,
                trim, norm, clarify, pitch, stretch, chorus,
                custom_voice
            )
        
        generate_button.click(
            fn=pipeline_handler,
            inputs=[
                text_input, language_choice, voice_style_dropdown, speed_slider, quality_slider,
                trim_silence_cb, normalize_vol_cb, clarity_boost_cb, pitch_slider, post_time_stretch, chorus_cb,
                custom_voice_upload, execution_provider
            ],
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
    print("  Supertonic-3 TTS WebUI Pipeline")
    print("  Native AI + Librosa Post-Processing")
    print("=" * 60)
    
    app = build_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True,
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="gray")
    )