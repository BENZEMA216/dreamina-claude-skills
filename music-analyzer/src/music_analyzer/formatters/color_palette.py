"""Color palette generator from musical mood and tonality."""

from __future__ import annotations

from music_analyzer.models import ColorPalette, MusicAnalysisResult

# ---------------------------------------------------------------------------
# Base color mappings by emotion + mode
# ---------------------------------------------------------------------------

_PALETTES = {
    # (emotion, mode) → palette dict
    ("happy", "major"): {
        "primary": "#FFD700",
        "secondary": "#FF6B35",
        "accent": "#FF1493",
        "background": "#FFFAF0",
        "text": "#2F2F2F",
        "palette": ["#FFD700", "#FF6B35", "#FFA07A", "#FFEC8B", "#FF1493", "#FFFAF0"],
        "mood_association": "joyful warmth",
    },
    ("happy", "minor"): {
        "primary": "#FFA500",
        "secondary": "#CD853F",
        "accent": "#FF6347",
        "background": "#FFF8E7",
        "text": "#333333",
        "palette": ["#FFA500", "#CD853F", "#FF6347", "#DEB887", "#FFD700", "#FFF8E7"],
        "mood_association": "bittersweet joy",
    },
    ("sad", "minor"): {
        "primary": "#4682B4",
        "secondary": "#708090",
        "accent": "#5F9EA0",
        "background": "#F0F4F8",
        "text": "#2C3E50",
        "palette": ["#4682B4", "#708090", "#5F9EA0", "#87CEEB", "#B0C4DE", "#F0F4F8"],
        "mood_association": "melancholic blue",
    },
    ("sad", "major"): {
        "primary": "#6495ED",
        "secondary": "#87CEEB",
        "accent": "#DDA0DD",
        "background": "#F5F5FF",
        "text": "#2C3E50",
        "palette": ["#6495ED", "#87CEEB", "#DDA0DD", "#B0C4DE", "#E6E6FA", "#F5F5FF"],
        "mood_association": "gentle sorrow",
    },
    ("angry", "minor"): {
        "primary": "#DC143C",
        "secondary": "#8B0000",
        "accent": "#FF4500",
        "background": "#1A1A1A",
        "text": "#F5F5F5",
        "palette": ["#DC143C", "#8B0000", "#FF4500", "#B22222", "#FF6347", "#1A1A1A"],
        "mood_association": "fierce rage",
    },
    ("angry", "major"): {
        "primary": "#FF4500",
        "secondary": "#FF6347",
        "accent": "#FFD700",
        "background": "#2C1810",
        "text": "#F5F5F5",
        "palette": ["#FF4500", "#FF6347", "#FFD700", "#DC143C", "#FF8C00", "#2C1810"],
        "mood_association": "fiery intensity",
    },
    ("calm", "major"): {
        "primary": "#98D8C8",
        "secondary": "#B8E6B8",
        "accent": "#87CEEB",
        "background": "#F0FFF0",
        "text": "#2F4F4F",
        "palette": ["#98D8C8", "#B8E6B8", "#87CEEB", "#E6F2E6", "#AFEEEE", "#F0FFF0"],
        "mood_association": "serene nature",
    },
    ("calm", "minor"): {
        "primary": "#5F9EA0",
        "secondary": "#708090",
        "accent": "#B0C4DE",
        "background": "#F0F5F5",
        "text": "#2F4F4F",
        "palette": ["#5F9EA0", "#708090", "#B0C4DE", "#AFEEEE", "#D3D3D3", "#F0F5F5"],
        "mood_association": "quiet contemplation",
    },
    ("energetic", "major"): {
        "primary": "#FF1493",
        "secondary": "#FFD700",
        "accent": "#00FF7F",
        "background": "#0D0D0D",
        "text": "#FFFFFF",
        "palette": ["#FF1493", "#FFD700", "#00FF7F", "#FF6347", "#7CFC00", "#0D0D0D"],
        "mood_association": "electric vitality",
    },
    ("energetic", "minor"): {
        "primary": "#FF4500",
        "secondary": "#8B008B",
        "accent": "#00CED1",
        "background": "#121212",
        "text": "#F5F5F5",
        "palette": ["#FF4500", "#8B008B", "#00CED1", "#FF1493", "#7B68EE", "#121212"],
        "mood_association": "dark energy",
    },
    ("melancholic", "minor"): {
        "primary": "#6A5ACD",
        "secondary": "#483D8B",
        "accent": "#DDA0DD",
        "background": "#1A1A2E",
        "text": "#D3D3D3",
        "palette": ["#6A5ACD", "#483D8B", "#DDA0DD", "#778899", "#9370DB", "#1A1A2E"],
        "mood_association": "deep melancholy",
    },
    ("melancholic", "major"): {
        "primary": "#9370DB",
        "secondary": "#B0C4DE",
        "accent": "#DEB887",
        "background": "#F5F0FF",
        "text": "#4B4B4B",
        "palette": ["#9370DB", "#B0C4DE", "#DEB887", "#C0C0C0", "#E6E6FA", "#F5F0FF"],
        "mood_association": "wistful nostalgia",
    },
    ("romantic", "major"): {
        "primary": "#FF69B4",
        "secondary": "#FFB6C1",
        "accent": "#FFD700",
        "background": "#FFF0F5",
        "text": "#4B2040",
        "palette": ["#FF69B4", "#FFB6C1", "#FFD700", "#DDA0DD", "#FFC0CB", "#FFF0F5"],
        "mood_association": "romantic bloom",
    },
    ("romantic", "minor"): {
        "primary": "#C71585",
        "secondary": "#8B008B",
        "accent": "#FFD700",
        "background": "#2C0A2C",
        "text": "#F5F5F5",
        "palette": ["#C71585", "#8B008B", "#FFD700", "#DA70D6", "#4B0082", "#2C0A2C"],
        "mood_association": "passionate desire",
    },
}

# Default fallback
_DEFAULT_PALETTE = {
    "primary": "#607D8B",
    "secondary": "#90A4AE",
    "accent": "#FF9800",
    "background": "#FAFAFA",
    "text": "#212121",
    "palette": ["#607D8B", "#90A4AE", "#FF9800", "#B0BEC5", "#FFB74D", "#FAFAFA"],
    "mood_association": "neutral",
}


def generate_color_palette(result: MusicAnalysisResult) -> ColorPalette:
    """Generate a color palette from music analysis result."""
    emotion = result.emotion
    tonality = result.tonality

    primary_emotion = emotion.primary_emotion if emotion else "calm"
    mode = tonality.mode if tonality else "major"

    # Look up palette
    key = (primary_emotion, mode)
    palette_data = _PALETTES.get(key)

    # Try emotion-only match
    if palette_data is None:
        for k, v in _PALETTES.items():
            if k[0] == primary_emotion:
                palette_data = v
                break

    if palette_data is None:
        palette_data = _DEFAULT_PALETTE

    return ColorPalette(**palette_data)
