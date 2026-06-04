"""
Supertonic-3 WebUI - Local Text-to-Speech Interface
===================================================
A comprehensive Gradio-based WebUI for the Supertonic-3 TTS model.
Supports multiple execution providers, Librosa Post-Processing, and Presets.
"""

import gradio as gr
import numpy as np
import os
import json
import re
from typing import Tuple, Optional


# ===========================================================================
# GLOBAL TTS ENGINE INITIALIZATION & PRESETS SETUP
# ===========================================================================

_tts_engine = None
_tts_config = {"provider": "CPU"}

PRESETS_DIR = "presets"
os.makedirs(PRESETS_DIR, exist_ok=True)


def get_preset_list():
    presets = [f.replace(".json", "") for f in os.listdir(PRESETS_DIR) if f.endswith(".json")]
    return presets if presets else ["default"]


def get_execution_providers(provider_name: str):
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
    else:
        print("[Supertonic-3] Using CPUExecutionProvider")
        return ["CPUExecutionProvider"]


def initialize_tts_engine(provider: str = "CPU"):
    global _tts_engine, _tts_config
    try:
        _tts_config["provider"] = provider
        print(f"[Supertonic-3] Initializing TTS engine with provider: {provider}...")
        from supertonic import TTS
        _tts_engine = TTS(auto_download=True)
        _tts_engine._provider = provider
        print(f"[Supertonic-3] TTS engine initialized successfully!")
        return f"✅ Engine ready ({provider}).", provider
    except Exception as e:
        error_msg = f"❌ Failed to initialize: {e}"
        print(error_msg)
        return error_msg, provider


def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        initialize_tts_engine(_tts_config["provider"])
    return _tts_engine


# ===========================================================================
# PRESET SAVE / LOAD LOGIC
# ===========================================================================

def save_preset(name, provider, lang, voice, speed, quality, trim, norm, clarity, pitch, stretch, chorus, text):
    if not name or name.strip() == "": name = "default"
    name = re.sub(r'[\\/*?:"<>|]', "", name.strip())
    
    filepath = os.path.join(PRESETS_DIR, f"{name}.json")
    data = {
        "provider": provider, "language": lang, "voice_style": voice,
        "speed": speed, "quality": quality, "trim_silence": trim,
        "normalize_vol": norm, "clarity_boost": clarity, "pitch": pitch,
        "time_stretch": stretch, "chorus": chorus, "text": text
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    return gr.update(choices=get_preset_list(), value=name), gr.update(value=name), f"✅ Preset '{name}' saved!"


def load_preset(name):
    if not name or name.strip() == "": name = "default"
    filepath = os.path.join(PRESETS_DIR, f"{name}.json")
    
    defaults = {
        "provider": "CPU", "language": "na", "voice_style": "M1", 
        "speed": 1.0, "quality": 8, "trim_silence": True, 
        "normalize_vol": True, "clarity_boost": False, "pitch": 0, 
        "time_stretch": 1.0, "chorus": False, "text": ""
    }
    
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                defaults.update(data)
                status = f"✅ Preset '{name}' loaded!"
            except Exception as e:
                status = f"❌ Error reading preset: {e}"
    else:
        status = f"⚠️ Preset '{name}' not found."
        
    return (
        defaults["provider"], defaults["language"], defaults["voice_style"], 
        defaults["speed"], defaults["quality"], defaults["trim_silence"], 
        defaults["normalize_vol"], defaults["clarity_boost"], defaults["pitch"], 
        defaults["time_stretch"], defaults["chorus"], defaults["text"],
        gr.update(value=name), status
    )


# ===========================================================================
# VOICE STYLE & LANGUAGE HELPERS
# ===========================================================================

DEFAULT_VOICE_STYLES = ["M1", "M2", "F1", "F2", "M3", "M4", "M5", "F3", "F4", "F5"]

SUPPORTED_LANGUAGES = [
    ("Auto-Detect (Language Agnostic)", "na"), ("Arabic (ar)", "ar"), ("Bulgarian (bg)", "bg"), 
    ("Croatian (hr)", "hr"), ("Czech (cs)", "cs"), ("Danish (da)", "da"), ("Dutch (nl)", "nl"), 
    ("English (en)", "en"), ("Estonian (et)", "et"), ("Finnish (fi)", "fi"), ("French (fr)", "fr"), 
    ("German (de)", "de"), ("Greek (el)", "el"), ("Hindi (hi)", "hi"), ("Hungarian (hu)", "hu"), 
    ("Indonesian (id)", "id"), ("Italian (it)", "it"), ("Japanese (ja)", "ja"), ("Korean (ko)", "ko"), 
    ("Latvian (lv)", "lv"), ("Lithuanian (lt)", "lt"), ("Polish (pl)", "pl"), ("Portuguese (pt)", "pt"), 
    ("Romanian (ro)", "ro"), ("Russian (ru)", "ru"), ("Slovak (sk)", "sk"), ("Slovenian (sl)", "sl"), 
    ("Spanish (es)", "es"), ("Swedish (sv)", "sv"), ("Turkish (tr)", "tr"), ("Ukrainian (uk)", "uk"), 
    ("Vietnamese (vi)", "vi")
]

EXPRESSION_TAGS = {
    "<laugh>": "Laugh", "<breath>": "Breath", "<surprise>": "Surprise", "<sigh>": "Sigh", 
    "<scream>": "Scream", "<throatclear>": "Throat", "<sad>": "Sad", "<angry>": "Angry", 
    "<cough>": "Cough", "<yawn>": "Yawn",
}

def insert_tag_at_cursor(current_text: str, tag: str) -> str:
    safe_text = current_text if current_text else ""
    return safe_text + f" {tag} "


# ===========================================================================
# MAIN SYNTHESIS & POST-PROCESSING LOGIC
# ===========================================================================

def synthesize_speech(text, lang, voice_style, speed, quality_steps, trim_silence, normalize_vol, clarity_boost, pitch_semitones, post_time_stretch, chorus_effect, custom_voice_file):
    global _tts_engine
    empty_audio = (22050, np.array([], dtype=np.float32))
    sr = 44100 
    
    if not text or not text.strip(): return empty_audio, "❌ Error: Please enter some text."
    
    try:
        tts = get_tts_engine()
        try:
            if custom_voice_file and os.path.exists(custom_voice_file):
                with open(custom_voice_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "voice_embedding" in data:
                    style = tts.build_custom_voice(embedding=data["voice_embedding"], **{k: v for k, v in data.items() if k != "voice_embedding"})
                else: style = tts.get_voice_style(voice_name=voice_style)
            else: style = tts.get_voice_style(voice_name=voice_style)
        except Exception as e: return empty_audio, f"❌ Error loading voice: {e}."
        
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        wav, duration = tts.synthesize(text=cleaned_text, voice_style=style, lang=lang, speed=speed, total_steps=quality_steps)
        
        if isinstance(wav, list): wav = np.array(wav, dtype=np.float32)
        elif not isinstance(wav, np.ndarray): wav = np.frombuffer(wav, dtype=np.float32)
        if len(wav.shape) > 1: wav = wav.flatten()
            
        status_addon = ""
        if trim_silence or normalize_vol or clarity_boost or (pitch_semitones != 0) or (post_time_stretch != 1.0) or chorus_effect:
            try:
                import librosa
                if trim_silence: wav, _ = librosa.effects.trim(wav, top_db=25)
                if clarity_boost: wav = librosa.effects.preemphasis(wav, coef=0.97)
                if pitch_semitones != 0: wav = librosa.effects.pitch_shift(y=wav, sr=sr, n_steps=float(pitch_semitones))
                if post_time_stretch != 1.0: wav = librosa.effects.time_stretch(y=wav, rate=post_time_stretch)
                if chorus_effect:
                    wav_ps = librosa.effects.pitch_shift(y=wav, sr=sr, n_steps=-2)
                    wav_delayed = np.pad(wav_ps, (int(sr * 0.03), 0), mode='constant')
                    min_len = min(len(wav), len(wav_delayed))
                    wav = (wav[:min_len] * 0.7) + (wav_delayed[:min_len] * 0.5)
                if normalize_vol: wav = librosa.util.normalize(wav)
                status_addon = " | ✨ Effects Applied"
            except ImportError:
                status_addon = " | ⚠️ Librosa missing"

        if wav.dtype in [np.float32, np.float64]:
            wav = np.int16(np.clip(wav, -1.0, 1.0) * 32767.0)
            
        return (sr, wav), f"✅ Success! Duration: {len(wav)/sr:.2f}s{status_addon}"
    except Exception as e:
        return (0, np.array([], dtype=np.float32)), f"❌ Error: {e}"


# ===========================================================================
# GRADIO UI DEFINITION (ADAPTIVE THEME)
# ===========================================================================

# CSS explicitly uses Gradio's native theme variables to support both Light & Dark modes flawlessly
CUSTOM_CSS = """
.main-title { text-align: center; padding: 5px 0 15px 0; border-bottom: 1px solid var(--border-color-primary); margin-bottom: 20px;}
.subtitle { text-align: center; font-size: 15px; color: var(--body-text-color-subdued); margin-top: -10px;}
.header-links { text-align: center; margin-top: 10px; font-size: 14px; }
.header-links a { margin: 0 12px; text-decoration: none; font-weight: bold; color: var(--color-accent);}
.header-links a:hover { text-decoration: underline; }
.tag-button { margin: 2px !important; flex-grow: 1; }
.panel-box { background: var(--background-fill-secondary); padding: 15px; border-radius: 8px; border: 1px solid var(--border-color-primary);}
"""

def build_app():
    with gr.Blocks(title="Supertonic-3 TTS") as app:
        
        with gr.Column(elem_classes="main-title"):
            gr.Markdown("# 🎙️ Supertonic-3 TTS Studio")
            gr.Markdown("<p class='subtitle'><br>Local, Offline, Expressive Text-to-Speech Engine</p>")
            
            gr.Markdown("<div class='header-links'><a href='https://github.com/Anonymzx/Supertonic-WebUI' target='_blank'>⭐ GitHub Repository</a> | <a href='https://ko-fi.com/anonymzx' target='_blank'>☕ Buy Me a Coffee</a></div>")
        
        with gr.Row():
            
            # ==========================================
            # LEFT COLUMN: THE WORKSPACE (SCALE=2)
            # ==========================================
            with gr.Column(scale=2):
                gr.Markdown("### 📝 Text Input & Generation")
                
                text_input = gr.Textbox(
                    label="", 
                    placeholder="Type your script here...\nExample: Halo, apa kabar? <laugh> Senang bertemu denganmu!", 
                    lines=8, 
                    max_lines=20,
                    show_label=False
                )
                
                with gr.Accordion("🎭 Expression Tags", open=True):
                    tag_items = list(EXPRESSION_TAGS.items())
                    with gr.Row():
                        for tag, desc in tag_items[:5]:
                            gr.Button(tag, variant="secondary", size="sm", elem_classes="tag-button").click(fn=lambda current, t=tag: insert_tag_at_cursor(current, t), inputs=[text_input], outputs=[text_input])
                    with gr.Row():
                        for tag, desc in tag_items[5:]:
                            gr.Button(tag, variant="secondary", size="sm", elem_classes="tag-button").click(fn=lambda current, t=tag: insert_tag_at_cursor(current, t), inputs=[text_input], outputs=[text_input])
                
                generate_button = gr.Button("🚀 Generate Audio", variant="primary", size="lg")
                
                gr.Markdown("### 🎧 Output")
                audio_output = gr.Audio(label="", type="numpy", interactive=False, show_label=False)
                output_status = gr.Textbox(label="Status", interactive=False, lines=1)

            # ==========================================
            # RIGHT COLUMN: THE CONTROL PANEL (SCALE=1)
            # ==========================================
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Control Panel")
                
                # --- ACCORDION 1: AI & VOICE ---
                with gr.Accordion("🎛️ Voice Settings", open=True):
                    language_choice = gr.Dropdown(choices=SUPPORTED_LANGUAGES, value="na", label="Language")
                    voice_style_dropdown = gr.Dropdown(choices=DEFAULT_VOICE_STYLES, value="M1", label="Preset Voice Style")
                    speed_slider = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.05, label="AI Reading Speed")
                    quality_slider = gr.Slider(minimum=5, maximum=12, value=8, step=1, label="Quality (Steps)")
                    custom_voice_upload = gr.File(label="Upload Custom JSON (Optional)", file_types=[".json"])
                
                # --- ACCORDION 2: POST-PROCESSING ---
                with gr.Accordion("🪄 Post-Processing (Librosa)", open=False):
                    gr.Markdown("*Applied after AI generation*")
                    pitch_slider = gr.Slider(minimum=-12, maximum=12, value=0, step=1, label="Pitch (Semitones)")
                    post_time_stretch = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, step=0.05, label="Time Stretch")
                    trim_silence_cb = gr.Checkbox(label="✂️ Auto-Trim Silence", value=True)
                    normalize_vol_cb = gr.Checkbox(label="🔊 Normalize Volume", value=True)
                    clarity_boost_cb = gr.Checkbox(label="🎙️ Clarity Boost", value=False)
                    chorus_cb = gr.Checkbox(label="🤖 Sci-Fi Effect", value=False)
                
                # --- ACCORDION 3: SYSTEM & PRESETS ---
                with gr.Accordion("💾 System & Presets", open=False):
                    gr.Markdown("**Saved Profiles**")
                    preset_dropdown = gr.Dropdown(choices=get_preset_list(), value="default" if "default" in get_preset_list() else None, label="Load Preset", show_label=False)
                    load_btn = gr.Button("📂 Load Profile", variant="secondary", size="sm")
                    
                    gr.Markdown("---")
                    preset_name_input = gr.Textbox(value="default", label="Save As (Name)", show_label=False, placeholder="Preset name...")
                    save_btn = gr.Button("💾 Save Profile", variant="secondary", size="sm")
                    preset_status = gr.Textbox(show_label=False, interactive=False, lines=1)
                    
                    gr.Markdown("---")
                    gr.Markdown("**Hardware Backend**")
                    execution_provider = gr.Dropdown(choices=["CPU", "CUDA", "DirectML", "ROCm"], value="CPU", show_label=False)
                    init_button = gr.Button("🔄 Reinitialize Engine", variant="secondary", size="sm")
                    init_status = gr.Textbox(show_label=False, interactive=False, lines=1)

        # ==================== EVENT HANDLERS ====================
        ui_state_components = [
            execution_provider, language_choice, voice_style_dropdown, 
            speed_slider, quality_slider, trim_silence_cb, normalize_vol_cb, 
            clarity_boost_cb, pitch_slider, post_time_stretch, chorus_cb, text_input
        ]

        save_btn.click(fn=save_preset, inputs=[preset_name_input] + ui_state_components, outputs=[preset_dropdown, preset_name_input, preset_status])
        load_btn.click(fn=load_preset, inputs=[preset_dropdown], outputs=ui_state_components + [preset_name_input, preset_status])
        init_button.click(fn=initialize_tts_engine, inputs=[execution_provider], outputs=[init_status, execution_provider])
        
        def pipeline_handler(text, lang, voice, ai_spd, qual, trim, norm, clr, pch, strch, chrs, cust_voice, prov):
            _, current_prov = initialize_tts_engine(prov)
            return synthesize_speech(text, lang, voice, ai_spd, qual, trim, norm, clr, pch, strch, chrs, cust_voice)
        
        generate_button.click(
            fn=pipeline_handler,
            inputs=[text_input, language_choice, voice_style_dropdown, speed_slider, quality_slider, trim_silence_cb, normalize_vol_cb, clarity_boost_cb, pitch_slider, post_time_stretch, chorus_cb, custom_voice_upload, execution_provider],
            outputs=[audio_output, output_status]
        )
        
        def app_startup():
            vals = load_preset("default") 
            init_msg, _ = initialize_tts_engine(vals[0])
            return (*vals[:12], init_msg)

        app.load(fn=app_startup, outputs=ui_state_components + [init_status])
    
    return app


if __name__ == "__main__":
    print("=" * 60)
    print("  Supertonic-3 TTS WebUI Pipeline")
    print("=" * 60)
    app = build_app()
    app.launch(server_name="localhost", server_port=7860, share=False, show_error=True, inbrowser=True, css=CUSTOM_CSS, theme=gr.themes.Soft(primary_hue="blue", secondary_hue="gray"))