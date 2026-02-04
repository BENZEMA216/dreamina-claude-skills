"""Generic JSON formatter for analysis results."""

from __future__ import annotations

import json
from typing import Any

from music_analyzer.models import MusicAnalysisResult


def format_json(result: MusicAnalysisResult, indent: int = 2) -> str:
    """Format analysis result as pretty JSON."""
    return result.model_dump_json(indent=indent, exclude_none=True)


def format_section_json(result: MusicAnalysisResult, section: str) -> str:
    """Format a specific analysis section as JSON.

    Parameters
    ----------
    section : one of 'rhythm', 'emotion', 'timbre', 'tonality', 'lyrics', 'onsets', 'color_palette'
    """
    data = getattr(result, section, None)
    if data is None:
        return json.dumps({"error": f"Section '{section}' not available"}, indent=2)
    return data.model_dump_json(indent=2, exclude_none=True)


def load_analysis_json(path: str) -> MusicAnalysisResult:
    """Load a previously saved analysis JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return MusicAnalysisResult(**data)
