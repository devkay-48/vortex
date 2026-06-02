"""
Persistent download history stored at ~/.local/share/vortex/queue.json
Each entry: { title, url, success, timestamp }
"""

import json
import os
from datetime import datetime


QUEUE_DIR  = os.path.join(os.path.expanduser("~"), ".local", "share", "vortex")
QUEUE_FILE = os.path.join(QUEUE_DIR, "queue.json")


class DownloadQueue:

    def __init__(self):
        os.makedirs(QUEUE_DIR, exist_ok=True)
        self._entries = self._load()

    def _load(self) -> list:
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self):
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._entries, f, indent=2, ensure_ascii=False)

    def add(self, title: str, url: str, success: bool):
        entry = {
            "title":     title or url,
            "url":       url,
            "success":   success,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        self._entries.insert(0, entry)   # newest first
        # keep last 200 entries
        self._entries = self._entries[:200]
        self._save()

    def all(self) -> list:
        return list(self._entries)

    def clear(self):
        self._entries = []
        self._save()
