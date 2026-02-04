"""Lyrics transcription using faster-whisper (optional dependency)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np

from music_analyzer.config import HAS_FASTER_WHISPER
from music_analyzer.models import LyricSegment, LyricsAnalysis


def analyze_lyrics(
    y: np.ndarray,
    sr: int,
    audio_path: Optional[Path] = None,
    model_size: str = "base",
) -> LyricsAnalysis:
    """Transcribe lyrics from audio.

    Parameters
    ----------
    y : audio waveform (mono)
    sr : sample rate
    audio_path : original file path (faster-whisper can read directly)
    model_size : whisper model size: tiny, base, small, medium, large-v2
    """
    if not HAS_FASTER_WHISPER:
        # Check if vocals are present using energy heuristic
        has_vocals = _detect_vocals_heuristic(y, sr)
        return LyricsAnalysis(
            segments=[],
            full_text="",
            language="unknown",
            has_vocals=has_vocals,
            method="none",
        )

    return _transcribe_whisper(y, sr, audio_path, model_size)


def _detect_vocals_heuristic(y: np.ndarray, sr: int) -> bool:
    """Simple heuristic to detect presence of vocals based on spectral features.

    Vocals tend to have energy in 300-3400 Hz range with specific spectral patterns.
    """
    import librosa

    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)

    # Vocal frequency range (300-3400 Hz)
    vocal_mask = (freqs >= 300) & (freqs <= 3400)
    full_mask = freqs > 0

    vocal_energy = float(np.mean(S[vocal_mask, :] ** 2))
    total_energy = float(np.mean(S[full_mask, :] ** 2))

    vocal_ratio = vocal_energy / max(total_energy, 1e-8)

    # If vocal-range energy is dominant, likely has vocals
    return vocal_ratio > 0.3


def _transcribe_whisper(
    y: np.ndarray,
    sr: int,
    audio_path: Optional[Path],
    model_size: str,
) -> LyricsAnalysis:
    """Transcribe using faster-whisper."""
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(model_size, compute_type="int8")

        # Resample to 16kHz for whisper
        import librosa
        if sr != 16000:
            y_16k = librosa.resample(y, orig_sr=sr, target_sr=16000)
        else:
            y_16k = y

        segments_iter, info = model.transcribe(
            y_16k,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        segments = []
        full_texts = []
        for seg in segments_iter:
            segments.append(LyricSegment(
                start=round(seg.start, 2),
                end=round(seg.end, 2),
                text=seg.text.strip(),
                confidence=round(seg.avg_logprob if hasattr(seg, "avg_logprob") else 0.5, 2),
            ))
            full_texts.append(seg.text.strip())

        return LyricsAnalysis(
            segments=segments,
            full_text=" ".join(full_texts),
            language=info.language if hasattr(info, "language") else "unknown",
            has_vocals=len(segments) > 0,
            method="whisper",
        )

    except Exception as e:
        print(f"Whisper transcription error: {e}", file=sys.stderr)
        return LyricsAnalysis(
            segments=[],
            full_text="",
            language="unknown",
            has_vocals=False,
            method="none",
        )
