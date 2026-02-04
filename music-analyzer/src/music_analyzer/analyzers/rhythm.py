"""Rhythm analysis: BPM, beats, time signature, song structure segmentation."""

from __future__ import annotations

import numpy as np
import librosa

from music_analyzer.models import BeatInfo, RhythmAnalysis, SongSection


def analyze_rhythm(y: np.ndarray, sr: int) -> RhythmAnalysis:
    """Run full rhythm analysis on audio waveform.

    Parameters
    ----------
    y : audio waveform (mono)
    sr : sample rate
    """
    duration = float(librosa.get_duration(y=y, sr=sr))

    # --- Tempo / BPM ---
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        bpm = float(tempo[0])
    else:
        bpm = float(tempo)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    # BPM confidence via tempogram autocorrelation
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
    bpm_confidence = float(np.clip(np.max(np.mean(tempogram, axis=1)) / 10.0, 0.0, 1.0))

    # --- Beat info ---
    beats = []
    for i, t in enumerate(beat_times):
        # Approximate strength from onset envelope
        frame_idx = librosa.time_to_frames([t], sr=sr)[0]
        strength = float(np.clip(onset_env[min(frame_idx, len(onset_env) - 1)] / (np.max(onset_env) + 1e-8), 0, 1))
        beats.append(BeatInfo(time=float(t), strength=strength))

    # --- Downbeats (estimate every Nth beat for time signature) ---
    time_sig = _estimate_time_signature(onset_env, sr, bpm)
    beats_per_measure = int(time_sig.split("/")[0])
    downbeats = [float(beat_times[i]) for i in range(0, len(beat_times), beats_per_measure)]

    # --- Structural segmentation ---
    sections = _segment_structure(y, sr, duration)

    return RhythmAnalysis(
        bpm=round(bpm, 1),
        bpm_confidence=round(bpm_confidence, 2),
        time_signature=time_sig,
        beats=beats,
        downbeats=downbeats,
        sections=sections,
        duration=round(duration, 2),
    )


def _estimate_time_signature(onset_env: np.ndarray, sr: int, bpm: float) -> str:
    """Estimate time signature from onset envelope periodicity."""
    # Simple heuristic: check accent patterns in onset envelope
    hop_length = 512
    frames_per_beat = (60.0 / bpm) * sr / hop_length

    if len(onset_env) < int(frames_per_beat * 8):
        return "4/4"

    # Check energy ratio at 3-beat vs 4-beat groupings
    energy_3 = 0.0
    energy_4 = 0.0
    count_3 = 0
    count_4 = 0

    for i in range(len(onset_env)):
        pos_in_3 = (i % int(frames_per_beat * 3))
        pos_in_4 = (i % int(frames_per_beat * 4))

        if pos_in_3 < frames_per_beat * 0.3:
            energy_3 += onset_env[i]
            count_3 += 1
        if pos_in_4 < frames_per_beat * 0.3:
            energy_4 += onset_env[i]
            count_4 += 1

    avg_3 = energy_3 / max(count_3, 1)
    avg_4 = energy_4 / max(count_4, 1)

    if avg_3 > avg_4 * 1.2:
        return "3/4"
    return "4/4"


def _segment_structure(y: np.ndarray, sr: int, duration: float) -> list[SongSection]:
    """Segment song into structural sections using spectral clustering.

    Uses librosa's recurrence matrix and spectral decomposition to find
    structural boundaries, then labels sections heuristically.
    """
    # Compute features for segmentation
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    features = np.vstack([
        librosa.util.normalize(mfcc, axis=1),
        librosa.util.normalize(chroma, axis=1),
    ])

    # Compute novelty curve from feature self-similarity using a checkerboard kernel
    from scipy.ndimage import convolve

    # Self-similarity via recurrence matrix
    rec = librosa.segment.recurrence_matrix(
        features,
        width=3,
        mode="affinity",
        sym=True,
    )

    # Checkerboard kernel novelty detection (replaces removed librosa.segment.novelty)
    kernel_size = 16
    k = np.ones((kernel_size, kernel_size))
    k[:kernel_size // 2, kernel_size // 2:] = -1
    k[kernel_size // 2:, :kernel_size // 2] = -1
    novelty = np.abs(convolve(rec.astype(float), k, mode="reflect").diagonal())

    # Pick peaks as boundaries
    hop_length = 512
    # features has shape (n_features, n_frames); use frame count to compute seconds-per-frame
    n_frames = features.shape[1]
    frames_per_sec = n_frames / max(duration, 1.0)
    min_segment_frames = int(15.0 * frames_per_sec)  # min 15 seconds per section

    peaks = []
    for i in range(1, len(novelty) - 1):
        if novelty[i] > novelty[i - 1] and novelty[i] > novelty[i + 1]:
            if novelty[i] > np.mean(novelty) + 1.0 * np.std(novelty):
                if not peaks or (i - peaks[-1]) >= min_segment_frames:
                    peaks.append(i)

    # peaks are indices into the feature/novelty array; convert to time
    boundary_times = [0.0] + [float(p / frames_per_sec) for p in peaks] + [duration]

    # Label sections heuristically based on position and energy
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    sections = []
    n_sections = len(boundary_times) - 1

    for i in range(n_sections):
        start = boundary_times[i]
        end = boundary_times[i + 1]

        # Compute segment energy
        start_frame = librosa.time_to_frames(start, sr=sr)
        end_frame = librosa.time_to_frames(end, sr=sr)
        end_frame = min(end_frame, len(onset_env))
        if start_frame < end_frame:
            seg_energy = float(np.mean(onset_env[start_frame:end_frame]))
        else:
            seg_energy = 0.0

        label = _label_section(i, n_sections, seg_energy, onset_env, start, end, duration)
        sections.append(SongSection(
            label=label,
            start=round(start, 2),
            end=round(end, 2),
            confidence=0.5,
        ))

    return sections


def _label_section(
    idx: int,
    total: int,
    energy: float,
    onset_env: np.ndarray,
    start: float,
    end: float,
    duration: float,
) -> str:
    """Heuristically label a section based on position and energy."""
    mean_energy = float(np.mean(onset_env)) if len(onset_env) > 0 else 0.0
    relative_pos = start / max(duration, 1.0)

    # First section → intro
    if idx == 0 and (end - start) < duration * 0.2:
        return "intro"

    # Last section → outro
    if idx == total - 1 and relative_pos > 0.75:
        return "outro"

    # High energy → chorus
    if energy > mean_energy * 1.3:
        # Count previous choruses
        chorus_count = idx  # simplified
        return f"chorus"

    # Medium-low energy in middle → bridge
    if 0.5 < relative_pos < 0.8 and energy < mean_energy * 0.9:
        return "bridge"

    # Default → verse
    return "verse"
