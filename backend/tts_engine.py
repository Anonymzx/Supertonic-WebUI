"""
Supertonic TTS WebUI - TTS Engine Module
Core text-to-speech generation using official Supertonic 3 SDK.
Uses `TTS` class with auto-download and HuggingFace caching.
"""
import re
import time
import hashlib
import logging
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path

import numpy as np
import soundfile as sf

from config import (
    SAMPLE_RATE, AUDIO_EXTENSION, OUTPUTS_DIR,
    EXPRESSION_TAGS, CHUNK_SIZE, MAX_TEXT_LENGTH,
    AVAILABLE_VOICES, CACHE_DIR, CACHE_MAX_AGE_HOURS,
)
from execution_providers import (
    detect_execution_providers,
    get_provider_info,
)

logger = logging.getLogger("supertonic-tts.engine")


class TextPreprocessor:
    """Handles text preprocessing for TTS."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text for TTS processing."""
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove expression tags
        for tag in EXPRESSION_TAGS:
            text = text.replace(tag, '')
        return text

    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
        """Split long text into manageable chunks."""
        if len(text) <= chunk_size:
            return [text]
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection for Indonesian/English."""
        id_patterns = [
            r'\byang\b', r'\bdengan\b', r'\bdan\b', r'\bdi\b',
            r'\btidak\b', r'\bini\b', r'\bitu\b', r'\bada\b',
            r'\bakan\b', r'\bdapat\b', r'\bdari\b', r'\bdia\b',
            r'\bke\b', r'\boleh\b', r'\bpada\b', r'\buntuk\b',
            r'\bsaya\b', r'\bkamu\b', r'\bkami\b', r'\bmereka\b',
        ]
        id_score = sum(1 for p in id_patterns if re.search(p, text.lower()))
        return "id" if id_score >= 3 else "en"


class AudioCache:
    """Manages audio file caching to avoid regenerating identical requests."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, text: str, voice: str, speed: float,
                       quality_steps: int, language: str) -> str:
        content = f"{text}:{voice}:{speed}:{quality_steps}:{language}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, text: str, voice: str, speed: float,
            quality_steps: int, language: str) -> Optional[Path]:
        cache_key = self._get_cache_key(text, voice, speed, quality_steps, language)
        cache_file = self.cache_dir / f"{cache_key}{AUDIO_EXTENSION}"
        if cache_file.exists():
            age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
            if age_hours <= CACHE_MAX_AGE_HOURS:
                logger.info(f"Cache hit: {cache_key}")
                return cache_file
            else:
                cache_file.unlink(missing_ok=True)
        return None

    def set(self, text: str, voice: str, speed: float,
            quality_steps: int, language: str, audio_data: np.ndarray,
            sample_rate: int = SAMPLE_RATE) -> Path:
        cache_key = self._get_cache_key(text, voice, speed, quality_steps, language)
        cache_file = self.cache_dir / f"{cache_key}{AUDIO_EXTENSION}"
        sf.write(str(cache_file), audio_data, sample_rate)
        return cache_file

    def clear_expired(self) -> int:
        removed = 0
        for cache_file in self.cache_dir.glob(f"*{AUDIO_EXTENSION}"):
            age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
            if age_hours > CACHE_MAX_AGE_HOURS:
                cache_file.unlink()
                removed += 1
        return removed

    @property
    def size_mb(self) -> float:
        total_bytes = sum(f.stat().st_size for f in self.cache_dir.glob(f"*{AUDIO_EXTENSION}"))
        return total_bytes / (1024 * 1024)

    @property
    def count(self) -> int:
        return len(list(self.cache_dir.glob(f"*{AUDIO_EXTENSION}")))


class SupertonicTTS:
    """
    Core TTS engine using official Supertonic 3 SDK.
    Uses TTS class with auto_download=True for HuggingFace caching.
    """

    def __init__(self):
        self.tts = None
        self.voice_styles: dict = {}
        self.providers = ["CPUExecutionProvider"]
        self.provider_info = {}
        self.model_loaded = False
        self.cache = AudioCache()
        self.text_processor = TextPreprocessor()
        self._load_error: Optional[str] = None

        # Detect execution providers on init
        self._setup_providers()

    def _setup_providers(self) -> None:
        """Detect and configure execution providers."""
        try:
            logger.info("Detecting available execution providers...")
            self.providers = detect_execution_providers()
            self.provider_info = get_provider_info()
            logger.info(f"Providers: {self.providers} | GPU: {self.provider_info.get('gpu_available')}")
        except Exception as e:
            logger.warning(f"Provider detection failed: {e}")
            self.providers = ["CPUExecutionProvider"]

    def load_model(self) -> bool:
        """
        Load the Supertonic 3 model using official SDK.
        Uses auto_download=True for automatic HuggingFace caching.

        Returns:
            True if model loaded successfully
        """
        try:
            logger.info("Loading Supertonic 3 via official SDK (auto_download=True)...")

            # Import supertonic SDK
            from supertonic import TTS

            # Initialize TTS with auto-download enabled
            if "DmlExecutionProvider" in self.providers:
                logger.info("Using DirectML execution provider for AMD GPU")
                self.tts = TTS(
                    auto_download=True,
                    providers=["DmlExecutionProvider", "CPUExecutionProvider"],
                )
            else:
                logger.info("Using CPU execution provider")
                self.tts = TTS(
                    auto_download=True,
                    providers=["CPUExecutionProvider"],
                )

            # Pre-cache voice styles for all available voices
            voice_ids = list(AVAILABLE_VOICES.keys())
            for vid in voice_ids:
                try:
                    style = self.tts.get_voice_style(voice_name=vid)
                    self.voice_styles[vid] = style
                    logger.info(f"Cached voice style: {vid}")
                except Exception as e:
                    logger.warning(f"Could not cache voice style {vid}: {e}")

            self.model_loaded = True
            self._load_error = None
            logger.info("[OK] Supertonic 3 model loaded successfully!")
            return True

        except ImportError:
            self._load_error = (
                "Supertonic SDK not installed. "
                "Run: pip install supertonic"
            )
            logger.error(self._load_error)
            return False

        except Exception as e:
            self._load_error = str(e)
            logger.error(f"[FAIL] Failed to load model via SDK: {e}", exc_info=True)
            return False

    def get_voice_style(self, voice: str):
        """Get cached voice style or fetch it live."""
        if voice in self.voice_styles:
            return self.voice_styles[voice]
        if self.tts is not None:
            try:
                style = self.tts.get_voice_style(voice_name=voice)
                self.voice_styles[voice] = style
                return style
            except Exception as e:
                logger.error(f"[FAIL] Failed to get voice style {voice}: {e}")
                raise
        raise RuntimeError("Model not loaded")

    def generate(
        self,
        text: str,
        voice: str = "F1",
        speed: float = 1.0,
        quality_steps: int = 8,
        language: str = "na",
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate speech audio from text using official Supertonic SDK.

        Args:
            text: Input text to synthesize
            voice: Voice ID (F1-F5, M1-M5)
            speed: Speech speed multiplier (0.5-2.0)
            quality_steps: Number of sampling steps (8-64)
            language: Language code (na=auto, id=Indonesian, en=English)

        Returns:
            Tuple of (audio_array, metadata_dict)
        """
        start_time = time.time()

        if not self.tts or not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Clean and prepare text
        text = self.text_processor.clean_text(text)
        if not text:
            raise ValueError("Empty text after preprocessing")

        # Auto-detect language if set to auto
        if language == "na":
            language = self.text_processor.detect_language(text)
        logger.info(f"Detected language: {language}")

        # Check cache first
        cached = self.cache.get(text, voice, speed, quality_steps, language)
        if cached:
            audio, sr = sf.read(str(cached))
            inference_time = (time.time() - start_time) * 1000
            duration_ms = int(len(audio) / SAMPLE_RATE * 1000)
            metadata = {
                "inference_ms": int(inference_time),
                "duration_ms": duration_ms,
                "cached": True,
            }
            logger.info(f"Cache hit for: {text[:50]}...")
            return audio, metadata

        # Get voice style and synthesize
        try:
            voice_style = self.get_voice_style(voice)

            logger.info(
                f"Synthesizing: voice={voice}, lang={language}, "
                f"steps={quality_steps}, speed={speed}"
            )

            # Official SDK synthesize call
            wav, duration = self.tts.synthesize(
                text=text,
                lang=language,
                voice_style=voice_style,
                total_steps=quality_steps,
                speed=speed,
            )

            # Convert to numpy array if needed
            audio = np.array(wav, dtype=np.float32)
            if audio.ndim > 1:
                audio = audio.flatten()

            inference_time = (time.time() - start_time) * 1000
            duration_ms = int(duration * 1000) if isinstance(duration, float) else int(len(audio) / SAMPLE_RATE * 1000)

            # Cache the result
            self.cache.set(text, voice, speed, quality_steps, language, audio)

            metadata = {
                "inference_ms": int(inference_time),
                "duration_ms": duration_ms,
                "cached": False,
            }

            logger.info(
                f"Generated {duration_ms}ms audio in {inference_time:.0f}ms "
                f"(voice={voice}, lang={language})"
            )

            return audio, metadata

        except Exception as e:
            logger.error(f"[FAIL] TTS synthesis failed: {e}", exc_info=True)
            raise RuntimeError(f"TTS synthesis error: {e}")

    def generate_streaming(
        self,
        text: str,
        voice: str = "F1",
        speed: float = 1.0,
        quality_steps: int = 8,
        language: str = "na",
        chunk_size: int = 4096,
    ):
        """
        Generate speech with streaming output.
        Yields audio chunks as they're generated.
        """
        text_chunks = self.text_processor.chunk_text(text)
        for i, chunk in enumerate(text_chunks):
            audio, _ = self.generate(chunk, voice, speed, quality_steps, language)
            for start in range(0, len(audio), chunk_size):
                yield audio[start:start + chunk_size]

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model and system."""
        info = {
            "model_loaded": self.model_loaded,
            "providers": self.providers,
            "provider_info": self.provider_info,
            "cache_size_mb": round(self.cache.size_mb, 2),
            "cache_count": self.cache.count,
            "load_error": self._load_error,
        }
        return info


# Global TTS engine instance
tts_engine = SupertonicTTS()