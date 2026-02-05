#!/usr/bin/env python3
"""Azure Speech TTS - Text to speech using Azure Cognitive Services."""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION


def synthesize(text: str, voice: str, output: str, speed: float = 1.0) -> None:
    import azure.cognitiveservices.speech as speechsdk

    key = AZURE_SPEECH_KEY()
    region = AZURE_SPEECH_REGION()

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config
    )

    rate = f"{(speed - 1) * 100:+.0f}%"
    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-CN">'
        f'<voice name="{voice}">'
        f'<prosody rate="{rate}">{text}</prosody>'
        f"</voice></speak>"
    )

    result = synthesizer.speak_ssml_async(ssml).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Saved to {output}")
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        print(f"Error: {details.reason} - {details.error_details}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Azure Speech TTS")
    parser.add_argument("--text", help="Text to synthesize")
    parser.add_argument("--file", help="Read text from file")
    parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="Voice name (default: zh-CN-XiaoxiaoNeural)")
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
