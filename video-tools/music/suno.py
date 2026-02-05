#!/usr/bin/env python3
"""Suno API - AI music generation via Suno."""

import argparse
import sys
import os
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUNO_KEY

BASE_URL = "https://studio-api.suno.ai/api"
# Alternative: use third-party Suno API wrapper
ALT_URL = "https://api.sunoaiapi.com/api/v1"


def generate(prompt: str, duration: int, output: str) -> None:
    key = SUNO_KEY()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    # Create generation task
    payload = {
        "gpt_description_prompt": prompt,
        "make_instrumental": True,
        "mv": "chirp-v3-5",
    }

    resp = requests.post(f"{ALT_URL}/gateway/generate/gpt_desc", json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"Error: Suno API returned {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    if "data" not in data:
        print(f"Error: unexpected response: {data}", file=sys.stderr)
        sys.exit(1)

    task_ids = [item["song_id"] for item in data["data"]]
    print(f"Generation started, task IDs: {task_ids}")

    # Poll for completion
    for _ in range(60):
        time.sleep(10)
        resp = requests.get(
            f"{ALT_URL}/gateway/query",
            params={"ids": ",".join(task_ids)},
            headers=headers,
            timeout=30,
        )
        if resp.status_code != 200:
            continue
        items = resp.json().get("data", [])
        for item in items:
            if item.get("status") == "complete" and item.get("audio_url"):
                audio_url = item["audio_url"]
                print(f"Downloading from {audio_url}")
                audio_resp = requests.get(audio_url, timeout=120)
                with open(output, "wb") as f:
                    f.write(audio_resp.content)
                print(f"Saved to {output} ({len(audio_resp.content)} bytes)")
                return
        print("  Waiting for generation...")

    print("Error: generation timed out.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Suno AI Music Generation")
    parser.add_argument("--prompt", required=True, help="Music style description")
    parser.add_argument("--duration", type=int, default=30, help="Target duration in seconds (default: 30)")
    parser.add_argument("--output", required=True, help="Output audio file path")
    args = parser.parse_args()

    generate(args.prompt, args.duration, args.output)


if __name__ == "__main__":
    main()
