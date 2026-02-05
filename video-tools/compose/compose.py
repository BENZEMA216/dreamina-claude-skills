#!/usr/bin/env python3
"""Video composition - merge video, voiceover, and BGM using FFmpeg or MoviePy."""

from __future__ import annotations

import argparse
import subprocess
import shutil
import sys
from typing import Optional


def compose_ffmpeg(video, voice, bgm, bgm_volume, output):
    # type: (str, Optional[str], Optional[str], float, str) -> None
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg not found in PATH.", file=sys.stderr)
        sys.exit(1)

    inputs = ["-i", video]
    filter_parts = []
    audio_streams = []
    input_idx = 1

    if voice:
        inputs.extend(["-i", voice])
        audio_streams.append(f"[{input_idx}:a]")
        input_idx += 1

    if bgm:
        inputs.extend(["-i", bgm])
        filter_parts.append(f"[{input_idx}:a]volume={bgm_volume}[bgm_adj]")
        audio_streams.append("[bgm_adj]")
        input_idx += 1

    cmd = ["ffmpeg", "-y"] + inputs

    if not voice and not bgm:
        # No audio changes, just copy
        cmd.extend(["-c", "copy", output])
    elif len(audio_streams) == 1 and not bgm:
        # Voice only, no filter needed
        cmd.extend([
            "-filter_complex", f"[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            output,
        ])
    else:
        # Build complex filter
        all_filter = []
        mix_inputs = ["[0:a]"]  # original audio

        if voice and bgm:
            all_filter.append(f"[{input_idx - 1}:a]volume={bgm_volume}[bgm_adj]")
            mix_inputs.append(f"[{input_idx - 2}:a]")  # voice
            mix_inputs.append("[bgm_adj]")  # bgm adjusted
        elif voice:
            mix_inputs.append(f"[1:a]")
        elif bgm:
            all_filter.append(f"[1:a]volume={bgm_volume}[bgm_adj]")
            mix_inputs.append("[bgm_adj]")

        n = len(mix_inputs)
        mix_str = "".join(mix_inputs)
        all_filter.append(f"{mix_str}amix=inputs={n}:duration=first:dropout_transition=2[aout]")

        filter_complex = ";".join(all_filter)
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            output,
        ])

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"Saved to {output}")


def compose_moviepy(video, voice, bgm, bgm_volume, output):
    # type: (str, Optional[str], Optional[str], float, str) -> None
    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
    except ImportError:
        print("Error: moviepy is not installed. Install with: pip install moviepy", file=sys.stderr)
        sys.exit(1)

    clip = VideoFileClip(video)
    audio_clips = []

    if clip.audio:
        audio_clips.append(clip.audio)

    if voice:
        voice_clip = AudioFileClip(voice)
        audio_clips.append(voice_clip)

    if bgm:
        bgm_clip = AudioFileClip(bgm).volumex(bgm_volume)
        # Loop BGM if shorter than video
        if bgm_clip.duration < clip.duration:
            from moviepy.editor import afx
            bgm_clip = afx.audio_loop(bgm_clip, duration=clip.duration)
        else:
            bgm_clip = bgm_clip.subclip(0, clip.duration)
        audio_clips.append(bgm_clip)

    if audio_clips:
        final_audio = CompositeAudioClip(audio_clips)
        clip = clip.set_audio(final_audio)

    clip.write_videofile(output, codec="libx264", audio_codec="aac")
    print(f"Saved to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Video Composition - merge video, voice, and BGM")
    parser.add_argument("--video", required=True, help="Input video file")
    parser.add_argument("--voice", help="Voiceover audio file (optional)")
    parser.add_argument("--bgm", help="Background music file (optional)")
    parser.add_argument("--bgm-volume", type=float, default=0.2, help="BGM volume ratio (default: 0.2)")
    parser.add_argument("--output", required=True, help="Output video file path")
    parser.add_argument("--engine", choices=["ffmpeg", "moviepy"], default="ffmpeg", help="Composition engine (default: ffmpeg)")
    args = parser.parse_args()

    if args.engine == "ffmpeg":
        compose_ffmpeg(args.video, args.voice, args.bgm, args.bgm_volume, args.output)
    else:
        compose_moviepy(args.video, args.voice, args.bgm, args.bgm_volume, args.output)


if __name__ == "__main__":
    main()
