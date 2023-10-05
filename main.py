#!/usr/bin/env python
import argparse
import json
import os
import re

from audio_processing import extract_url_from_metadata, yt_dlp
from transcribe import transcribe_audio, translate_audio
from tagger import create_tags_from_transcript

# Set up argument parser
parser = argparse.ArgumentParser(
    description="""Transcribes an audio source to text using the OpenAI's Whisper API. The result is saved in the timestamps/ folder as a Markdown file. In case the input is a YouTube URL, the timestamps link to the video at the corresponding time."""
)
parser.add_argument(
    "input",
    type=str,
    help="Path or URL to the audio source to transcribe, in one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm.",
)
parser.add_argument(
    "-p",
    "--prompt",
    type=str,
    help="An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language.",
    default=None,
)
parser.add_argument(
    "-l",
    "--language",
    type=str,
    help="The language of the input audio. Supplying the input language in ISO-639-1 format will improve accuracy and latency.",
    default=None,
)
parser.add_argument(
    "-t",
    "--translate",
    action="store_true",
    help="Translate the audio file to English.",
)

args = parser.parse_args()

# Check if input is a URL
if re.match(r"^https?://", args.input):
    # Download the audio file
    url = args.input
    file = yt_dlp(url)
else:
    file = args.input
    url = extract_url_from_metadata(file)

# Get the base name of the audio file
base_name, extension = os.path.splitext(os.path.basename(file))

if extension not in [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]:
    raise argparse.ArgumentTypeError(
        f"Invalid file extension: {extension}. The file extension must be one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm."
    )

if args.translate:
    # Translate the audio file to English
    transcript = translate_audio(file, args.prompt)
    base_name += "[English]"
else:
    # Transcribe the audio file to text
    transcript = transcribe_audio(file, args.prompt, args.language)

# Write the transcript to a file
with open(f"jsons/{base_name}.json", "w") as file:
    json.dump(transcript, file, indent=4, ensure_ascii=False)

# Create tags from the transcript
tags = create_tags_from_transcript(url, transcript)

# Write the tags to a file
with open(f"timestamps/{base_name}.md", "w") as file:
    print(*tags, sep="\\\n", file=file, end="\n")
