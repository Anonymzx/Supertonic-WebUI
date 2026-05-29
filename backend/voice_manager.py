"""
Supertonic TTS WebUI - Voice Manager
Manages voice selection, previews, and voice metadata.
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from config import AVAILABLE_VOICES, OUTPUTS_DIR
from models import VoiceInfo

logger = logging.getLogger("supertonic-tts.voices")


class VoiceManager:
    """
    Manages voice profiles and metadata for the TTS system.
    Handles voice selection, preview generation, and voice info.
    """

    def __init__(self):
        self.voices: Dict[str, Dict[str, Any]] = AVAILABLE_VOICES
        self.voice_previews_dir = OUTPUTS_DIR / "voice_previews"
        self.voice_previews_dir.mkdir(parents=True, exist_ok=True)

    def get_voices(self) -> List[VoiceInfo]:
        """
        Get list of all available voices with metadata.

        Returns:
            List of VoiceInfo objects
        """
        voices = []
        for voice_id, info in self.voices.items():
            voices.append(VoiceInfo(
                id=voice_id,
                name=info["name"],
                gender=info["gender"],
                description=info.get("description", ""),
            ))
        return voices

    def get_voice(self, voice_id: str) -> Optional[VoiceInfo]:
        """
        Get information for a specific voice.

        Args:
            voice_id: The voice identifier

        Returns:
            VoiceInfo object or None if not found
        """
        if voice_id not in self.voices:
            logger.warning(f"Voice not found: {voice_id}")
            return None

        info = self.voices[voice_id]
        return VoiceInfo(
            id=voice_id,
            name=info["name"],
            gender=info["gender"],
            description=info.get("description", ""),
        )

    def get_preview_path(self, voice_id: str) -> Optional[Path]:
        """
        Get path to voice preview audio file if it exists.

        Args:
            voice_id: The voice identifier

        Returns:
            Path to preview file or None
        """
        preview_path = self.voice_previews_dir / f"{voice_id}_preview.wav"
        if preview_path.exists():
            return preview_path
        return None

    def set_preview(self, voice_id: str, audio_path: Path) -> bool:
        """
        Set or update a voice preview audio file.

        Args:
            voice_id: The voice identifier
            audio_path: Path to the audio file

        Returns:
            True if successful
        """
        if voice_id not in self.voices:
            logger.error(f"Cannot set preview for unknown voice: {voice_id}")
            return False

        if not audio_path.exists():
            logger.error(f"Preview audio not found: {audio_path}")
            return False

        try:
            import shutil
            dest = self.voice_previews_dir / f"{voice_id}_preview.wav"
            shutil.copy2(str(audio_path), str(dest))
            logger.info(f"Voice preview set for {voice_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to set voice preview: {e}")
            return False

    def get_voice_groups(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get voices grouped by gender.

        Returns:
            Dict with 'female' and 'male' voice lists
        """
        groups: Dict[str, List[Dict[str, Any]]] = {
            "female": [],
            "male": [],
        }

        for voice_id, info in self.voices.items():
            gender = info.get("gender", "female")
            groups[gender].append({
                "id": voice_id,
                "name": info["name"],
                "description": info.get("description", ""),
            })

        return groups


# Global voice manager instance
voice_manager = VoiceManager()
</write_to_file>