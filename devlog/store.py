"""Note storage backend using flat JSON files."""

import hashlib
import json
import os
from datetime import datetime, timezone


DEFAULT_DIR = os.path.expanduser("~/.devlog")


class LogStore:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or DEFAULT_DIR
        self.data_file = os.path.join(self.base_dir, "notes.json")
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(self.base_dir, exist_ok=True)

    def _load(self):
        if not os.path.exists(self.data_file):
            return []
        with open(self.data_file) as f:
            return json.load(f)

    def _save(self, notes):
        with open(self.data_file, "w") as f:
            json.dump(notes, f, indent=2)

    def _make_id(self, text, timestamp):
        raw = f"{timestamp}:{text}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def add(self, text, tags=None):
        notes = self._load()
        now = datetime.now(timezone.utc)
        ts = now.isoformat()
        note = {
            "id": self._make_id(text, ts),
            "text": text,
            "date": now.strftime("%Y-%m-%d %H:%M"),
            "timestamp": ts,
            "tags": tags or [],
        }
        notes.insert(0, note)
        self._save(notes)
        return note

    def list_notes(self, count=None, tag=None):
        notes = self._load()
        if tag:
            notes = [n for n in notes if tag in n.get("tags", [])]
        if count:
            notes = notes[:count]
        return notes

    def search(self, query):
        notes = self._load()
        query_lower = query.lower()
        return [
            n for n in notes
            if query_lower in n["text"].lower()
            or any(query_lower in t.lower() for t in n.get("tags", []))
        ]

    def list_tags(self):
        notes = self._load()
        tag_counts = {}
        for note in notes:
            for tag in note.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts

    def get_by_prefix(self, prefix):
        notes = self._load()
        for note in notes:
            if note["id"].startswith(prefix):
                return note
        return None

    def update(self, note_id, new_text):
        notes = self._load()
        for note in notes:
            if note["id"] == note_id:
                note["text"] = new_text
                note["modified"] = datetime.now(timezone.utc).isoformat()
                break
        self._save(notes)

    def delete(self, note_id):
        notes = self._load()
        notes = [n for n in notes if n["id"] != note_id]
        self._save(notes)

    def export_json(self):
        notes = self._load()
        return json.dumps(notes, indent=2)
