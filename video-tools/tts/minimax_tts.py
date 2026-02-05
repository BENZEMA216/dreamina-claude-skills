#!/usr/bin/env python3
"""MiniMax TTS - Text to speech using MiniMax API."""

import argparse
import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MINIMAX_KEY, MINIMAX_GROUP_ID

API_URL = "https://api.minimax.chat/v1/t2a_v2"

VOICES = {
    "male-qn-qingse": "青涩青年音色",
    "male-qn-jingying": "精英青年音色",
    "male-qn-badao": "霸道青年音色",
    "male-qn-daxuesheng": "青年大学生音色",
    "female-shaonv": "少女音色",
    "female-yujie": "御姐音色",
    "female-chengshu": "成熟女性音色",
    "female-tianmei": "甜美女性音色",
    "presenter_male": "男性主持人",
    "presenter_female": "女性主持人",
    "audiobook_male_1": "男性有声书1",
    "audiobook_male_2": "男性有声书2",
    "audiobook_female_1": "女性有声书1",
    "audiobook_female_2": "女性有声书2",
}


def synthesize(text: str, voice: str, output: str, speed: float = 1.0) -> None:
    key = MINIMAX_KEY()
    group_id = MINIMAX_GROUP_ID()

    url = f"{API_URL}?GroupId={group_id}" if group_id else API_URL
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "speech-01-turbo",
        "text": text,
        "timber_weights": [{"voice_id": voice, "weight": 1}],
        "audio_setting": {
            "format": "mp3",
            "sample_rate": 32000,
            "speed": speed,
        },
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    if resp.status_code != 200:
        print(f"Error: MiniMax API returned {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    if "data" not in data or "audio" not in data["data"]:
        print(f"Error: unexpected response: {data}", file=sys.stderr)
        sys.exit(1)

    import base64
    audio_bytes = base64.b64decode(data["data"]["audio"])
    with open(output, "wb") as f:
        f.write(audio_bytes)
    print(f"Saved to {output} ({len(audio_bytes)} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MiniMax TTS",
        epilog="Available voices: " + ", ".join(VOICES.keys()),
    )
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--file", help="Read text from file")
    parser.add_argument("--voice", default="female-shaonv", help="Voice ID (default: female-shaonv)")
    parser.add_argument("--output", required=True, help="Output audio file path")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    args = parser.parse_args()

    if args.list_voices:
        for vid, desc in VOICES.items():
            print(f"  {vid:30s} {desc}")
        return

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
