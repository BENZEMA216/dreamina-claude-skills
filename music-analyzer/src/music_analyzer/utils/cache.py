"""Analysis result caching based on file hash."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from music_analyzer.config import CACHE_DIR


def _file_hash(path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file (first 10MB for large files)."""
    h = hashlib.sha256()
    max_bytes = 10 * 1024 * 1024
    total = 0
    with open(path, "rb") as f:
        while total < max_bytes:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
            total += len(chunk)
    # Include file size to differentiate truncated reads
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16]


def cache_key(audio_path: Path) -> str:
    """Generate a cache key for an audio file."""
    return f"{audio_path.stem}_{_file_hash(audio_path)}"


def get_cached(audio_path: Path, suffix: str = "analysis") -> Optional[dict]:
    """Load cached analysis result if it exists.

    Parameters
    ----------
    audio_path : path to the audio file
    suffix : cache file suffix (e.g. 'analysis', 'dreamina', 'storyboard')
    """
    key = cache_key(audio_path)
    cache_file = CACHE_DIR / f"{key}_{suffix}.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_cache(audio_path: Path, data: dict, suffix: str = "analysis") -> Path:
    """Save analysis result to cache.

    Returns the cache file path.
    """
    key = cache_key(audio_path)
    cache_file = CACHE_DIR / f"{key}_{suffix}.json"
    cache_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return cache_file
