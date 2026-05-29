"""
Supertonic TTS WebUI - Configuration Module
Central configuration for the TTS backend application.
"""
import os
import logging
from pathlib import Path


# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
OUTPUTS_DIR = BASE_DIR / "outputs"
HISTORY_DIR = OUTPUTS_DIR / "history"
CACHE_DIR = OUTPUTS_DIR / "cache"
MODELS_DIR = OUTPUTS_DIR / "models"
LOGS_DIR = BACKEND_DIR / "logs"

# Ensure directories exist
for d in [OUTPUTS_DIR, HISTORY_DIR, CACHE_DIR, MODELS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Supertonic Model Configuration
SUPERTONIC_MODEL_NAME = os.getenv("SUPERTONIC_MODEL", "supertonic-3-voice-model")
SUPERTONIC_MODEL_PATH = MODELS_DIR / SUPERTONIC_MODEL_NAME
SUPERTONIC_MODEL_URL = os.getenv(
    "SUPERTONIC_MODEL_URL",
    "https://huggingface.co/supertonic/supertonic-3/resolve/main/model.onnx"
)

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
BACKEND_URL = f"http://{HOST}:{PORT}"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# TTS Default Settings
DEFAULT_VOICE = "F1"
DEFAULT_SPEED = 1.0
DEFAULT_QUALITY_STEPS = 32
DEFAULT_LANGUAGE = "na"  # "na" means auto-detect
SUPPORTED_LANGUAGES = ["na", "en", "id", "ja", "ko", "zh", "es", "fr", "de"]

# Available Voices
AVAILABLE_VOICES = {
    "F1": {"name": "Female Voice 1", "gender": "female", "description": "Natural female voice"},
    "F2": {"name": "Female Voice 2", "gender": "female", "description": "Soft female voice"},
    "F3": {"name": "Female Voice 3", "gender": "female", "description": "Bright female voice"},
    "F4": {"name": "Female Voice 4", "gender": "female", "description": "Deep female voice"},
    "F5": {"name": "Female Voice 5", "gender": "female", "description": "Warm female voice"},
    "M1": {"name": "Male Voice 1", "gender": "male", "description": "Deep male voice"},
    "M2": {"name": "Male Voice 2", "gender": "male", "description": "Natural male voice"},
    "M3": {"name": "Male Voice 3", "gender": "male", "description": "Soft male voice"},
    "M4": {"name": "Male Voice 4", "gender": "male", "description": "Authoritative male voice"},
    "M5": {"name": "Male Voice 5", "gender": "male", "description": "Warm male voice"},
}

# Expression tags to strip
EXPRESSION_TAGS = ["<laugh>", "<breath>", "<sigh>", "</laugh>", "</breath>", "</sigh>"]

# Audio Configuration
SAMPLE_RATE = 24000
AUDIO_FORMAT = "WAV"
AUDIO_EXTENSION = ".wav"
MAX_TEXT_LENGTH = 5000
CHUNK_SIZE = 500  # Characters per chunk for long text

# ONNX Runtime Configuration
ORT_OPTIONS = {
    "enable_cpu_mem_arena": False,
    "enable_mem_pattern": False,
    "execution_mode": "sequential",
    "graph_optimization_level": 99,  # Enable all optimizations
}

# Cache Configuration
CACHE_MAX_AGE_HOURS = 24
CACHE_MAX_SIZE_MB = 500

# History Configuration
HISTORY_MAX_ITEMS = 200
HISTORY_FILE = HISTORY_DIR / "history.json"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("supertonic-tts")
</write_to_file>