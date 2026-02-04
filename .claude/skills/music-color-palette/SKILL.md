---
name: music-color-palette
description: Generate color palette from music mood and tonality
user_invocable: true
---

# /music-color-palette — Music → Color Palette

Generate a color palette based on the emotional mood and tonality of a music track. Outputs primary, secondary, accent, background, and text colors with hex codes.

## Usage

```
/music-color-palette <audio_file_or_analysis_json>
```

Accepts either an audio file (runs analysis first) or a previously saved analysis JSON.

## Steps

1. Validate input (audio file or JSON)
2. Generate color palette:

```bash
python3 -m music_analyzer color-palette "<input_path>"
```

3. Present the palette:
   - **Primary color** — dominant visual color
   - **Secondary color** — supporting color
   - **Accent color** — highlight/emphasis
   - **Background** — suggested background
   - **Text** — readable text color
   - **Full palette** — extended hex code list
   - **Mood association** — what the palette represents

## Mapping Logic

The palette is derived from:
- **Primary emotion** (happy, sad, calm, energetic, etc.)
- **Key mode** (major → brighter, minor → deeper)

Each (emotion, mode) combination maps to a curated palette.

## Output Format

```json
{
  "primary": "#FFD700",
  "secondary": "#FF6B35",
  "accent": "#FF1493",
  "background": "#FFFAF0",
  "text": "#2F2F2F",
  "palette": ["#FFD700", "#FF6B35", "#FFA07A", "#FFEC8B", "#FF1493"],
  "mood_association": "joyful warmth"
}
```

## Use Cases

- Pair with `/music-to-dreamina` for consistent visual styling
- Use as design system base colors for music-themed projects
- Feed into Dreamina or other visual generation tools
