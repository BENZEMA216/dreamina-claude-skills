"""Timbre analysis: MFCC, spectral features, loudness, source separation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np
import librosa

from music_analyzer.config import CACHE_DIR, HAS_DEMUCS, HAS_PYLOUDNORM
from music_analyzer.models import MFCCSummary, SpectralFeatures, StemPaths, TimbreAnalysis


def analyze_timbre(
    y: np.ndarray,
    sr: int,
    audio_path: Optional[Path] = None,
    run_separation: bool = True,
) -> TimbreAnalysis:
    """Run timbre and spectral analysis.

    Parameters
    ----------
    y : audio waveform (mono)
    sr : sample rate
    audio_path : original file path (needed for source separation)
    run_separation : whether to run demucs source separation
    """
    # --- MFCC ---
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_summary = MFCCSummary(
        means=[round(float(m), 4) for m in np.mean(mfcc, axis=1)],
        stds=[round(float(s), 4) for s in np.std(mfcc, axis=1)],
        n_mfcc=13,
    )

    # --- Spectral features ---
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    zcr = librosa.feature.zero_crossing_rate(y)[0]

    spectral = SpectralFeatures(
        spectral_centroid_mean=round(float(np.mean(spectral_centroid)), 1),
        spectral_centroid_std=round(float(np.std(spectral_centroid)), 1),
        spectral_bandwidth_mean=round(float(np.mean(spectral_bandwidth)), 1),
        spectral_rolloff_mean=round(float(np.mean(spectral_rolloff)), 1),
        zero_crossing_rate_mean=round(float(np.mean(zcr)), 6),
    )

    # --- Loudness ---
    loudness_lufs = None
    loudness_range = None
    if HAS_PYLOUDNORM:
        try:
            import pyloudnorm as pyln
            meter = pyln.Meter(sr)
            # pyloudnorm expects float64 and at least 0.4s
            if len(y) > int(0.4 * sr):
                loudness_lufs = round(float(meter.integrated_loudness(y.astype(np.float64))), 1)
        except Exception:
            pass

    # --- Dynamic range ---
    rms = librosa.feature.rms(y=y)[0]
    rms_nonzero = rms[rms > 0]
    if len(rms_nonzero) > 10:
        rms_db = librosa.amplitude_to_db(rms_nonzero)
        dynamic_range = float(np.percentile(rms_db, 95) - np.percentile(rms_db, 5))
    else:
        dynamic_range = 0.0

    # --- Brightness (normalized spectral centroid) ---
    # Nyquist as upper reference
    nyquist = sr / 2.0
    brightness = float(np.clip(np.mean(spectral_centroid) / nyquist, 0, 1))

    # --- Warmth (ratio of low-frequency energy) ---
    S = np.abs(librosa.stft(y))
    freqs = librosa.fft_frequencies(sr=sr)
    low_mask = freqs < 500
    total_energy = float(np.sum(S ** 2))
    low_energy = float(np.sum(S[low_mask, :] ** 2)) if np.any(low_mask) else 0.0
    warmth = float(np.clip(low_energy / max(total_energy, 1e-8), 0, 1))

    # --- Source separation (Demucs) ---
    stems = None
    if run_separation and HAS_DEMUCS and audio_path is not None:
        stems = _run_demucs(audio_path)

    return TimbreAnalysis(
        mfcc=mfcc_summary,
        spectral=spectral,
        loudness_lufs=loudness_lufs,
        loudness_range=loudness_range,
        dynamic_range_db=round(dynamic_range, 1),
        brightness=round(brightness, 3),
        warmth=round(warmth, 3),
        stems=stems,
    )


def _run_demucs(audio_path: Path) -> Optional[StemPaths]:
    """Run Demucs source separation and return stem paths."""
    try:
        import subprocess

        output_dir = CACHE_DIR / "stems" / audio_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [
                sys.executable, "-m", "demucs",
                "--out", str(output_dir),
                "--two-stems", "vocals",
                str(audio_path),
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            print(f"Demucs warning: {result.stderr[:200]}", file=sys.stderr)
            return None

        # Find output stems
        stem_dir = None
        for d in output_dir.iterdir():
            if d.is_dir():
                stem_dir = d
                break

        if stem_dir is None:
            return None

        stems = StemPaths()
        for stem_file in stem_dir.iterdir():
            name = stem_file.stem.lower()
            if "vocal" in name:
                stems.vocals = str(stem_file)
            elif "drum" in name:
                stems.drums = str(stem_file)
            elif "bass" in name:
                stems.bass = str(stem_file)
            elif "other" in name or "no_vocal" in name:
                stems.other = str(stem_file)

        return stems
    except Exception as e:
        print(f"Demucs error: {e}", file=sys.stderr)
        return None
