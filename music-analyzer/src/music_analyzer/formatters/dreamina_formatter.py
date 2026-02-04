"""Dreamina prompt formatter: maps music analysis to visual generation prompts.

Mapping logic:
- emotion.primary_emotion → style keywords
- emotion.overall_energy → composition intensity
- rhythm.bpm → rhythm description
- tonality.key/mode → brightness/darkness base
- rhythm.sections[] → per-section prompts
- emotion.genre → visual style
"""

from __future__ import annotations

from music_analyzer.models import (
    DreaminaOutput,
    DreaminaSectionPrompt,
    MusicAnalysisResult,
)

# ---------------------------------------------------------------------------
# Mapping tables
# ---------------------------------------------------------------------------

EMOTION_TO_STYLE_ZH = {
    "happy": "明亮暖色调，充满活力，欢快氛围",
    "sad": "冷色调，柔和阴影，忧郁意境",
    "angry": "高对比度，深红与黑色，强烈冲击感",
    "calm": "柔和色调，宁静氛围，自然光线",
    "energetic": "鲜艳色彩，动感光效，充满力量",
    "melancholic": "灰蓝色调，朦胧光影，怀旧氛围",
    "romantic": "粉色与金色，柔焦效果，浪漫光晕",
    "dark": "深色调，暗影，神秘光线",
    "dreamy": "梦幻柔光，紫色与蓝色渐变，朦胧",
    "aggressive": "锐利线条，闪电效果，强烈对比",
    "peaceful": "白色与淡蓝，开阔空间，晨光",
    "epic": "宏大场景，黄金比例构图，壮丽光线",
    "nostalgic": "暖黄色调，胶片质感，复古风格",
    "playful": "糖果色彩，几何图案，活泼构图",
    "mysterious": "深蓝与紫色，雾气效果，暗角",
    "uplifting": "阳光金色，向上运动感，温暖明亮",
}

EMOTION_TO_STYLE_EN = {
    "happy": "bright warm tones, vibrant, joyful atmosphere",
    "sad": "cool tones, soft shadows, melancholic mood",
    "angry": "high contrast, deep red and black, intense impact",
    "calm": "soft tones, serene atmosphere, natural lighting",
    "energetic": "vivid colors, dynamic lighting, powerful energy",
    "melancholic": "grey-blue tones, hazy light, nostalgic atmosphere",
    "romantic": "pink and gold, soft focus, romantic halo",
    "dark": "dark tones, deep shadows, mysterious lighting",
    "dreamy": "dreamy soft light, purple and blue gradient, ethereal",
    "aggressive": "sharp lines, lightning effects, strong contrast",
    "peaceful": "white and light blue, open space, morning light",
    "epic": "grand scene, golden ratio composition, magnificent lighting",
    "nostalgic": "warm yellow tones, film grain texture, vintage style",
    "playful": "candy colors, geometric patterns, lively composition",
    "mysterious": "deep blue and purple, fog effects, dark vignette",
    "uplifting": "golden sunlight, upward motion, warm and bright",
}

ENERGY_TO_COMPOSITION_ZH = {
    "high": "动态构图，强对比，爆发力",
    "mid": "均衡构图，节奏感，流动线条",
    "low": "宁静构图，开阔空间，简洁",
}

ENERGY_TO_COMPOSITION_EN = {
    "high": "dynamic composition, strong contrast, explosive energy",
    "mid": "balanced composition, rhythmic flow, flowing lines",
    "low": "serene composition, open space, minimal",
}

BPM_TO_RHYTHM_ZH = {
    "fast": "激烈节奏，闪烁光效，快速运动",
    "mid": "律动节奏，规律运动，有序变化",
    "slow": "舒缓节奏，缓慢流动，静谧",
}

BPM_TO_RHYTHM_EN = {
    "fast": "intense rhythm, flickering lights, rapid motion",
    "mid": "groovy rhythm, regular motion, ordered changes",
    "slow": "soothing rhythm, slow flow, tranquil",
}

MODE_TO_TONE_ZH = {
    "major": "明亮基调，开放感，向上",
    "minor": "戏剧性暗调，深邃，内省",
}

MODE_TO_TONE_EN = {
    "major": "bright base tone, openness, upward feeling",
    "minor": "dramatic dark tone, depth, introspective",
}

GENRE_TO_VISUAL_ZH = {
    "electronic": "赛博朋克，几何图形，霓虹灯光",
    "jazz": "烟雾缭绕，温暖灯光，复古酒吧",
    "classical": "宏伟建筑，对称构图，古典美学",
    "rock": "舞台灯光，电吉他火花，摇滚能量",
    "hip-hop": "街头涂鸦，城市夜景，潮流文化",
    "pop": "时尚舞台，明亮色彩，流行元素",
    "ambient": "自然景观，极简主义，空灵氛围",
    "metal": "暗黑美学，火焰效果，金属质感",
    "folk": "田园风光，木质纹理，温馨氛围",
    "r&b": "柔和灯光，丝绒质感，亲密氛围",
    "country": "乡村风景，日落余晖，质朴",
    "latin": "热带色彩，热情舞蹈，阳光",
    "blues": "昏暗酒吧，蓝色灯光，忧郁",
    "reggae": "牙买加色彩，热带风情，悠闲",
    "funk": "迪斯科灯球，复古时尚，律动",
    "soul": "柔和金光，情感深邃，温暖",
}

GENRE_TO_VISUAL_EN = {
    "electronic": "cyberpunk, geometric shapes, neon lights",
    "jazz": "smoky atmosphere, warm lighting, vintage bar",
    "classical": "grand architecture, symmetric composition, classical aesthetics",
    "rock": "stage lights, guitar sparks, rock energy",
    "hip-hop": "street graffiti, city nightscape, urban culture",
    "pop": "fashion stage, bright colors, pop elements",
    "ambient": "natural landscape, minimalism, ethereal atmosphere",
    "metal": "dark aesthetics, flame effects, metallic texture",
    "folk": "pastoral scenery, wood textures, cozy atmosphere",
    "r&b": "soft lighting, velvet textures, intimate atmosphere",
    "country": "rural landscape, sunset glow, rustic",
    "latin": "tropical colors, passionate dance, sunshine",
    "blues": "dim bar, blue lights, melancholy",
    "reggae": "Jamaican colors, tropical vibes, relaxed",
    "funk": "disco ball, retro fashion, groove",
    "soul": "soft golden light, deep emotion, warmth",
}

# Section-level visual intensity
SECTION_INTENSITY = {
    "intro": 0.3,
    "verse": 0.5,
    "chorus": 0.9,
    "bridge": 0.6,
    "outro": 0.3,
}


def format_dreamina(result: MusicAnalysisResult) -> DreaminaOutput:
    """Convert full analysis result to Dreamina prompts per section."""
    emotion = result.emotion
    rhythm = result.rhythm
    tonality = result.tonality

    # Defaults
    primary_emotion = emotion.primary_emotion if emotion else "calm"
    overall_energy = emotion.overall_energy if emotion else 0.5
    genre = emotion.genre if emotion else "unknown"
    bpm = rhythm.bpm if rhythm else 120
    mode = tonality.mode if tonality else "major"
    sections = rhythm.sections if rhythm else []

    # Global style
    genre_style_zh = GENRE_TO_VISUAL_ZH.get(genre, "")
    genre_style_en = GENRE_TO_VISUAL_EN.get(genre, "")

    global_keywords = [primary_emotion, genre]
    if emotion:
        global_keywords.extend(emotion.mood_tags[:3])

    # Per-section prompts
    section_prompts = []
    if not sections:
        # No sections detected — generate single prompt
        prompt = _build_section_prompt(
            section_label="full",
            start=0.0,
            end=result.duration,
            primary_emotion=primary_emotion,
            overall_energy=overall_energy,
            bpm=bpm,
            mode=mode,
            genre=genre,
        )
        section_prompts.append(prompt)
    else:
        for i, sec in enumerate(sections):
            prompt = _build_section_prompt(
                section_label=f"{sec.label}_{i + 1}",
                start=sec.start,
                end=sec.end,
                primary_emotion=primary_emotion,
                overall_energy=overall_energy,
                bpm=bpm,
                mode=mode,
                genre=genre,
            )
            section_prompts.append(prompt)

    return DreaminaOutput(
        song_title=result.file_name,
        total_duration=result.duration,
        sections=section_prompts,
        global_style=f"{genre_style_zh} / {genre_style_en}" if genre_style_zh else "",
        global_keywords=global_keywords,
    )


def _build_section_prompt(
    section_label: str,
    start: float,
    end: float,
    primary_emotion: str,
    overall_energy: float,
    bpm: float,
    mode: str,
    genre: str,
) -> DreaminaSectionPrompt:
    """Build a Dreamina prompt for one section."""
    # Determine section base type for intensity
    base_label = section_label.split("_")[0].lower()
    section_intensity = SECTION_INTENSITY.get(base_label, 0.5)
    effective_energy = (overall_energy * 0.6 + section_intensity * 0.4)

    # Energy level
    if effective_energy > 0.65:
        energy_key = "high"
    elif effective_energy < 0.35:
        energy_key = "low"
    else:
        energy_key = "mid"

    # BPM category
    if bpm > 140:
        bpm_key = "fast"
    elif bpm < 100:
        bpm_key = "slow"
    else:
        bpm_key = "mid"

    # Assemble Chinese prompt
    parts_zh = [
        EMOTION_TO_STYLE_ZH.get(primary_emotion, ""),
        ENERGY_TO_COMPOSITION_ZH.get(energy_key, ""),
        BPM_TO_RHYTHM_ZH.get(bpm_key, ""),
        MODE_TO_TONE_ZH.get(mode, ""),
        GENRE_TO_VISUAL_ZH.get(genre, ""),
    ]
    prompt_zh = "，".join(p for p in parts_zh if p)

    # Assemble English prompt
    parts_en = [
        EMOTION_TO_STYLE_EN.get(primary_emotion, ""),
        ENERGY_TO_COMPOSITION_EN.get(energy_key, ""),
        BPM_TO_RHYTHM_EN.get(bpm_key, ""),
        MODE_TO_TONE_EN.get(mode, ""),
        GENRE_TO_VISUAL_EN.get(genre, ""),
    ]
    prompt_en = ", ".join(p for p in parts_en if p)

    # Style keywords
    keywords = [primary_emotion]
    if genre != "unknown":
        keywords.append(genre)
    keywords.append(energy_key + "_energy")

    # Color palette from emotion
    palette = _emotion_to_colors(primary_emotion, effective_energy)

    return DreaminaSectionPrompt(
        section=section_label,
        time_range={"start": round(start, 2), "end": round(end, 2)},
        prompt_zh=prompt_zh,
        prompt_en=prompt_en,
        style_keywords=keywords,
        color_palette=palette,
        energy_level=round(effective_energy, 2),
    )


def _emotion_to_colors(emotion: str, energy: float) -> list[str]:
    """Map emotion + energy to a simple color palette."""
    palettes = {
        "happy": ["#FFD700", "#FF6B35", "#FFA07A", "#FFEC8B"],
        "sad": ["#4682B4", "#708090", "#5F9EA0", "#87CEEB"],
        "angry": ["#DC143C", "#8B0000", "#FF4500", "#B22222"],
        "calm": ["#98D8C8", "#B8E6B8", "#E6F2E6", "#87CEEB"],
        "energetic": ["#FF1493", "#FF6347", "#FFD700", "#00FF7F"],
        "melancholic": ["#6A5ACD", "#483D8B", "#708090", "#778899"],
        "romantic": ["#FF69B4", "#FFB6C1", "#FFD700", "#DDA0DD"],
        "dark": ["#2F2F2F", "#4A0E4E", "#191970", "#2C003E"],
        "dreamy": ["#9B59B6", "#8E44AD", "#D4A5FF", "#C39BD3"],
        "aggressive": ["#FF0000", "#000000", "#FF4500", "#8B0000"],
        "peaceful": ["#E0F0FF", "#B0D4F1", "#FFFFFF", "#D4E6F1"],
        "epic": ["#FFD700", "#DAA520", "#B8860B", "#CD853F"],
        "nostalgic": ["#DEB887", "#D2B48C", "#CD853F", "#F5DEB3"],
        "playful": ["#FF69B4", "#00CED1", "#FFD700", "#7CFC00"],
        "mysterious": ["#191970", "#4B0082", "#2C003E", "#301934"],
        "uplifting": ["#FFD700", "#FFA500", "#FF8C00", "#FFFACD"],
    }
    return palettes.get(emotion, ["#808080", "#A9A9A9", "#C0C0C0", "#D3D3D3"])
