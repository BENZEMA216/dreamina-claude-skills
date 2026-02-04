"""Configuration and dependency detection for music_analyzer."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Literal

# Cache directory for analysis results and separated stems
CACHE_DIR = Path.home() / ".cache" / "music-analyzer"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Default audio sample rate for analysis
DEFAULT_SR = 22050

# Supported audio formats
SUPPORTED_FORMATS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"}


def _has(module: str) -> bool:
    """Check whether an optional dependency is importable."""
    try:
        importlib.import_module(module)
        return True
    except ImportError:
        return False


HAS_ESSENTIA = _has("essentia")
HAS_PYLOUDNORM = _has("pyloudnorm")
HAS_DEMUCS = _has("demucs")
HAS_FASTER_WHISPER = _has("faster_whisper")
HAS_CLAP = _has("laion_clap")
HAS_TORCH = _has("torch")


def dependency_tier() -> Literal["lite", "standard", "full"]:
    """Return the current dependency tier based on what is installed."""
    if HAS_DEMUCS or HAS_FASTER_WHISPER or HAS_CLAP:
        return "full"
    if HAS_ESSENTIA or HAS_PYLOUDNORM:
        return "standard"
    return "lite"
