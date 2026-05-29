"""
Supertonic TTS WebUI - TTS Engine Module
Core text-to-speech generation using Supertonic 3 via ONNX Runtime.
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
    SUPERTONIC_MODEL_PATH, SUPERTONIC_MODEL_NAME,
    EXPRESSION_TAGS, CHUNK_SIZE, MAX_TEXT_LENGTH,
    AVAILABLE_VOICES, CACHE_DIR, CACHE_MAX_AGE_HOURS,
    ORT_OPTIONS, CACHE_MAX_SIZE_MB
)
from execution_providers import (
    detect_execution_providers,
    create_session_options,
    get_provider_info,
)

logger = logging.getLogger("supertonic-tts.engine")


class TextPreprocessor:
    """Handles text preprocessing for TTS."""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text for TTS processing."""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove expression tags (handle them as SSML-like markers)
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
        # Indonesian-specific characters/patterns
        id_patterns = [
            r'\byang\b', r'\bdengan\b', r'\bdan\b', r'\bdi\b',
            r'\btidak\b', r'\bini\b', r'\bitu\b', r'\bada\b',
            r'\bakan\b', r'\bdapat\b', r'\bdari\b', r'\bdia\b',
            r'\bke\b', r'\boleh\b', r'\bpada\b', r'\buntuk\b',
            r'\bsaya\b', r'\bkamu\b', r'\bkami\b', r'\bmereka\b',
            r'\bmeng\w+', r'\bber\w+', r'\bter\w+', r'\bpe\w+',
            r'\bse\w+', r'\bmem\w+', r'\bben\w+', r'\bmemper\w+',
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
        """Generate a unique cache key from generation parameters."""
        content = f"{text}:{voice}:{speed}:{quality_steps}:{language}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, text: str, voice: str, speed: float,
            quality_steps: int, language: str) -> Optional[Path]:
        """Get cached audio file if it exists and is valid."""
        cache_key = self._get_cache_key(text, voice, speed, quality_steps, language)
        cache_file = self.cache_dir / f"{cache_key}{AUDIO_EXTENSION}"

        if cache_file.exists():
            # Check age
            age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
            if age_hours <= CACHE_MAX_AGE_HOURS:
                logger.info(f"Cache hit: {cache_key}")
                return cache_file
            else:
                # Expired, remove it
                cache_file.unlink(missing_ok=True)

        return None

    def set(self, text: str, voice: str, speed: float,
            quality_steps: int, language: str, audio_data: np.ndarray,
            sample_rate: int = SAMPLE_RATE) -> Path:
        """Cache generated audio data."""
        cache_key = self._get_cache_key(text, voice, speed, quality_steps, language)
        cache_file = self.cache_dir / f"{cache_key}{AUDIO_EXTENSION}"

        # Save audio file
        sf.write(str(cache_file), audio_data, sample_rate)
        logger.info(f"Cached: {cache_key}")

        return cache_file

    def clear_expired(self) -> int:
        """Clear expired cache entries. Returns count of removed files."""
        removed = 0
        for cache_file in self.cache_dir.glob(f"*{AUDIO_EXTENSION}"):
            age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
            if age_hours > CACHE_MAX_AGE_HOURS:
                cache_file.unlink()
                removed += 1

        if removed > 0:
            logger.info(f"Cleared {removed} expired cache entries")

        return removed

    @property
    def size_mb(self) -> float:
        """Get total cache size in MB."""
        total_bytes = sum(
            f.stat().st_size for f in self.cache_dir.glob(f"*{AUDIO_EXTENSION}")
        )
        return total_bytes / (1024 * 1024)

    @property
    def count(self) -> int:
        """Get number of cached files."""
        return len(list(self.cache_dir.glob(f"*{AUDIO_EXTENSION}")))


class SupertonicTTS:
    """
    Core TTS engine using Supertonic 3 model via ONNX Runtime.
    Handles model loading, inference, and audio generation.
    """

    def __init__(self):
        self.session = None
        self.providers = ["CPUExecutionProvider"]
        self.provider_info = {}
        self.model_loaded = False
        self.cache = AudioCache()
        self.text_processor = TextPreprocessor()

        # Detect execution providers on init
        self._setup_providers()

    def _setup_providers(self) -> None:
        """Detect and configure execution providers."""
        try:
            logger.info("Detecting available execution providers...")
            self.providers = detect_execution_providers()
            self.provider_info = get_provider_info()

            logger.info(
                f"Providers detected: {self.providers} "
                f"(GPU: {self.provider_info.get('gpu_available', False)})"
            )
        except Exception as e:
            logger.warning(f"Provider detection failed, using CPU: {e}")
            self.providers = ["CPUExecutionProvider"]

    def load_model(self) -> bool:
        """
        Load the Supertonic 3 ONNX model.

        Returns:
            True if model loaded successfully
        """
        try:
            # Check if model file exists
            model_path = self._find_model_file()
            if not model_path:
                logger.error("Model file not found. Please download first.")
                return False

            logger.info(f"Loading model from: {model_path}")

            # Try using supertonic SDK first
            try:
                from supertonic import SupertonicModel
                self.session = SupertonicModel(
                    model_path=str(model_path),
                    providers=self.providers,
                    session_options=create_session_options(),
                )
                logger.info("Model loaded via Supertonic SDK")
                self.model_loaded = True
                return True
            except ImportError:
                logger.info("Supertonic SDK not found, using direct ONNX Runtime")

            # Fallback: direct ONNX Runtime
            import onnxruntime as ort
            opts = create_session_options()
            self.session = ort.InferenceSession(
                str(model_path),
                sess_options=opts,
                providers=self.providers,
            )
            logger.info("Model loaded via ONNX Runtime directly")
            self.model_loaded = True
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model_loaded = False
            return False

    def _find_model_file(self) -> Optional[Path]:
        """Find the model file in the models directory."""
        model_dir = SUPERTONIC_MODEL_PATH

        # Check common model file patterns
        patterns = [
            model_dir / "model.onnx",
            model_dir / "supertonic-3.onnx",
            model_dir / "supertonic_model.onnx",
            model_dir / "Supertonic-3.onnx",
        ]

        for pattern in patterns:
            if pattern.exists():
                return pattern

        # Also check for any .onnx file in the directory
        onnx_files = list(SUPERTONIC_MODEL_PATH.parent.glob("*.onnx"))
        if onnx_files:
            return onnx_files[0]

        # Check if the model path itself is an ONNX file
        if model_path := Path(SUPERTONIC_MODEL_PATH).with_suffix(".onnx"):
            if model_path.exists():
                return model_path

        return None

    def generate(
        self,
        text: str,
        voice: str = "F1",
        speed: float = 1.0,
        quality_steps: int = 32,
        language: str = "na",
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate speech audio from text.

        Args:
            text: Input text to synthesize
            voice: Voice ID to use
            speed: Speech speed multiplier (0.5-2.0)
            quality_steps: Number of quality/sampling steps
            language: Language code (na=auto)

        Returns:
            Tuple of (audio_array, metadata_dict)
        """
        start_time = time.time()

        # Clean and prepare text
        text = self.text_processor.clean_text(text)

        if not text:
            raise ValueError("Empty text after preprocessing")

        # Auto-detect language if set to auto
        if language == "na":
            language = self.text_processor.detect_language(text)

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
            return audio, metadata

        # Generate audio using the model
        audio = self._run_inference(text, voice, speed, quality_steps, language)
        inference_time = (time.time() - start_time) * 1000

        # Calculate duration
        duration_ms = int(len(audio) / SAMPLE_RATE * 1000)

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

    def _run_inference(
        self,
        text: str,
        voice: str,
        speed: float,
        quality_steps: int,
        language: str,
    ) -> np.ndarray:
        """
        Run model inference to generate audio.

        Args:
            text: Processed text
            voice: Voice ID
            speed: Speed multiplier
            quality_steps: Quality steps
            language: Detected/specified language

        Returns:
            Audio array as numpy array
        """
        if not self.session or not self.model_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            # Try Supertonic SDK inference
            if hasattr(self.session, 'synthesize'):
                audio = self.session.synthesize(
                    text=text,
                    voice=voice,
                    speed=speed,
                    steps=quality_steps,
                    language=language,
                )
                return np.array(audio, dtype=np.float32)

            # Direct ONNX Runtime inference
            # Prepare input tensors
            input_names = [inp.name for inp in self.session.get_inputs()]
            output_names = [out.name for out in self.session.get_outputs()]

            # Build input dict based on model requirements
            inputs = {}
            for name in input_names:
                if "text" in name.lower() or "input" in name.lower():
                    inputs[name] = np.array([text], dtype=np.str_)
                elif "voice" in name.lower():
                    # Map voice to index
                    voice_idx = list(AVAILABLE_VOICES.keys()).index(voice)
                    inputs[name] = np.array([voice_idx], dtype=np.int64)
                elif "speed" in name.lower():
                    inputs[name] = np.array([speed], dtype=np.float32)
                elif "steps" in name.lower() or "quality" in name.lower():
                    inputs[name] = np.array([quality_steps], dtype=np.int64)
                elif "language" in name.lower() or "lang" in name.lower():
                    inputs[name] = np.array([language], dtype=np.str_)
                else:
                    # Use default empty tensor
                    inputs[name] = np.array([0], dtype=np.int64)

            # Run inference
            outputs = self.session.run(output_names, inputs)

            # Get audio output (first output typically)
            audio = outputs[0]
            if isinstance(audio, list):
                audio = audio[0]

            return np.array(audio, dtype=np.float32).flatten()

        except Exception as e:
            logger.error(f"Inference failed: {e}")
            raise RuntimeError(f"TTS inference error: {e}")

    def generate_streaming(
        self,
        text: str,
        voice: str = "F1",
        speed: float = 1.0,
        quality_steps: int = 32,
        language: str = "na",
        chunk_size: int = 4096,
    ):
        """
        Generate speech with streaming output.
        Yields audio chunks as they're generated.

        Args:
            text: Input text
            voice: Voice ID
            speed: Speed multiplier
            quality_steps: Quality steps
            language: Language code
            chunk_size: Size of audio chunks to yield

        Yields:
            Audio data chunks
        """
        # For long text, chunk and process each part
        text_chunks = self.text_processor.chunk_text(text)

        for i, chunk in enumerate(text_chunks):
            audio, _ = self.generate(chunk, voice, speed, quality_steps, language)

            # Yield in small chunks for streaming
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
        }

        if self.model_loaded and hasattr(self.session, 'get_model_info'):
            try:
                info["model_info"] = self.session.get_model_info()
            except Exception:
                pass

        return info


# Global TTS engine instance
tts_engine = SupertonicTTS()
</write_to_file>