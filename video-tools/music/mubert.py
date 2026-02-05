#!/usr/bin/env python3
"""Mubert API - AI music generation via Mubert."""

import argparse
import sys
import os
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MUBERT_KEY

API_URL = "https://api-b2b.mubert.com/v2"


def generate(prompt: str, duration: int, output: str) -> None:
    key = MUBERT_KEY()

    # Request track generation
    payload = {
        "method": "RecordTrackTTM",
        "params": {
            "pat": key,
            "prompt": prompt,
            "duration": duration,
            "format": "file",
        },
    }

    resp = requests.post(f"{API_URL}/TTM", json=payload, timeout=30)
    if resp.status_code != 200:
        print(f"Error: Mubert API returned {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    if data.get("status") != 1:
        print(f"Error: {data}", file=sys.stderr)
        sys.exit(1)

    task_id = data["data"]["tasks"][0]["task_id"]
    print(f"Generation started, task ID: {task_id}")

    # Poll for completion
    for _ in range(60):
        time.sleep(5)
        poll_payload = {
            "method": "TrackStatus",
            "params": {
                "pat": key,
                "task_id": task_id,
            },
        }
        resp = requests.post(f"{API_URL}/TrackStatus", json=poll_payload, timeout=30)
        if resp.status_code != 200:
            continue

        result = resp.json()
        if result.get("status") == 1:
            task = result["data"]["tasks"][0]
            if task.get("download_link"):
                download_url = task["download_link"]
                print(f"Downloading from {download_url}")
                audio_resp = requests.get(download_url, timeout=120)
                with open(output, "wb") as f:
                    f.write(audio_resp.content)
                print(f"Saved to {output} ({len(audio_resp.content)} bytes)")
                return
        print("  Waiting for generation...")

    print("Error: generation timed out.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mubert AI Music Generation")
    parser.add_argument("--prompt", required=True, help="Music style description")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds (default: 30)")
    parser.add_argument("--output", required=True, help="Output audio file path")
    args = parser.parse_args()

    generate(args.prompt, args.duration, args.output)


if __name__ == "__main__":
    main()
