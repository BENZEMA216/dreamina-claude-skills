#!/usr/bin/env python3
"""OpenAI TTS - Text to speech using OpenAI API."""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY

VOICES = ["alloy", "ash", "ballad", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]


def synthesize(text: str, voice: str, output: str, speed: float = 1.0) -> None:
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai is not installed. Install with: pip install openai", file=sys.stderr)
        sys.exit(1)

    key = OPENAI_API_KEY()
    client = OpenAI(api_key=key)

    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        speed=speed,
        response_format="mp3",
    )

    response.stream_to_file(output)
    print(f"Saved to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAI TTS")
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--file", help="Read text from file")
    parser.add_argument("--voice", default="alloy", choices=VOICES, help="Voice name (default: alloy)")
    parser.add_argument("--output", required=True, help="Output audio file path")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (0.25-4.0, default: 1.0)")
    args = parser.parse_args()

    text = args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    if not text:
        print("Error: --text or --file is required.", file=sys.stderr)
        sys.exit(1)

    synthesize(text, args.voice, args.output, args.speed)


if __name__ == "__main__":
    main()
