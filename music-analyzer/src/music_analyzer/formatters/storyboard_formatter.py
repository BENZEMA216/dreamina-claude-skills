"""Storyboard formatter: maps music analysis to shot-by-shot storyboard.

Section-to-shot mapping:
- 前奏 (intro): 远景→中景, slow push-in, environment establishing
- 主歌 (verse): 中景/近景, static/slow pan, narrative focus
- 副歌 (chorus): 全景/特写, orbit/fast push, visual climax
- 桥段 (bridge): 特写/远景, slow pull-out, contrast/reflection
- 尾奏 (outro): 远景, slow pull-out/fade, closure

Output is compatible with pull-film's storyboard-generator format.
"""

from __future__ import annotations

from music_analyzer.models import (
    MusicAnalysisResult,
    StoryboardOutput,
    StoryboardShot,
)

# ---------------------------------------------------------------------------
# Section-to-shot defaults
# ---------------------------------------------------------------------------

SECTION_SHOT_DEFAULTS = {
    "intro": {
        "shot_type": "wide",
        "camera_movement": "slow dolly in",
        "visual_zh": "环境建立，氛围铺垫，远景到中景过渡",
        "visual_en": "environment establishing, atmosphere building, wide to medium transition",
        "transition": "fade",
    },
    "verse": {
        "shot_type": "medium",
        "camera_movement": "static",
        "visual_zh": "叙事推进，人物聚焦，中景稳定画面",
        "visual_en": "narrative progression, character focus, stable medium shot",
        "transition": "cut",
    },
    "chorus": {
        "shot_type": "wide",
        "camera_movement": "orbit",
        "visual_zh": "视觉高潮，强烈色彩，动态全景",
        "visual_en": "visual climax, vivid colors, dynamic wide shot",
        "transition": "cut",
    },
    "bridge": {
        "shot_type": "close-up",
        "camera_movement": "slow dolly out",
        "visual_zh": "情绪转折，细节特写到远景拉出",
        "visual_en": "emotional shift, close-up detail pulling to wide",
        "transition": "dissolve",
    },
    "outro": {
        "shot_type": "wide",
        "camera_movement": "slow dolly out",
        "visual_zh": "收束余韵，画面渐远，淡出结束",
        "visual_en": "closing, camera pulling away, fading out",
        "transition": "fade",
    },
}


def format_storyboard(result: MusicAnalysisResult) -> StoryboardOutput:
    """Convert full analysis result to a storyboard."""
    rhythm = result.rhythm
    emotion = result.emotion
    tonality = result.tonality

    bpm = rhythm.bpm if rhythm else 120
    key = tonality.key if tonality else ""
    sections = rhythm.sections if rhythm else []
    primary_emotion = emotion.primary_emotion if emotion else "calm"
    overall_energy = emotion.overall_energy if emotion else 0.5
    genre = emotion.genre if emotion else "unknown"

    shots = []

    if not sections:
        # No structural segmentation — create default 3-act structure
        dur = result.duration
        sections_fallback = [
            {"label": "intro", "start": 0, "end": dur * 0.1},
            {"label": "verse", "start": dur * 0.1, "end": dur * 0.35},
            {"label": "chorus", "start": 0.35 * dur, "end": dur * 0.6},
            {"label": "verse", "start": dur * 0.6, "end": dur * 0.75},
            {"label": "chorus", "start": dur * 0.75, "end": dur * 0.9},
            {"label": "outro", "start": dur * 0.9, "end": dur},
        ]
    else:
        sections_fallback = [
            {"label": s.label, "start": s.start, "end": s.end}
            for s in sections
        ]

    for i, sec in enumerate(sections_fallback):
        label = sec["label"].split("_")[0].lower()
        defaults = SECTION_SHOT_DEFAULTS.get(label, SECTION_SHOT_DEFAULTS["verse"])
        start = sec["start"]
        end = sec["end"]
        duration = end - start

        # Energy-adjusted shot type
        section_energy = _section_energy(label, overall_energy)

        # Enhance defaults based on energy
        shot_type = defaults["shot_type"]
        camera_movement = defaults["camera_movement"]
        if section_energy > 0.7:
            if label == "chorus":
                camera_movement = "fast orbit"
                shot_type = "wide"
            elif label == "verse":
                camera_movement = "slow pan"

        # Build visual description
        mood_desc_zh = _mood_visual_zh(primary_emotion, genre, label, section_energy)
        mood_desc_en = _mood_visual_en(primary_emotion, genre, label, section_energy)

        visual_zh = f"{defaults['visual_zh']}，{mood_desc_zh}"
        visual_en = f"{defaults['visual_en']}, {mood_desc_en}"

        # Color palette for this section
        from music_analyzer.formatters.dreamina_formatter import _emotion_to_colors
        colors = _emotion_to_colors(primary_emotion, section_energy)

        shot = StoryboardShot(
            shot_number=i + 1,
            section=sec["label"],
            time_range={"start": round(start, 2), "end": round(end, 2)},
            duration=round(duration, 2),
            shot_type=shot_type,
            camera_movement=camera_movement,
            visual_description_zh=visual_zh,
            visual_description_en=visual_en,
            mood=primary_emotion,
            color_palette=colors,
            transition=defaults["transition"],
            energy_level=round(section_energy, 2),
        )
        shots.append(shot)

    return StoryboardOutput(
        song_title=result.file_name,
        total_duration=result.duration,
        bpm=bpm,
        key=key,
        shots=shots,
        global_mood=primary_emotion,
        global_style=genre,
    )


def _section_energy(label: str, overall_energy: float) -> float:
    """Compute section-specific energy level."""
    multipliers = {
        "intro": 0.4,
        "verse": 0.7,
        "chorus": 1.3,
        "bridge": 0.8,
        "outro": 0.4,
    }
    mult = multipliers.get(label, 0.7)
    return min(1.0, overall_energy * mult)


def _mood_visual_zh(emotion: str, genre: str, section: str, energy: float) -> str:
    """Generate mood-specific visual description in Chinese."""
    parts = []

    mood_visuals = {
        "happy": "温暖笑容",
        "sad": "雨滴窗外",
        "angry": "闪电裂痕",
        "calm": "静水微澜",
        "energetic": "火花四射",
        "melancholic": "秋叶飘零",
        "romantic": "花瓣飞舞",
        "dark": "暗影重重",
        "dreamy": "星光闪烁",
        "peaceful": "白云轻飘",
        "epic": "群山巍峨",
        "nostalgic": "老照片",
        "uplifting": "朝阳初升",
    }
    parts.append(mood_visuals.get(emotion, "抽象意象"))

    if energy > 0.7:
        parts.append("高能量画面")
    elif energy < 0.3:
        parts.append("柔和画面")

    return "，".join(parts)


def _mood_visual_en(emotion: str, genre: str, section: str, energy: float) -> str:
    """Generate mood-specific visual description in English."""
    parts = []

    mood_visuals = {
        "happy": "warm smiles",
        "sad": "raindrops on window",
        "angry": "lightning cracks",
        "calm": "still water ripples",
        "energetic": "sparks flying",
        "melancholic": "autumn leaves falling",
        "romantic": "flower petals drifting",
        "dark": "deep shadows",
        "dreamy": "starlight shimmer",
        "peaceful": "white clouds drifting",
        "epic": "majestic mountains",
        "nostalgic": "old photographs",
        "uplifting": "sunrise breaking through",
    }
    parts.append(mood_visuals.get(emotion, "abstract imagery"))

    if energy > 0.7:
        parts.append("high energy visuals")
    elif energy < 0.3:
        parts.append("soft gentle visuals")

    return ", ".join(parts)
