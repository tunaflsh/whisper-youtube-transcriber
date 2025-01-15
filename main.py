#!/usr/bin/env python
import argparse
import logging
import logging.config
from logging_config import logging_config

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
    help="A list of correct word spellings for problematic words.",
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
parser.add_argument(
    "-d",
    "--debug",
    nargs="?",
    const="",
    default=[],
    action="append",
    help="Enable debug mode. If a list of modules is provided, only those modules will be debugged.",
)

args = parser.parse_args()
logging.config.dictConfig(logging_config(args.debug))
logger = logging.getLogger(__name__)

import glob
import json
import os
import re

from audio_processing import extract_url, getid, yt_dlp
from tagger import create_tags
from transcribe import transcribe_audio, translate_audio
from transcription_processing import filter_no_speech


def check_not_overwrite(file):
    logger.debug(f"Checking if {file} exists.")

    files = glob.glob(file)
    logger.debug(f"Found: {files}")

    if files and input(
        f'File "{files[0]}" already exists. Overwrite? [y/N] '
    ).lower() not in ["y", "yes"]:
        return files[0]
    return None


# Check if input is a URL
if re.match(r"^https?://", args.input):
    logger.debug(f"Input is a URL: {args.input}")

    # Download the audio file
    url = args.input
    video_id = getid(url)

    # Check if ./audios/{video_id}.* exists
    audio_file = check_not_overwrite(f"./audios/{glob.escape(video_id)}.*") or yt_dlp(
        url
    )
else:
    logger.debug(f"Input is a file: {args.input}")

    audio_file = args.input
    url = extract_url(audio_file)

# Get the base name of the audio file
base_name, extension = os.path.splitext(os.path.basename(audio_file))

if extension not in [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]:
    error = argparse.ArgumentTypeError(
        f"Invalid file extension: {extension}. The file extension must be one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm."
    )
    logger.error(error)
    raise error

if args.translate:
    logger.debug(f"Translation enabled.")
    base_name += "[English]"

# Check if ./jsons/{base_name}.json exists
transcription_json = f"./jsons/{base_name}.json"
if check_not_overwrite(f"./jsons/{glob.escape(base_name)}.json"):
    with open(transcription_json) as f:
        transcription = json.load(f)
else:
    logger.info(f"Transcribing...")

    if args.translate:
        transcription = translate_audio(audio_file, args.prompt)
    else:
        transcription = transcribe_audio(audio_file, args.prompt, args.language)

    logger.info(f"Saving transcription to {transcription_json}")
    os.makedirs(os.path.dirname(transcription_json), exist_ok=True)
    with open(transcription_json, "w") as f:
        json.dump(transcription, f, indent=4, ensure_ascii=False)

    tags = create_tags(url, transcription)
    logger.info(f"Saving timestamps to timestamps/{base_name}.md")
    os.makedirs(os.path.dirname(f"timestamps/{base_name}.md"), exist_ok=True)
    with open(f"timestamps/{base_name}.md", "w") as audio_file:
        print(*tags, sep="\\\n", file=audio_file, end="\n")

# Filter out segments with no speech
speech, no_speech = filter_no_speech(transcription)

if no_speech:
    logger.info(f"[Experimental] Saving segments with speech to jsons/{base_name}-speech.json")
    os.makedirs(os.path.dirname(f"./jsons/{base_name}-speech.json"), exist_ok=True)
    with open(f"./jsons/{base_name}-speech.json", "w") as f:
        json.dump(speech, f, indent=4, ensure_ascii=False)

    speech_tags = create_tags(url, speech)
    logger.info(f"[Experimental] Saving timestamps of segments with speech to timestamps/{base_name}-speech.md")
    os.makedirs(os.path.dirname(f"timestamps/{base_name}-speech.md"), exist_ok=True)
    with open(f"timestamps/{base_name}-speech.md", "w") as audio_file:
        print(*speech_tags, sep="\\\n", file=audio_file, end="\n")

    logger.info(f"[Experimental] Saving segments with no speech to jsons/{base_name}-no_speech.json")
    os.makedirs(os.path.dirname(f"./jsons/{base_name}-no_speech.json"), exist_ok=True)
    with open(f"./jsons/{base_name}-no_speech.json", "w") as f:
        json.dump(no_speech, f, indent=4, ensure_ascii=False)

    no_speech_tags = create_tags(url, no_speech)
    logger.info(f"[Experimental] Saving timestamps of segments with no speech to timestamps/{base_name}-no_speech.md")
    os.makedirs(os.path.dirname(f"timestamps/{base_name}-no_speech.md"), exist_ok=True)
    with open(f"timestamps/{base_name}-no_speech.md", "w") as audio_file:
        print(*no_speech_tags, sep="\\\n", file=audio_file, end="\n")
