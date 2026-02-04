"""CLI entry point for music_analyzer.

Usage:
    python3 -m music_analyzer analyze <audio_file> [--output <path>] [--no-cache] [--no-separation]
    python3 -m music_analyzer rhythm <audio_file>
    python3 -m music_analyzer emotion <audio_file>
    python3 -m music_analyzer timbre <audio_file> [--no-separation]
    python3 -m music_analyzer tonality <audio_file>
    python3 -m music_analyzer lyrics <audio_file> [--model-size <size>]
    python3 -m music_analyzer dreamina <audio_file_or_json> [--output <path>]
    python3 -m music_analyzer storyboard <audio_file_or_json> [--output <path>]
    python3 -m music_analyzer color-palette <audio_file_or_json>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from music_analyzer.config import DEFAULT_SR, SUPPORTED_FORMATS, dependency_tier


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="music-analyzer",
        description="Analyze audio files and generate creative format outputs",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- analyze ---
    p_analyze = sub.add_parser("analyze", help="Full analysis of an audio file")
    p_analyze.add_argument("audio", help="Path to audio file")
    p_analyze.add_argument("--output", "-o", help="Output JSON path (default: stdout)")
    p_analyze.add_argument("--no-cache", action="store_true", help="Bypass cache")
    p_analyze.add_argument("--no-separation", action="store_true", help="Skip source separation")

    # --- individual analyzers ---
    for cmd in ("rhythm", "emotion", "timbre", "tonality", "lyrics"):
        p = sub.add_parser(cmd, help=f"Run {cmd} analysis only")
        p.add_argument("audio", help="Path to audio file")
        if cmd == "timbre":
            p.add_argument("--no-separation", action="store_true")
        if cmd == "lyrics":
            p.add_argument("--model-size", default="base", help="Whisper model size")

    # --- formatters ---
    for cmd in ("dreamina", "storyboard", "color-palette"):
        p = sub.add_parser(cmd, help=f"Generate {cmd} output")
        p.add_argument("input", help="Audio file or analysis JSON path")
        p.add_argument("--output", "-o", help="Output path (default: stdout)")

    # --- visualize ---
    p_vis = sub.add_parser("visualize", help="Generate HTML visualization report")
    p_vis.add_argument("input", help="Audio file or analysis JSON path")
    p_vis.add_argument("--output", "-o", help="Output HTML path (default: <name>_report.html)")
    p_vis.add_argument("--open", action="store_true", help="Open in browser after generation")

    args = parser.parse_args()

    try:
        _dispatch(args)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _dispatch(args: argparse.Namespace) -> None:
    """Route to the appropriate handler."""
    cmd = args.command

    if cmd == "analyze":
        _cmd_analyze(args)
    elif cmd in ("rhythm", "emotion", "timbre", "tonality", "lyrics"):
        _cmd_single(args)
    elif cmd in ("dreamina", "storyboard", "color-palette"):
        _cmd_format(args)
    elif cmd == "visualize":
        _cmd_visualize(args)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


def _cmd_analyze(args: argparse.Namespace) -> None:
    """Full analysis pipeline."""
    from music_analyzer.utils.audio_io import validate_audio_path, load_audio, get_audio_info
    from music_analyzer.utils.cache import get_cached, save_cache
    from music_analyzer.analyzers.rhythm import analyze_rhythm
    from music_analyzer.analyzers.tonality import analyze_tonality
    from music_analyzer.analyzers.onset import analyze_onsets
    from music_analyzer.analyzers.timbre import analyze_timbre
    from music_analyzer.analyzers.emotion import analyze_emotion
    from music_analyzer.analyzers.lyrics import analyze_lyrics
    from music_analyzer.formatters.color_palette import generate_color_palette
    from music_analyzer.models import MusicAnalysisResult

    audio_path = validate_audio_path(args.audio)

    # Check cache
    if not args.no_cache:
        cached = get_cached(audio_path, "analysis")
        if cached:
            _output_json(cached, getattr(args, "output", None))
            return

    # Load audio
    info = get_audio_info(audio_path)
    y, sr = load_audio(audio_path)

    tier = dependency_tier()
    print(f"Analyzing {audio_path.name} (tier: {tier})...", file=sys.stderr)

    # Run analyzers
    rhythm = analyze_rhythm(y, sr)
    tonality = analyze_tonality(y, sr)
    onsets = analyze_onsets(y, sr)
    timbre = analyze_timbre(
        y, sr,
        audio_path=audio_path,
        run_separation=not args.no_separation,
    )
    emotion = analyze_emotion(
        y, sr,
        key_mode=tonality.mode,
        bpm=rhythm.bpm,
    )
    lyrics = analyze_lyrics(y, sr, audio_path=audio_path)

    # Assemble result
    result = MusicAnalysisResult(
        file_path=str(audio_path),
        file_name=audio_path.name,
        duration=rhythm.duration,
        sample_rate=sr,
        dependency_tier=tier,
        rhythm=rhythm,
        emotion=emotion,
        timbre=timbre,
        tonality=tonality,
        lyrics=lyrics,
        onsets=onsets,
    )

    # Generate color palette from results
    result.color_palette = generate_color_palette(result)

    # Output
    data = json.loads(result.model_dump_json(exclude_none=True))

    if not args.no_cache:
        save_cache(audio_path, data, "analysis")

    _output_json(data, getattr(args, "output", None))


def _cmd_single(args: argparse.Namespace) -> None:
    """Single analyzer command."""
    from music_analyzer.utils.audio_io import validate_audio_path, load_audio

    audio_path = validate_audio_path(args.audio)
    y, sr = load_audio(audio_path)
    cmd = args.command

    if cmd == "rhythm":
        from music_analyzer.analyzers.rhythm import analyze_rhythm
        result = analyze_rhythm(y, sr)
    elif cmd == "tonality":
        from music_analyzer.analyzers.tonality import analyze_tonality
        result = analyze_tonality(y, sr)
    elif cmd == "timbre":
        from music_analyzer.analyzers.timbre import analyze_timbre
        result = analyze_timbre(
            y, sr,
            audio_path=audio_path,
            run_separation=not getattr(args, "no_separation", False),
        )
    elif cmd == "emotion":
        from music_analyzer.analyzers.emotion import analyze_emotion
        # For standalone emotion, first detect key for better heuristic
        from music_analyzer.analyzers.tonality import analyze_tonality
        from music_analyzer.analyzers.rhythm import analyze_rhythm
        tonality = analyze_tonality(y, sr)
        rhythm = analyze_rhythm(y, sr)
        result = analyze_emotion(y, sr, key_mode=tonality.mode, bpm=rhythm.bpm)
    elif cmd == "lyrics":
        from music_analyzer.analyzers.lyrics import analyze_lyrics
        result = analyze_lyrics(
            y, sr,
            audio_path=audio_path,
            model_size=getattr(args, "model_size", "base"),
        )
    else:
        print(f"Unknown analyzer: {cmd}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.model_dump_json(exclude_none=True))
    _output_json(data)


def _cmd_format(args: argparse.Namespace) -> None:
    """Formatter command — accepts audio file or analysis JSON."""
    input_path = Path(args.input).expanduser().resolve()

    if input_path.suffix.lower() == ".json":
        # Load pre-existing analysis
        from music_analyzer.formatters.json_formatter import load_analysis_json
        analysis = load_analysis_json(str(input_path))
    elif input_path.suffix.lower() in SUPPORTED_FORMATS:
        # Run full analysis first
        from music_analyzer.utils.audio_io import validate_audio_path, load_audio, get_audio_info
        from music_analyzer.utils.cache import get_cached
        from music_analyzer.models import MusicAnalysisResult

        audio_path = validate_audio_path(str(input_path))

        # Try cache
        cached = get_cached(audio_path, "analysis")
        if cached:
            analysis = MusicAnalysisResult(**cached)
        else:
            # Run analysis
            from music_analyzer.analyzers.rhythm import analyze_rhythm
            from music_analyzer.analyzers.tonality import analyze_tonality
            from music_analyzer.analyzers.onset import analyze_onsets
            from music_analyzer.analyzers.timbre import analyze_timbre
            from music_analyzer.analyzers.emotion import analyze_emotion
            from music_analyzer.analyzers.lyrics import analyze_lyrics
            from music_analyzer.formatters.color_palette import generate_color_palette

            y, sr = load_audio(audio_path)
            rhythm = analyze_rhythm(y, sr)
            tonality = analyze_tonality(y, sr)
            onsets = analyze_onsets(y, sr)
            timbre = analyze_timbre(y, sr, audio_path=audio_path, run_separation=False)
            emotion = analyze_emotion(y, sr, key_mode=tonality.mode, bpm=rhythm.bpm)
            lyrics = analyze_lyrics(y, sr, audio_path=audio_path)

            analysis = MusicAnalysisResult(
                file_path=str(audio_path),
                file_name=audio_path.name,
                duration=rhythm.duration,
                sample_rate=sr,
                dependency_tier=dependency_tier(),
                rhythm=rhythm,
                emotion=emotion,
                timbre=timbre,
                tonality=tonality,
                lyrics=lyrics,
                onsets=onsets,
            )
            analysis.color_palette = generate_color_palette(analysis)
    else:
        print(f"Error: input must be an audio file or analysis JSON, got: {input_path.suffix}", file=sys.stderr)
        sys.exit(1)

    # Run formatter
    cmd = args.command

    if cmd == "dreamina":
        from music_analyzer.formatters.dreamina_formatter import format_dreamina
        output = format_dreamina(analysis)
    elif cmd == "storyboard":
        from music_analyzer.formatters.storyboard_formatter import format_storyboard
        output = format_storyboard(analysis)
    elif cmd == "color-palette":
        from music_analyzer.formatters.color_palette import generate_color_palette
        output = generate_color_palette(analysis)
    else:
        print(f"Unknown formatter: {cmd}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(output.model_dump_json(exclude_none=True))
    _output_json(data, getattr(args, "output", None))


def _cmd_visualize(args: argparse.Namespace) -> None:
    """Generate an HTML visualization report."""
    input_path = Path(args.input).expanduser().resolve()

    if input_path.suffix.lower() == ".json":
        from music_analyzer.formatters.json_formatter import load_analysis_json
        analysis = load_analysis_json(str(input_path))
    elif input_path.suffix.lower() in SUPPORTED_FORMATS:
        from music_analyzer.utils.audio_io import validate_audio_path, load_audio
        from music_analyzer.utils.cache import get_cached
        from music_analyzer.models import MusicAnalysisResult

        audio_path = validate_audio_path(str(input_path))
        cached = get_cached(audio_path, "analysis")
        if cached:
            analysis = MusicAnalysisResult(**cached)
        else:
            from music_analyzer.analyzers.rhythm import analyze_rhythm
            from music_analyzer.analyzers.tonality import analyze_tonality
            from music_analyzer.analyzers.onset import analyze_onsets
            from music_analyzer.analyzers.timbre import analyze_timbre
            from music_analyzer.analyzers.emotion import analyze_emotion
            from music_analyzer.analyzers.lyrics import analyze_lyrics
            from music_analyzer.formatters.color_palette import generate_color_palette

            print(f"Analyzing {audio_path.name}...", file=sys.stderr)
            y, sr = load_audio(audio_path)
            rhythm = analyze_rhythm(y, sr)
            tonality = analyze_tonality(y, sr)
            onsets = analyze_onsets(y, sr)
            timbre = analyze_timbre(y, sr, audio_path=audio_path, run_separation=False)
            emotion = analyze_emotion(y, sr, key_mode=tonality.mode, bpm=rhythm.bpm)
            lyrics = analyze_lyrics(y, sr, audio_path=audio_path)

            analysis = MusicAnalysisResult(
                file_path=str(audio_path),
                file_name=audio_path.name,
                duration=rhythm.duration,
                sample_rate=sr,
                dependency_tier=dependency_tier(),
                rhythm=rhythm, emotion=emotion, timbre=timbre,
                tonality=tonality, lyrics=lyrics, onsets=onsets,
            )
            analysis.color_palette = generate_color_palette(analysis)
    else:
        print(f"Error: input must be an audio file or analysis JSON, got: {input_path.suffix}", file=sys.stderr)
        sys.exit(1)

    from music_analyzer.formatters.dreamina_formatter import format_dreamina
    from music_analyzer.formatters.storyboard_formatter import format_storyboard
    from music_analyzer.formatters.html_report import generate_html_report

    dreamina_output = format_dreamina(analysis)
    storyboard_output = format_storyboard(analysis)
    html = generate_html_report(analysis, dreamina_output, storyboard_output)

    # Determine output path
    output_path = getattr(args, "output", None)
    if not output_path:
        stem = input_path.stem
        output_path = str(input_path.parent / f"{stem}_report.html")

    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Report written to {output_path}", file=sys.stderr)

    if getattr(args, "open", False):
        import webbrowser
        webbrowser.open(f"file://{Path(output_path).resolve()}")


def _output_json(data: dict, output_path: str | None = None) -> None:
    """Write JSON to file or stdout."""
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    if output_path:
        Path(output_path).write_text(json_str, encoding="utf-8")
        print(f"Output written to {output_path}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
