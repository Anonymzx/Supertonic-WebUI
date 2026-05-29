"""
Supertonic TTS WebUI - Main FastAPI Application
REST API for text-to-speech generation using official Supertonic 3 SDK.
"""
import io
import json
import time
import logging
from typing import Optional
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles

from config import (
    HOST, PORT, BACKEND_URL, FRONTEND_URL,
    SAMPLE_RATE, AUDIO_EXTENSION, OUTPUTS_DIR,
    AVAILABLE_VOICES, logger,
)
from models import (
    TTSRequest, BatchTTSRequest, TTSResponse,
    VoiceInfo, HistoryResponse, HistoryItem,
    SystemInfo, ErrorResponse,
)
from tts_engine import tts_engine, SupertonicTTS
from voice_manager import voice_manager
from history_manager import history_manager
from queue_manager import generation_queue

logger = logging.getLogger("supertonic-tts.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    logger.info("=" * 50)
    logger.info("Supertonic TTS WebUI Starting...")
    logger.info("=" * 50)

    # Log system info
    providers = tts_engine.providers
    logger.info(f"Execution providers: {providers}")
    logger.info(f"GPU available: {tts_engine.provider_info.get('gpu_available', False)}")
    logger.info(f"GPU name: {tts_engine.provider_info.get('gpu_name', 'N/A')}")

    # Try to load model automatically using official SDK (auto_download=True)
    logger.info("Attempting to load Supertonic 3 model (official SDK with auto-download)...")
    try:
        model_loaded = tts_engine.load_model()
        if model_loaded:
            logger.info("✓ Model loaded successfully via official SDK")
        else:
            err = tts_engine._load_error or "Unknown error"
            logger.warning(f"⚠ Model could not be loaded: {err}")
            logger.warning("  The SDK will auto-download on first successful load.")
    except Exception as e:
        logger.error(f"⚠ Unexpected error during model loading: {e}")

    # Show available endpoints
    logger.info(f"API: http://{HOST}:{PORT}/api")
    logger.info(f"Docs: http://{HOST}:{PORT}/docs")
    logger.info(f"Frontend: {FRONTEND_URL}")

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Supertonic TTS WebUI",
    description="Local AI Text-to-Speech powered by Supertonic 3 (official SDK)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── TTS Endpoints ───────────────────────────────────────────────────────


@app.post("/api/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Generate speech from text using the official Supertonic 3 SDK.
    Auto-downloads model via HuggingFace cache if not present.
    """
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        # Try to load model if not loaded (auto-download)
        if not tts_engine.model_loaded:
            logger.info("Model not loaded. Attempting SDK load with auto_download...")
            success = tts_engine.load_model()
            if not success:
                err = tts_engine._load_error or "Unknown error"
                raise HTTPException(
                    status_code=503,
                    detail=f"Model could not be loaded: {err}. "
                           f"Ensure supertonic SDK is installed: pip install supertonic",
                )

        # Generate audio
        audio, metadata = tts_engine.generate(
            text=text,
            voice=request.voice,
            speed=request.speed,
            quality_steps=request.quality_steps,
            language=request.language,
        )

        # Save output file
        output_id = f"{int(time.time())}_{abs(hash(text)) % 10000:04d}"
        output_filename = f"{output_id}{AUDIO_EXTENSION}"
        output_path = OUTPUTS_DIR / output_filename

        sf.write(str(output_path), audio, SAMPLE_RATE)

        # Build audio URL
        audio_url = f"/audio/{output_filename}"

        # Add to history
        history_id = history_manager.add_item(
            text=text,
            voice=request.voice,
            speed=request.speed,
            quality_steps=request.quality_steps,
            duration_ms=metadata["duration_ms"],
            inference_ms=metadata["inference_ms"],
            audio_url=audio_url,
            language=request.language,
        )

        # Return response
        return TTSResponse(
            id=history_id,
            text=text,
            voice=request.voice,
            speed=request.speed,
            quality_steps=request.quality_steps,
            duration_ms=metadata["duration_ms"],
            inference_ms=metadata["inference_ms"],
            audio_url=audio_url,
            language=request.language,
            created_at=__import__("datetime").datetime.utcnow().isoformat() + "Z",
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"TTS generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/api/tts/stream")
async def text_to_speech_stream(request: TTSRequest):
    """Generate speech with streaming audio response."""
    try:
        if not tts_engine.model_loaded:
            success = tts_engine.load_model()
            if not success:
                raise HTTPException(
                    status_code=503,
                    detail=f"Model not loaded: {tts_engine._load_error}",
                )

        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        audio, metadata = tts_engine.generate(
            text=text,
            voice=request.voice,
            speed=request.speed,
            quality_steps=request.quality_steps,
            language=request.language,
        )

        async def generate_stream():
            buffer = io.BytesIO()
            sf.write(buffer, audio, SAMPLE_RATE, format="WAV")
            buffer.seek(0)
            chunk_size = 4096
            while True:
                chunk = buffer.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        return StreamingResponse(
            generate_stream(),
            media_type="audio/wav",
            headers={
                "X-Audio-Duration-Ms": str(metadata.get("duration_ms", 0)),
                "X-Inference-Ms": str(metadata.get("inference_ms", 0)),
                "Content-Disposition": f'attachment; filename="stream{AUDIO_EXTENSION}"',
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Streaming TTS failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts/batch")
async def batch_text_to_speech(request: BatchTTSRequest):
    """Generate speech for multiple texts in batch."""
    try:
        if not tts_engine.model_loaded:
            success = tts_engine.load_model()
            if not success:
                raise HTTPException(
                    status_code=503,
                    detail=f"Model not loaded: {tts_engine._load_error}",
                )

        results = []
        for i, text in enumerate(request.texts):
            text = text.strip()
            if not text:
                continue
            audio, metadata = tts_engine.generate(
                text=text,
                voice=request.voice,
                speed=request.speed,
                quality_steps=request.quality_steps,
                language=request.language,
            )
            output_id = f"batch_{i}_{int(time.time())}"
            output_filename = f"{output_id}{AUDIO_EXTENSION}"
            output_path = OUTPUTS_DIR / output_filename
            sf.write(str(output_path), audio, SAMPLE_RATE)

            audio_url = f"/audio/{output_filename}"

            history_id = history_manager.add_item(
                text=text,
                voice=request.voice,
                speed=request.speed,
                quality_steps=request.quality_steps,
                duration_ms=metadata["duration_ms"],
                inference_ms=metadata["inference_ms"],
                audio_url=audio_url,
                language=request.language,
            )

            results.append(TTSResponse(
                id=history_id,
                text=text,
                voice=request.voice,
                speed=request.speed,
                quality_steps=request.quality_steps,
                duration_ms=metadata["duration_ms"],
                inference_ms=metadata["inference_ms"],
                audio_url=audio_url,
                language=request.language,
                created_at=__import__("datetime").datetime.utcnow().isoformat() + "Z",
            ))

        return {"items": results, "total": len(results)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch TTS failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ─── Voice Endpoints ────────────────────────────────────────────────────


@app.get("/api/voices", response_model=list)
async def get_voices():
    """Get list of all available voices with metadata."""
    voices = voice_manager.get_voices()
    return [
        {
            "id": v.id,
            "name": v.name,
            "gender": v.gender,
            "description": v.description,
        }
        for v in voices
    ]


@app.get("/api/voices/{voice_id}", response_model=VoiceInfo)
async def get_voice(voice_id: str):
    voice = voice_manager.get_voice(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")
    return voice


@app.get("/api/voices/groups/grouped")
async def get_voice_groups():
    return voice_manager.get_voice_groups()


# ─── History Endpoints ──────────────────────────────────────────────────


@app.get("/api/history", response_model=HistoryResponse)
async def get_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    return history_manager.get_items(page=page, per_page=per_page)


@app.delete("/api/history/{item_id}")
async def delete_history_item(item_id: str):
    deleted = history_manager.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History item not found")
    return {"message": "Deleted", "id": item_id}


@app.delete("/api/history")
async def clear_history():
    count = history_manager.clear_all()
    return {"message": f"Cleared {count} items"}


@app.get("/api/history/stats")
async def get_history_stats():
    return history_manager.get_stats()


# ─── System Endpoints ───────────────────────────────────────────────────


@app.get("/api/system-info")
@app.get("/api/system/info")
async def get_system_info():
    """
    Get system information including GPU status, execution provider,
    ONNX Runtime version, and model status.
    """
    try:
        import onnxruntime as ort
        onnx_ver = ort.__version__
    except Exception:
        onnx_ver = ""

    return {
        "execution_provider": tts_engine.providers[0] if tts_engine.providers else "CPU",
        "providers": tts_engine.providers,
        "gpu_available": tts_engine.provider_info.get("gpu_available", False),
        "gpu_name": tts_engine.provider_info.get("gpu_name", ""),
        "onnx_version": onnx_ver,
        "model_loaded": tts_engine.model_loaded,
        "audio_cache_size": tts_engine.cache.count,
        "queue_size": generation_queue.pending_count,
    }


@app.get("/api/system/providers")
async def get_providers():
    return {
        "providers": tts_engine.providers,
        "provider_info": tts_engine.provider_info,
    }


@app.get("/api/system/queue")
async def get_queue_status():
    return generation_queue.get_status()


# ─── Model Management Endpoints ─────────────────────────────────────────


@app.post("/api/model/load")
async def load_model():
    """Load the Supertonic 3 model using official SDK (auto-download)."""
    if tts_engine.model_loaded:
        return {"message": "Model already loaded", "status": "ok"}

    success = tts_engine.load_model()
    if not success:
        err = tts_engine._load_error or "Unknown error"
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {err}",
        )

    return {"message": "Model loaded successfully via SDK", "status": "ok"}


@app.post("/api/model/download")
async def download_model():
    """
    Download/load the Supertonic 3 model using official SDK.
    The SDK handles auto-download and HuggingFace caching automatically.
    """
    if tts_engine.model_loaded:
        return {"message": "Model already loaded", "status": "ok"}

    success = tts_engine.load_model()
    if success:
        return {"message": "Model downloaded and loaded via SDK", "status": "ok"}
    else:
        err = tts_engine._load_error or "Unknown error"
        return {
            "message": f"Model download initiated. Status: {err}",
            "status": "downloading",
        }


@app.get("/api/model/status")
async def get_model_status():
    return {
        "loaded": tts_engine.model_loaded,
        "model_info": tts_engine.get_model_info(),
    }


# ─── Audio Serving ──────────────────────────────────────────────────────


@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve generated audio files."""
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    file_path = OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        str(file_path),
        media_type="audio/wav",
        filename=filename,
    )


# ─── Health Check ───────────────────────────────────────────────────────


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "model_loaded": tts_engine.model_loaded,
        "gpu_available": tts_engine.provider_info.get("gpu_available", False),
        "execution_provider": tts_engine.providers[0] if tts_engine.providers else "CPU",
        "uptime": time.time() - app.state.__dict__.get("start_time", time.time()),
    }


@app.on_event("startup")
async def save_start_time():
    """Save application start time."""
    app.state.start_time = time.time()


# ─── Error Handlers ─────────────────────────────────────────────────────


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format - returns JSON the frontend can display."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return Response(
        content=json.dumps({
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}",
        }),
        status_code=exc.status_code,
        media_type="application/json",
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return Response(
        content=json.dumps({
            "error": "Internal server error",
            "detail": str(exc),
            "code": "INTERNAL_ERROR",
        }),
        status_code=500,
        media_type="application/json",
    )


# ─── Main Entry Point ───────────────────────────────────────────────────


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info",
    )
</write_to_file>