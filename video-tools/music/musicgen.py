#!/usr/bin/env python3
"""Meta MusicGen - Local AI music generation using audiocraft."""

import argparse
import sys


def generate(prompt: str, duration: int, output: str) -> None:
    try:
        from audiocraft.models import MusicGen
        from audiocraft.data.audio import audio_write
    except ImportError:
        print(
            "Error: audiocraft is not installed. Install with: pip install audiocraft\n"
            "Note: MusicGen requires a GPU with sufficient VRAM.",
            file=sys.stderr,
        )
        sys.exit(1)

    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("Warning: running on CPU, this will be very slow.", file=sys.stderr)

    print(f"Loading MusicGen model on {device}...")
    model = MusicGen.get_pretrained("facebook/musicgen-small", device=device)
    model.set_generation_params(duration=duration)

    print(f"Generating music: '{prompt}' ({duration}s)...")
    wav = model.generate([prompt])

    # audio_write expects path without extension
    out_path = output.rsplit(".", 1)[0] if "." in output else output
    audio_write(out_path, wav[0].cpu(), model.sample_rate, strategy="loudness")
    print(f"Saved to {out_path}.wav")


def main() -> None:
    parser = argparse.ArgumentParser(description="MusicGen Local Music Generation")
    parser.add_argument("--prompt", required=True, help="Music description prompt")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds (default: 30)")
    parser.add_argument("--output", required=True, help="Output audio file path")
    args = parser.parse_args()

    generate(args.prompt, args.duration, args.output)


if __name__ == "__main__":
    main()
