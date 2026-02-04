"""Emotion analysis: mood classification, energy, valence, genre.

Uses CLAP (laion-clap) when available, falls back to librosa-based
spectral heuristics.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import librosa

from music_analyzer.config import HAS_CLAP
from music_analyzer.models import EmotionAnalysis


# Emotion labels for CLAP classification
_CLAP_EMOTION_LABELS = [
    "happy", "sad", "angry", "calm", "energetic", "melancholic",
    "romantic", "dark", "dreamy", "aggressive", "peaceful", "epic",
    "nostalgic", "playful", "mysterious", "uplifting",
]

_CLAP_GENRE_LABELS = [
    "pop", "rock", "hip-hop", "electronic", "jazz", "classical",
    "r&b", "country", "folk", "metal", "ambient", "latin",
    "blues", "reggae", "funk", "soul",
]

# Heuristic mood mapping based on spectral/rhythm features
_MOOD_MAP = {
    "high_energy_major": {"emotion": "happy", "tags": ["upbeat", "bright", "joyful"]},
    "high_energy_minor": {"emotion": "angry", "tags": ["intense", "aggressive", "powerful"]},
    "low_energy_major": {"emotion": "calm", "tags": ["peaceful", "relaxing", "gentle"]},
    "low_energy_minor": {"emotion": "melancholic", "tags": ["sad", "reflective", "somber"]},
    "mid_energy_major": {"emotion": "uplifting", "tags": ["hopeful", "warm", "positive"]},
    "mid_energy_minor": {"emotion": "mysterious", "tags": ["atmospheric", "contemplative"]},
}


def analyze_emotion(
    y: np.ndarray,
    sr: int,
    key_mode: Optional[str] = None,
    bpm: Optional[float] = None,
) -> EmotionAnalysis:
    """Analyze emotional content of audio.

    Parameters
    ----------
    y : audio waveform (mono)
    sr : sample rate
    key_mode : detected key mode ('major' or 'minor') for heuristic fallback
    bpm : detected BPM for heuristic fallback
    """
    if HAS_CLAP:
        try:
            return _analyze_clap(y, sr)
        except Exception:
            pass

    return _analyze_heuristic(y, sr, key_mode, bpm)


def _analyze_heuristic(
    y: np.ndarray,
    sr: int,
    key_mode: Optional[str] = None,
    bpm: Optional[float] = None,
) -> EmotionAnalysis:
    """Heuristic emotion analysis using spectral and rhythm features."""
    duration = float(librosa.get_duration(y=y, sr=sr))

    # --- Energy ---
    rms = librosa.feature.rms(y=y)[0]
    # Use percentile-based normalization to avoid saturation
    rms_ref = float(np.percentile(rms, 95)) if len(rms) > 0 else 0.15
    rms_ref = max(rms_ref, 0.01)
    overall_energy = float(np.clip(np.mean(rms) / rms_ref, 0, 1))

    # Energy curve (split into ~10 segments)
    n_segments = min(10, max(1, int(duration / 5)))
    seg_len = len(rms) // max(n_segments, 1)
    energy_curve = []
    for i in range(n_segments):
        seg = rms[i * seg_len:(i + 1) * seg_len]
        if len(seg) > 0:
            energy_curve.append(round(float(np.clip(np.mean(seg) / rms_ref, 0, 1)), 3))

    # --- Spectral features for mood ---
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))

    # Brightness indicator (high spectral centroid = brighter)
    brightness = float(np.clip(spectral_centroid / (sr / 2), 0, 1))

    # --- Valence estimation ---
    # Major = positive, minor = negative, brightness adds positivity
    mode = key_mode or "major"
    mode_val = 0.3 if mode == "major" else -0.3
    brightness_val = (brightness - 0.3) * 0.5
    energy_val = (overall_energy - 0.5) * 0.2
    valence = float(np.clip(mode_val + brightness_val + energy_val, -1, 1))

    # --- Arousal estimation ---
    # High BPM + high energy = high arousal
    tempo = bpm or 120
    tempo_arousal = float(np.clip((tempo - 60) / 140, 0, 1))
    arousal = float(np.clip((overall_energy * 0.6 + tempo_arousal * 0.4), 0, 1))

    # --- Mood classification ---
    if overall_energy > 0.65:
        energy_level = "high_energy"
    elif overall_energy < 0.35:
        energy_level = "low_energy"
    else:
        energy_level = "mid_energy"

    mood_key = f"{energy_level}_{mode}"
    mood_info = _MOOD_MAP.get(mood_key, _MOOD_MAP["mid_energy_major"])

    primary_emotion = mood_info["emotion"]
    mood_tags = mood_info["tags"]

    # Additional tags based on features
    if tempo and tempo > 140:
        mood_tags.append("fast-paced")
    elif tempo and tempo < 80:
        mood_tags.append("slow")

    if brightness > 0.4:
        mood_tags.append("bright")
    else:
        mood_tags.append("warm")

    # --- Genre heuristic ---
    genre = _guess_genre_heuristic(overall_energy, brightness, tempo or 120, float(zcr))

    return EmotionAnalysis(
        primary_emotion=primary_emotion,
        secondary_emotions=[mood_info["emotion"]],
        overall_energy=round(overall_energy, 3),
        energy_curve=energy_curve,
        valence=round(valence, 3),
        arousal=round(arousal, 3),
        genre=genre,
        mood_tags=mood_tags,
        method="heuristic",
    )


def _guess_genre_heuristic(energy: float, brightness: float, bpm: float, zcr: float) -> str:
    """Very rough genre guess based on audio features."""
    if bpm > 125 and energy > 0.6:
        if brightness > 0.4:
            return "electronic"
        return "hip-hop"
    if bpm < 85 and energy < 0.3:
        if brightness < 0.2:
            return "ambient"
        return "classical"
    if energy > 0.7 and zcr > 0.1:
        return "rock"
    if 85 <= bpm <= 125 and energy < 0.5:
        return "jazz"
    if brightness > 0.35 and 90 <= bpm <= 130:
        return "pop"
    return "unknown"


def _analyze_clap(y: np.ndarray, sr: int) -> EmotionAnalysis:
    """CLAP-based emotion and genre classification."""
    import torch
    import laion_clap

    # Load CLAP model
    model = laion_clap.CLAP_Module(enable_fusion=False)
    model.load_ckpt()

    # Resample to 48kHz for CLAP
    if sr != 48000:
        y_48k = librosa.resample(y, orig_sr=sr, target_sr=48000)
    else:
        y_48k = y

    # Get audio embedding
    audio_embed = model.get_audio_embedding_from_data(
        [y_48k], use_tensor=True
    )

    # Classify emotions
    emotion_texts = [f"This music sounds {e}" for e in _CLAP_EMOTION_LABELS]
    text_embed = model.get_text_embedding(emotion_texts, use_tensor=True)

    similarity = torch.nn.functional.cosine_similarity(
        audio_embed.unsqueeze(1),
        text_embed.unsqueeze(0),
        dim=2,
    )[0]

    emotion_scores = torch.softmax(similarity * 10, dim=0).cpu().numpy()
    top_idx = int(np.argmax(emotion_scores))
    primary_emotion = _CLAP_EMOTION_LABELS[top_idx]

    # Top 3 secondary emotions
    sorted_indices = np.argsort(emotion_scores)[::-1]
    secondary = [_CLAP_EMOTION_LABELS[i] for i in sorted_indices[1:4]]

    # Classify genre
    genre_texts = [f"This is {g} music" for g in _CLAP_GENRE_LABELS]
    genre_embed = model.get_text_embedding(genre_texts, use_tensor=True)
    genre_sim = torch.nn.functional.cosine_similarity(
        audio_embed.unsqueeze(1),
        genre_embed.unsqueeze(0),
        dim=2,
    )[0]
    genre_scores = torch.softmax(genre_sim * 10, dim=0).cpu().numpy()
    genre = _CLAP_GENRE_LABELS[int(np.argmax(genre_scores))]

    # Compute energy/valence/arousal from features + CLAP hints
    rms = librosa.feature.rms(y=y, sr=sr)[0]
    overall_energy = float(np.clip(np.mean(rms) / 0.15, 0, 1))

    duration = float(librosa.get_duration(y=y, sr=sr))
    n_segments = min(10, max(1, int(duration / 5)))
    seg_len = len(rms) // max(n_segments, 1)
    energy_curve = []
    for i in range(n_segments):
        seg = rms[i * seg_len:(i + 1) * seg_len]
        if len(seg) > 0:
            energy_curve.append(round(float(np.clip(np.mean(seg) / 0.15, 0, 1)), 3))

    # Valence from emotion type
    positive_emotions = {"happy", "calm", "uplifting", "playful", "romantic", "peaceful"}
    valence = 0.5 if primary_emotion in positive_emotions else -0.3
    arousal = overall_energy

    # Mood tags
    mood_tags = [primary_emotion] + secondary

    return EmotionAnalysis(
        primary_emotion=primary_emotion,
        secondary_emotions=secondary,
        overall_energy=round(overall_energy, 3),
        energy_curve=energy_curve,
        valence=round(valence, 3),
        arousal=round(arousal, 3),
        genre=genre,
        mood_tags=mood_tags,
        method="clap",
    )
