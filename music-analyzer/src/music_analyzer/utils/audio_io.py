"""Audio file loading and format detection utilities."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from music_analyzer.config import DEFAULT_SR, SUPPORTED_FORMATS


def validate_audio_path(path: str) -> Path:
    """Validate that path points to a supported audio file.

    Returns resolved Path on success, raises SystemExit on failure.
    """
    p = Path(path).expanduser().resolve()
    if not p.exists():
        print(f"Error: file not found: {p}", file=sys.stderr)
        raise SystemExit(1)
    if p.suffix.lower() not in SUPPORTED_FORMATS:
        print(
            f"Error: unsupported format '{p.suffix}'. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return p


def load_audio(
    path: str | Path,
    sr: Optional[int] = None,
    mono: bool = True,
    duration: Optional[float] = None,
) -> Tuple[np.ndarray, int]:
    """Load audio file and return (waveform, sample_rate).

    Parameters
    ----------
    path : path to audio file
    sr : target sample rate (None = native rate, default = DEFAULT_SR)
    mono : convert to mono
    duration : only load first N seconds
    """
    import librosa

    target_sr = sr if sr is not None else DEFAULT_SR
    y, sr_out = librosa.load(str(path), sr=target_sr, mono=mono, duration=duration)
    return y, sr_out


def get_audio_info(path: str | Path) -> dict:
    """Get basic audio file metadata without loading full waveform."""
    import soundfile as sf

    p = Path(path)
    info = sf.info(str(p))
    return {
        "file_path": str(p.resolve()),
        "file_name": p.name,
        "format": info.format,
        "subtype": info.subtype,
        "sample_rate": info.samplerate,
        "channels": info.channels,
        "frames": info.frames,
        "duration": info.duration,
    }
