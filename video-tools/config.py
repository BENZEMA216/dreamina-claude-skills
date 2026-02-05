"""Unified configuration for video-tools. All API keys are read from environment variables."""

from __future__ import annotations

import os
import sys
from typing import Optional


def get_key(name: str, required: bool = True) -> Optional[str]:
    value = os.environ.get(name)
    if required and not value:
        print(f"Error: environment variable {name} is not set.", file=sys.stderr)
        sys.exit(1)
    return value


# TTS
FISH_AUDIO_KEY = lambda: get_key("FISH_AUDIO_KEY")
AZURE_SPEECH_KEY = lambda: get_key("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = lambda: get_key("AZURE_SPEECH_REGION", required=False) or "eastasia"
OPENAI_API_KEY = lambda: get_key("OPENAI_API_KEY")
MINIMAX_KEY = lambda: get_key("MINIMAX_KEY")
MINIMAX_GROUP_ID = lambda: get_key("MINIMAX_GROUP_ID", required=False) or ""

# Music
SUNO_KEY = lambda: get_key("SUNO_KEY")
MUBERT_KEY = lambda: get_key("MUBERT_KEY")
