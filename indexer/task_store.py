from __future__ import annotations
import copy
import threading
import time
import uuid

import logging

logger = logging.getLogger("repo-wiki-api")


class TaskStore:
    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    _MAX_TASKS = 200
    _TTL_SECONDS = 3600

    def __init__(self):
        self.tasks: dict[str, dict] = {}
        self._lock = threading.Lock()

    def _cleanup(self):
        now = time.time()
        expired = [tid for tid, t in self.tasks.items()
                   if t.get("status") in ("completed", "failed")
                   and now - t.get("_finished_at", now) > self._TTL_SECONDS]
        for tid in expired:
            del self.tasks[tid]
        if len(self.tasks) > self._MAX_TASKS:
            oldest = sorted(
                ((tid, t) for tid, t in self.tasks.items()
                 if t.get("status") not in ("pending", "running")),
                key=lambda x: x[1].get("_created_at", 0),
            )
            for tid, _ in oldest[:len(self.tasks) - self._MAX_TASKS]:
                del self.tasks[tid]

    def create(self, name: str, url: str) -> str:
        with self._lock:
            self._cleanup()
            task_id = uuid.uuid4().hex[:12]
            self.tasks[task_id] = {
                "id": task_id,
                "name": name,
                "url": url,
                "status": "pending",
                "progress": 0,
                "step": "queued",
                "detail": None,
                "result": None,
                "error": None,
                "_created_at": time.time(),
            }
            return task_id

    def get(self, task_id: str) -> dict | None:
        with self._lock:
            task = self.tasks.get(task_id)
            return copy.deepcopy(task) if task else None

    def update(self, task_id: str, **kwargs):
        with self._lock:
            if task_id in self.tasks:
                if kwargs.get("status") in ("completed", "failed"):
                    kwargs["_finished_at"] = time.time()
                self.tasks[task_id].update(kwargs)
