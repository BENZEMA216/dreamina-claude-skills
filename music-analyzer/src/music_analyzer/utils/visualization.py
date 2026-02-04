"""Visualization utilities for spectrograms and waveforms."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np


def save_waveform(
    y: np.ndarray,
    sr: int,
    output_path: str | Path,
    title: str = "Waveform",
    figsize: tuple = (12, 3),
) -> Path:
    """Save a waveform plot to disk."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa.display

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    librosa.display.waveshow(y, sr=sr, ax=ax, color="#4A90D9")
    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    fig.tight_layout()
    out = Path(output_path)
    fig.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def save_spectrogram(
    y: np.ndarray,
    sr: int,
    output_path: str | Path,
    title: str = "Mel Spectrogram",
    figsize: tuple = (12, 4),
) -> Path:
    """Save a mel spectrogram plot to disk."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa
    import librosa.display

    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    S_db = librosa.power_to_db(S, ref=np.max)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    img = librosa.display.specshow(S_db, sr=sr, x_axis="time", y_axis="mel", ax=ax, cmap="magma")
    ax.set_title(title)
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    fig.tight_layout()
    out = Path(output_path)
    fig.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def save_chromagram(
    y: np.ndarray,
    sr: int,
    output_path: str | Path,
    title: str = "Chromagram",
    figsize: tuple = (12, 4),
) -> Path:
    """Save a chromagram plot to disk."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa
    import librosa.display

    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    librosa.display.specshow(chroma, sr=sr, x_axis="time", y_axis="chroma", ax=ax, cmap="coolwarm")
    ax.set_title(title)
    fig.tight_layout()
    out = Path(output_path)
    fig.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def save_beat_grid(
    y: np.ndarray,
    sr: int,
    beat_times: list[float],
    output_path: str | Path,
    sections: Optional[list[dict]] = None,
    title: str = "Beat Grid",
    figsize: tuple = (14, 4),
) -> Path:
    """Save a waveform with beat markers and optional section highlights."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa.display

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    librosa.display.waveshow(y, sr=sr, ax=ax, color="#AAAAAA", alpha=0.5)

    # Plot beat markers
    for t in beat_times:
        ax.axvline(x=t, color="#E74C3C", alpha=0.4, linewidth=0.5)

    # Highlight sections
    if sections:
        colors = {
            "intro": "#3498DB",
            "verse": "#2ECC71",
            "chorus": "#E74C3C",
            "bridge": "#9B59B6",
            "outro": "#95A5A6",
        }
        for sec in sections:
            label = sec.get("label", "").split("_")[0].lower()
            color = colors.get(label, "#F39C12")
            ax.axvspan(sec["start"], sec["end"], alpha=0.15, color=color, label=sec.get("label", ""))

    ax.set_title(title)
    ax.set_xlabel("Time (s)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out = Path(output_path)
    fig.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out
