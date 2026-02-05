#!/usr/bin/env python3
"""Fish Audio TTS - Text to speech using Fish Audio API."""

import argparse
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FISH_AUDIO_KEY

API_URL = "https://api.fish.audio/v1/tts"


def synthesize(text: str, voice: str, output: str, speed: float = 1.0) -> None:
    key = FISH_AUDIO_KEY()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "reference_id": voice,
        "format": "mp3",
        "speed": speed,
    }

    resp = requests.post(API_URL, json=payload, headers=headers, timeout=120)
    if resp.status_code != 200:
        print(f"Error: Fish Audio API returned {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    with open(output, "wb") as f:
        f.write(resp.content)
    print(f"Saved to {output} ({len(resp.content)} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fish Audio TTS")
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--file", help="Read text from file")
    parser.add_argument("--voice", required=True, help="Voice reference ID")
    parser.add_argument("--output", required=True, help="Output audio file path")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
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
