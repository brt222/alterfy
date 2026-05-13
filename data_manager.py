"""
Alterfy — persistent data layer
Stores: search history, listen history, playlists, play counts
"""
import json
import os
import time
from typing import List, Dict, Optional
from collections import Counter

DATA_DIR  = os.path.join(os.path.expanduser("~"), ".alterfy")
DATA_FILE = os.path.join(DATA_DIR, "userdata.json")

_EMPTY = {
    "search_history": [],       # [{"query": str, "ts": float}]
    "listen_history": [],       # [{"id","title","uploader","thumbnail","url","duration", "ts"}]
    "play_counts":    {},       # {video_id: int}
    "artist_counts":  {},       # {artist_name: int}
    "playlists":      [],       # [{id, name, tracks:[...], created_ts}]
}

MAX_SEARCH_HISTORY = 30
MAX_LISTEN_HISTORY = 200


def _ensure():
    os.makedirs(DATA_DIR, exist_ok=True)


def load() -> dict:
    _ensure()
    if not os.path.exists(DATA_FILE):
        return json.loads(json.dumps(_EMPTY))
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in _EMPTY.items():
            if k not in data:
                data[k] = json.loads(json.dumps(v))
        return data
    except Exception:
        return json.loads(json.dumps(_EMPTY))


def save(data: dict):
    _ensure()
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as ex:
        print(f"[data] save error: {ex}")


class DataManager:
    def __init__(self):
        self._data = load()

    # ── search history ─────────────────────────────────────────

    def add_search(self, query: str):
        query = query.strip()
        if not query:
            return
        hist = self._data["search_history"]
        hist = [h for h in hist if h["query"].lower() != query.lower()]
        hist.insert(0, {"query": query, "ts": time.time()})
        self._data["search_history"] = hist[:MAX_SEARCH_HISTORY]
        self._flush()

    def get_search_history(self) -> List[str]:
        return [h["query"] for h in self._data["search_history"]]

    def clear_search_history(self):
        self._data["search_history"] = []
        self._flush()

    def remove_search(self, query: str):
        self._data["search_history"] = [
            h for h in self._data["search_history"]
            if h["query"].lower() != query.lower()
        ]
        self._flush()

    # ── listen history & counts ────────────────────────────────

    def record_play(self, meta: dict):
        vid_id  = meta.get("id", "")
        artist  = meta.get("uploader", "")
        hist    = self._data["listen_history"]
        entry   = {k: meta.get(k, "") for k in ("id","title","uploader","thumbnail","url","duration")}
        entry["ts"] = time.time()
        hist = [h for h in hist if h.get("id") != vid_id]
        hist.insert(0, entry)
        self._data["listen_history"] = hist[:MAX_LISTEN_HISTORY]
        self._data["play_counts"][vid_id] = self._data["play_counts"].get(vid_id, 0) + 1
        if artist:
            self._data["artist_counts"][artist] = self._data["artist_counts"].get(artist, 0) + 1
        self._flush()

    def get_recent_tracks(self, n: int = 20) -> List[dict]:
        return self._data["listen_history"][:n]

    def get_top_artists(self, n: int = 6) -> List[str]:
        counts = self._data["artist_counts"]
        return [a for a, _ in Counter(counts).most_common(n)]

    def get_top_tracks(self, n: int = 10) -> List[dict]:
        counts = self._data["play_counts"]
        hist_map = {h["id"]: h for h in self._data["listen_history"]}
        sorted_ids = [vid for vid, _ in Counter(counts).most_common(n)]
        return [hist_map[vid] for vid in sorted_ids if vid in hist_map]

    # ── playlists ──────────────────────────────────────────────

    def get_playlists(self) -> List[dict]:
        return self._data["playlists"]

    def get_playlist(self, pl_id: str) -> Optional[dict]:
        for pl in self._data["playlists"]:
            if pl["id"] == pl_id:
                return pl
        return None

    def create_playlist(self, name: str) -> dict:
        import uuid
        pl = {
            "id":         str(uuid.uuid4()),
            "name":       name,
            "tracks":     [],
            "created_ts": time.time(),
        }
        self._data["playlists"].append(pl)
        self._flush()
        return pl

    def rename_playlist(self, pl_id: str, new_name: str):
        pl = self.get_playlist(pl_id)
        if pl:
            pl["name"] = new_name
            self._flush()

    def delete_playlist(self, pl_id: str):
        self._data["playlists"] = [p for p in self._data["playlists"] if p["id"] != pl_id]
        self._flush()

    def add_track_to_playlist(self, pl_id: str, meta: dict) -> bool:
        pl = self.get_playlist(pl_id)
        if not pl:
            return False
        vid_id = meta.get("id", "")
        if any(t.get("id") == vid_id for t in pl["tracks"]):
            return False  # already in playlist
        entry = {k: meta.get(k, "") for k in ("id","title","uploader","thumbnail","url","duration")}
        pl["tracks"].append(entry)
        self._flush()
        return True

    def remove_track_from_playlist(self, pl_id: str, vid_id: str):
        pl = self.get_playlist(pl_id)
        if pl:
            pl["tracks"] = [t for t in pl["tracks"] if t.get("id") != vid_id]
            self._flush()

    def playlist_total_duration(self, pl_id: str) -> int:
        pl = self.get_playlist(pl_id)
        if not pl:
            return 0
        return sum(int(t.get("duration") or 0) for t in pl["tracks"])

    def _flush(self):
        save(self._data)
