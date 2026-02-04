"""Onset detection for visual sync points."""

from __future__ import annotations

import numpy as np
import librosa

from music_analyzer.models import OnsetInfo


def analyze_onsets(y: np.ndarray, sr: int) -> OnsetInfo:
    """Detect note/event onsets for visual synchronization.

    Parameters
    ----------
    y : audio waveform (mono)
    sr : sample rate
    """
    duration = float(librosa.get_duration(y=y, sr=sr))

    # Onset detection
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_frames = librosa.onset.onset_detect(
        y=y, sr=sr, onset_envelope=onset_env, backtrack=True
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    # Normalize onset strengths
    max_strength = float(np.max(onset_env)) if len(onset_env) > 0 else 1.0
    onset_strengths = []
    for frame in onset_frames:
        if frame < len(onset_env):
            onset_strengths.append(round(float(onset_env[frame] / max(max_strength, 1e-8)), 3))
        else:
            onset_strengths.append(0.0)

    # Onset rate (onsets per second)
    onset_rate = len(onset_times) / max(duration, 0.01)

    return OnsetInfo(
        onset_times=[round(float(t), 3) for t in onset_times],
        onset_strengths=onset_strengths,
        onset_rate=round(onset_rate, 2),
    )
