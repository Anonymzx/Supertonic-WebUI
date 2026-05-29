"""
Supertonic TTS WebUI - Pydantic Models
API request/response models for the TTS backend.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from config import MAX_TEXT_LENGTH, SUPPORTED_LANGUAGES, AVAILABLE_VOICES


class TTSRequest(BaseModel):
    """Request model for text-to-speech generation."""
    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LENGTH,
                      description="Text to synthesize")
    voice: str = Field(default="F1", description="Voice ID to use")
    speed: float = Field(default=1.0, ge=0.5, le=2.0,
                         description="Speech speed multiplier")
    quality_steps: int = Field(default=32, ge=8, le=64,
                               description="Quality/sampling steps")
    language: str = Field(default="na",
                          description="Language code (na=auto)")
    streaming: bool = Field(default=False,
                            description="Enable streaming response")

    @validator("voice")
    def validate_voice(cls, v: str) -> str:
        """Ensure voice is one of the available voices."""
        if v not in AVAILABLE_VOICES:
            raise ValueError(
                f"Invalid voice '{v}'. Available: {list(AVAILABLE_VOICES.keys())}"
            )
        return v

    @validator("language")
    def validate_language(cls, v: str) -> str:
        """Ensure language is supported."""
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{v}'. Supported: {SUPPORTED_LANGUAGES}"
            )
        return v


class BatchTTSRequest(BaseModel):
    """Request model for batch TTS generation."""
    texts: List[str] = Field(..., min_length=1, max_length=20,
                             description="List of texts to synthesize")
    voice: str = Field(default="F1")
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    quality_steps: int = Field(default=32, ge=8, le=64)
    language: str = Field(default="na")

    @validator("voice")
    def validate_voice(cls, v: str) -> str:
        if v not in AVAILABLE_VOICES:
            raise ValueError(
                f"Invalid voice '{v}'. Available: {list(AVAILABLE_VOICES.keys())}"
            )
        return v

    @validator("language")
    def validate_language(cls, v: str) -> str:
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{v}'. Supported: {SUPPORTED_LANGUAGES}"
            )
        return v

    @validator("texts")
    def validate_texts(cls, v: List[str]) -> List[str]:
        for i, text in enumerate(v):
            if len(text) > MAX_TEXT_LENGTH:
                raise ValueError(
                    f"Text at index {i} exceeds max length of {MAX_TEXT_LENGTH}"
                )
            if len(text.strip()) == 0:
                raise ValueError(f"Text at index {i} is empty")
        return v


class TTSResponse(BaseModel):
    """Response model for TTS generation."""
    id: str = Field(..., description="Unique generation ID")
    text: str = Field(..., description="Original input text")
    voice: str = Field(..., description="Voice used")
    speed: float = Field(..., description="Speed used")
    quality_steps: int = Field(..., description="Quality steps used")
    duration_ms: int = Field(..., description="Generated audio duration in ms")
    inference_ms: int = Field(..., description="Inference time in ms")
    audio_url: str = Field(..., description="URL to generated audio file")
    language: str = Field(..., description="Language code used")
    created_at: str = Field(..., description="ISO timestamp of generation")


class VoiceInfo(BaseModel):
    """Voice information model."""
    id: str = Field(..., description="Voice identifier")
    name: str = Field(..., description="Display name")
    gender: str = Field(..., description="Voice gender")
    description: str = Field(..., description="Voice description")


class HistoryItem(BaseModel):
    """Single history entry model."""
    id: str
    text: str
    voice: str
    speed: float
    quality_steps: int
    duration_ms: int
    inference_ms: int
    audio_url: str
    language: str
    created_at: str


class HistoryResponse(BaseModel):
    """History list response."""
    items: List[HistoryItem]
    total: int


class SystemInfo(BaseModel):
    """System information response."""
    gpu_available: bool
    gpu_name: str = ""
    execution_provider: str = ""
    onnx_version: str = ""
    model_loaded: bool
    audio_cache_size: int
    queue_size: int


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    code: str = "UNKNOWN_ERROR"
</write_to_file>