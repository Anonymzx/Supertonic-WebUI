"""
Supertonic TTS WebUI - History Manager
Manages generation history with JSON persistence.
"""
import json
import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from config import HISTORY_FILE, HISTORY_MAX_ITEMS
from models import HistoryItem, HistoryResponse

logger = logging.getLogger("supertonic-tts.history")


class HistoryManager:
    """
    Manages the history of TTS generations.
    Stores metadata in a JSON file with configurable max items.
    """

    def __init__(self):
        self.history_file: Path = HISTORY_FILE
        self.max_items: int = HISTORY_MAX_ITEMS
        self._items: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load history from JSON file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self._items = json.load(f)
                logger.info(f"Loaded {len(self._items)} history items")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load history: {e}")
                self._items = []
        else:
            self._items = []
            self._save()

    def _save(self) -> None:
        """Save history to JSON file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self._items, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save history: {e}")

    def add_item(
        self,
        text: str,
        voice: str,
        speed: float,
        quality_steps: int,
        duration_ms: int,
        inference_ms: int,
        audio_url: str,
        language: str,
    ) -> str:
        """
        Add a new generation to history.

        Returns:
            The unique ID of the new history item
        """
        item_id = uuid.uuid4().hex[:12]
        created_at = datetime.utcnow().isoformat() + "Z"

        item = {
            "id": item_id,
            "text": text,
            "voice": voice,
            "speed": speed,
            "quality_steps": quality_steps,
            "duration_ms": duration_ms,
            "inference_ms": inference_ms,
            "audio_url": audio_url,
            "language": language,
            "created_at": created_at,
        }

        self._items.insert(0, item)

        # Trim to max items
        if len(self._items) > self.max_items:
            self._items = self._items[:self.max_items]

        self._save()
        logger.info(f"Added history item: {item_id}")
        return item_id

    def get_items(self, page: int = 1, per_page: int = 20) -> HistoryResponse:
        """
        Get paginated history items.

        Args:
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            HistoryResponse with paginated items
        """
        start = (page - 1) * per_page
        end = start + per_page
        page_items = self._items[start:end]

        items = [
            HistoryItem(**item) for item in page_items
        ]

        return HistoryResponse(
            items=items,
            total=len(self._items),
        )

    def get_item(self, item_id: str) -> Optional[HistoryItem]:
        """
        Get a specific history item by ID.

        Args:
            item_id: The item's unique ID

        Returns:
            HistoryItem or None if not found
        """
        for item in self._items:
            if item["id"] == item_id:
                return HistoryItem(**item)
        return None

    def delete_item(self, item_id: str) -> bool:
        """
        Delete a history item by ID.

        Args:
            item_id: The item's unique ID

        Returns:
            True if item was deleted, False if not found
        """
        initial_len = len(self._items)
        self._items = [item for item in self._items if item["id"] != item_id]

        if len(self._items) < initial_len:
            self._save()
            logger.info(f"Deleted history item: {item_id}")
            return True

        logger.warning(f"History item not found: {item_id}")
        return False

    def clear_all(self) -> int:
        """
        Clear all history items.

        Returns:
            Number of items cleared
        """
        count = len(self._items)
        self._items = []
        self._save()
        logger.info(f"Cleared {count} history items")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the generation history.

        Returns:
            Dict with stats like total items, total duration, etc.
        """
        if not self._items:
            return {
                "total_items": 0,
                "total_duration_ms": 0,
                "voices_used": {},
                "languages_used": {},
            }

        voices: Dict[str, int] = {}
        languages: Dict[str, int] = {}
        total_duration = 0

        for item in self._items:
            voice = item.get("voice", "unknown")
            voices[voice] = voices.get(voice, 0) + 1

            lang = item.get("language", "unknown")
            languages[lang] = languages.get(lang, 0) + 1

            total_duration += item.get("duration_ms", 0)

        return {
            "total_items": len(self._items),
            "total_duration_ms": total_duration,
            "voices_used": voices,
            "languages_used": languages,
        }


# Global history manager instance
history_manager = HistoryManager()
