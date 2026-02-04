"""Tonality analysis: key detection, chord progression, melody contour."""

from __future__ import annotations

import numpy as np
import librosa

from music_analyzer.config import HAS_ESSENTIA
from music_analyzer.models import ChordEvent, TonalityAnalysis


# Pitch class names for librosa key detection
_PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Krumhansl-Schmuckler key profiles
_MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Simple chord templates (major and minor triads)
_CHORD_TEMPLATES = {}
for i, name in enumerate(_PITCH_CLASSES):
    # Major triad: root, major third, perfect fifth
    major = np.zeros(12)
    major[i] = 1.0
    major[(i + 4) % 12] = 0.8
    major[(i + 7) % 12] = 0.8
    _CHORD_TEMPLATES[name] = major

    # Minor triad: root, minor third, perfect fifth
    minor = np.zeros(12)
    minor[i] = 1.0
    minor[(i + 3) % 12] = 0.8
    minor[(i + 7) % 12] = 0.8
    _CHORD_TEMPLATES[f"{name}m"] = minor


def analyze_tonality(y: np.ndarray, sr: int) -> TonalityAnalysis:
    """Run tonality analysis on audio waveform.

    Uses essentia if available, otherwise falls back to librosa-based
    Krumhansl-Schmuckler key detection and template-based chord matching.
    """
    if HAS_ESSENTIA:
        try:
            return _analyze_essentia(y, sr)
        except Exception:
            pass  # Fall through to librosa

    return _analyze_librosa(y, sr)


def _analyze_librosa(y: np.ndarray, sr: int) -> TonalityAnalysis:
    """Librosa-based tonality analysis."""
    # --- Key detection via Krumhansl-Schmuckler ---
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    best_key = ""
    best_mode = "major"
    best_corr = -1.0

    for shift in range(12):
        rotated = np.roll(chroma_mean, -shift)

        corr_major = float(np.corrcoef(rotated, _MAJOR_PROFILE)[0, 1])
        corr_minor = float(np.corrcoef(rotated, _MINOR_PROFILE)[0, 1])

        if corr_major > best_corr:
            best_corr = corr_major
            best_key = _PITCH_CLASSES[shift]
            best_mode = "major"
        if corr_minor > best_corr:
            best_corr = corr_minor
            best_key = _PITCH_CLASSES[shift]
            best_mode = "minor"

    key_confidence = float(np.clip(best_corr, 0.0, 1.0))

    # --- Chord detection via template matching ---
    hop_length = 512
    # Use ~0.5 second windows for chord detection
    frames_per_chord = max(1, int(0.5 * sr / hop_length))
    chords = _detect_chords_template(chroma, sr, frames_per_chord)

    # --- Melody contour (simplified: use pitch from predominant frequency) ---
    melody_contour = _extract_melody_contour(y, sr)

    key_label = f"{best_key} {best_mode}"
    return TonalityAnalysis(
        key=key_label,
        key_confidence=round(key_confidence, 2),
        mode=best_mode,
        chords=chords,
        melody_contour=melody_contour,
        method="librosa",
    )


def _detect_chords_template(
    chroma: np.ndarray, sr: int, frames_per_chord: int
) -> list[ChordEvent]:
    """Detect chords by template matching on chroma windows."""
    hop_length = 512
    chords = []
    n_frames = chroma.shape[1]

    prev_chord = ""
    chord_start = 0.0

    for i in range(0, n_frames, frames_per_chord):
        end_frame = min(i + frames_per_chord, n_frames)
        window = np.mean(chroma[:, i:end_frame], axis=1)

        # Normalize
        norm = np.linalg.norm(window)
        if norm < 1e-6:
            continue
        window = window / norm

        # Match against templates
        best_label = "N"
        best_score = 0.3  # minimum threshold

        for label, template in _CHORD_TEMPLATES.items():
            t_norm = template / np.linalg.norm(template)
            score = float(np.dot(window, t_norm))
            if score > best_score:
                best_score = score
                best_label = label

        current_time = float(librosa.frames_to_time(i, sr=sr, hop_length=hop_length))

        if best_label != prev_chord:
            if prev_chord and prev_chord != "N":
                chords.append(ChordEvent(
                    time=round(chord_start, 2),
                    duration=round(current_time - chord_start, 2),
                    chord=prev_chord,
                    confidence=round(best_score, 2),
                ))
            chord_start = current_time
            prev_chord = best_label

    # Append last chord
    if prev_chord and prev_chord != "N":
        final_time = float(librosa.frames_to_time(n_frames, sr=sr, hop_length=hop_length))
        chords.append(ChordEvent(
            time=round(chord_start, 2),
            duration=round(final_time - chord_start, 2),
            chord=prev_chord,
            confidence=0.5,
        ))

    return chords


def _extract_melody_contour(y: np.ndarray, sr: int, max_points: int = 200) -> list[float]:
    """Extract a simplified melody pitch contour using piptrack."""
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    # Pick strongest pitch per frame
    contour = []
    for t in range(pitches.shape[1]):
        mag_col = magnitudes[:, t]
        if np.max(mag_col) < 0.01:
            contour.append(0.0)
        else:
            idx = np.argmax(mag_col)
            contour.append(float(pitches[idx, t]))

    # Downsample to max_points
    if len(contour) > max_points:
        step = len(contour) / max_points
        contour = [contour[int(i * step)] for i in range(max_points)]

    return [round(v, 1) for v in contour]


def _analyze_essentia(y: np.ndarray, sr: int) -> TonalityAnalysis:
    """Essentia-based tonality analysis (more accurate key/chord detection)."""
    import essentia.standard as es

    # Convert to essentia format (float32, mono)
    audio = y.astype(np.float32)

    # Key detection
    key_extractor = es.KeyExtractor()
    key, scale, key_strength = key_extractor(audio)

    mode = "major" if scale == "major" else "minor"
    key_label = f"{key} {mode}"

    # Chord detection using essentia's HPCP + chord templates
    chords = _detect_chords_essentia(audio, sr)

    # Melody contour (reuse librosa for simplicity)
    melody_contour = _extract_melody_contour(y, sr)

    return TonalityAnalysis(
        key=key_label,
        key_confidence=round(float(key_strength), 2),
        mode=mode,
        chords=chords,
        melody_contour=melody_contour,
        method="essentia",
    )


def _detect_chords_essentia(audio: np.ndarray, sr: int) -> list[ChordEvent]:
    """Detect chords using essentia's ChordsDetection."""
    try:
        import essentia.standard as es

        hpcp_extractor = es.HPCP(
            size=36,
            referenceFrequency=440.0,
            harmonics=8,
            bandPreset=True,
            minFrequency=40.0,
            maxFrequency=5000.0,
        )

        # Frame-based analysis
        frame_size = 8192
        hop_size = 4096
        frames = es.FrameGenerator(audio, frameSize=frame_size, hopSize=hop_size)

        hpcps = []
        for frame in frames:
            spectrum = es.Spectrum(size=frame_size)(es.Windowing(type="blackmanharris62")(frame))
            peaks_freq, peaks_mag = es.SpectralPeaks(
                orderBy="magnitude",
                magnitudeThreshold=0.001,
                maxPeaks=100,
                minFrequency=40.0,
                maxFrequency=5000.0,
                sampleRate=float(sr),
            )(spectrum)
            hpcp = hpcp_extractor(peaks_freq, peaks_mag)
            hpcps.append(hpcp)

        if not hpcps:
            return []

        hpcps_array = np.array(hpcps)
        chords_detection = es.ChordsDetection(hopSize=hop_size, sampleRate=float(sr))
        chord_labels, chord_strengths = chords_detection(hpcps_array)

        chords = []
        prev_label = ""
        chord_start = 0.0
        time_per_frame = hop_size / sr

        for i, label in enumerate(chord_labels):
            current_time = i * time_per_frame
            if label != prev_label:
                if prev_label and prev_label != "N":
                    chords.append(ChordEvent(
                        time=round(chord_start, 2),
                        duration=round(current_time - chord_start, 2),
                        chord=prev_label,
                        confidence=round(float(chord_strengths[i - 1] if i > 0 else 0.5), 2),
                    ))
                chord_start = current_time
                prev_label = label

        return chords
    except Exception:
        return []
