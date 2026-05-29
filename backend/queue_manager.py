"""
Supertonic TTS WebUI - Queue Manager
Async generation queue for managing TTS requests.
"""
import asyncio
import uuid
import time
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from enum import Enum
from datetime import datetime

logger = logging.getLogger("supertonic-tts.queue")


class QueueStatus(str, Enum):
    """Status of a queue item."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueueItem:
    """Represents a single item in the generation queue."""

    def __init__(
        self,
        request_data: Dict[str, Any],
        callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    ):
        self.id: str = uuid.uuid4().hex[:12]
        self.request_data: Dict[str, Any] = request_data
        self.status: QueueStatus = QueueStatus.PENDING
        self.callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = callback
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.created_at: float = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None

    @property
    def wait_time_ms(self) -> float:
        """Time spent waiting in queue."""
        if self.started_at:
            return (self.started_at - self.created_at) * 1000
        return (time.time() - self.created_at) * 1000

    @property
    def process_time_ms(self) -> Optional[float]:
        """Time spent processing."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at) * 1000
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "status": self.status.value,
            "request": self.request_data,
            "created_at": datetime.utcfromtimestamp(self.created_at).isoformat() + "Z",
            "wait_time_ms": round(self.wait_time_ms, 2),
            "process_time_ms": round(self.process_time_ms, 2) if self.process_time_ms else None,
            "error": self.error,
        }


class GenerationQueue:
    """
    Async queue for managing TTS generation requests.
    Processes items sequentially to avoid GPU memory issues.
    """

    def __init__(self, max_concurrent: int = 1):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.items: Dict[str, QueueItem] = {}
        self.max_concurrent: int = max_concurrent
        self._processing: bool = False
        self._workers: list = []
        self._current_count: int = 0

    async def enqueue(
        self,
        request_data: Dict[str, Any],
        callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    ) -> QueueItem:
        """
        Add a new generation request to the queue.

        Args:
            request_data: The TTS generation parameters
            callback: Optional async callback to call when complete

        Returns:
            QueueItem with status tracking
        """
        item = QueueItem(request_data, callback)
        self.items[item.id] = item

        await self.queue.put(item)
        logger.info(f"Enqueued request {item.id}: {item.request_data.get('text', '')[:50]}...")

        # Start workers if not running
        if not self._processing:
            self._start_workers()

        return item

    def _start_workers(self) -> None:
        """Start background worker tasks."""
        self._processing = True
        for _ in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker_loop())
            self._workers.append(worker)

    async def _worker_loop(self) -> None:
        """Main worker loop that processes queue items."""
        while True:
            try:
                item: QueueItem = await self.queue.get()

                # Update status
                item.status = QueueStatus.PROCESSING
                item.started_at = time.time()
                self._current_count += 1

                try:
                    # Process the item (actual processing is handled externally)
                    logger.info(f"Processing queue item {item.id}")
                    # Worker will wait for external processing to complete

                except Exception as e:
                    item.status = QueueStatus.FAILED
                    item.error = str(e)
                    logger.error(f"Queue item {item.id} failed: {e}")

                finally:
                    self.queue.task_done()
                    self._current_count -= 1

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)

    async def complete_item(
        self,
        item_id: str,
        result: Dict[str, Any],
    ) -> None:
        """
        Mark a queue item as completed with its result.

        Args:
            item_id: The item's unique ID
            result: The generation result data
        """
        item = self.items.get(item_id)
        if not item:
            logger.warning(f"Cannot complete unknown item: {item_id}")
            return

        item.status = QueueStatus.COMPLETED
        item.result = result
        item.completed_at = time.time()

        logger.info(
            f"Completed queue item {item_id} "
            f"(wait: {item.wait_time_ms:.0f}ms, "
            f"process: {item.process_time_ms:.0f}ms)"
        )

        # Call callback if provided
        if item.callback:
            try:
                await item.callback(result)
            except Exception as e:
                logger.error(f"Callback failed for {item_id}: {e}")

    async def fail_item(self, item_id: str, error: str) -> None:
        """
        Mark a queue item as failed.

        Args:
            item_id: The item's unique ID
            error: Error description
        """
        item = self.items.get(item_id)
        if not item:
            return

        item.status = QueueStatus.FAILED
        item.error = error
        item.completed_at = time.time()
        logger.error(f"Failed queue item {item_id}: {error}")

    def get_item(self, item_id: str) -> Optional[QueueItem]:
        """Get a queue item by ID."""
        return self.items.get(item_id)

    def get_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            "queue_size": self.queue.qsize(),
            "processing": self._current_count,
            "total_enqueued": len(self.items),
            "items": {
                status.value: sum(
                    1 for i in self.items.values()
                    if i.status.value == status.value
                )
                for status in QueueStatus
            },
        }

    def cancel_item(self, item_id: str) -> bool:
        """
        Cancel a pending queue item.

        Args:
            item_id: The item's unique ID

        Returns:
            True if item was cancelled
        """
        item = self.items.get(item_id)
        if not item or item.status != QueueStatus.PENDING:
            return False

        item.status = QueueStatus.CANCELLED
        logger.info(f"Cancelled queue item {item_id}")
        return True

    @property
    def pending_count(self) -> int:
        """Number of pending items in queue."""
        return self.queue.qsize()

    @property
    def total_count(self) -> int:
        """Total number of items ever enqueued."""
        return len(self.items)


# Global queue instance
generation_queue = GenerationQueue()
