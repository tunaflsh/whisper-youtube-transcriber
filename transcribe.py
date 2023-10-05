import glob
import os
import subprocess

import openai

# Load your OpenAI API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


def split_audio(file, split_sec=3600):
    root, ext = os.path.splitext(file)

    # Split the audio file into smaller chunks
    subprocess.run(
        f'ffmpeg -i "{file}" '
        f'-f segment -segment_time {split_sec} '
        f'-c copy "{root}-%03d{ext}"',
        shell=True, check=True)

    # Return the list of output filenames
    return glob.glob(f'{root}-*{ext}')


def merge(transcripts):
    transcript = {
        "task": transcripts[0]["task"],
        "language": transcripts[0]["language"],
        "duration": 0.00,
        "text": "",
        "segments": [],
    }

    id = 0
    for t in transcripts:
        for s in t["segments"]:
            transcript["segments"].append({
                "id": id,
                "seek": s["seek"] + transcript["duration"] * 100,
                "start": s["start"] + transcript["duration"],
                "end": s["end"] + transcript["duration"],
                "text": s["text"],
                "tokens": s["tokens"],
                "temperature": s["temperature"],
                "avg_logprob": s["avg_logprob"],
                "compression_ratio": s["compression_ratio"],
                "no_speech_prob": s["no_speech_prob"]
            })
            id += 1

        transcript["duration"] += t["duration"]
        transcript["text"] += t["text"]

    return transcript


def transcribe_audio(file, prompt=None, language=None):
    files = [file]

    # Check if the audio file is larger than 25 MB
    if os.path.getsize(file) > 25 * 1024 * 1024:
        # Split the audio file into smaller chunks
        files = split_audio(file)

    responses = []
    for file in files:
        # Open the audio file
        with open(file, "rb") as f:
            # Transcribe the audio file using the Whisper model
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=f,
                prompt=prompt,
                response_format="verbose_json",
                language=language,
            )

        responses.append(response)

    return merge(responses)


def translate_audio(file, prompt=None):
    files = [file]

    # Check if the audio file is larger than 25 MB
    if os.path.getsize(file) > 25 * 1024 * 1024:
        # Split the audio file into smaller chunks
        files = split_audio(file)

    responses = []
    for file in files:
        # Open the audio file
        with open(file, "rb") as f:
            # Translate the audio file to English using the Whisper model
            response = openai.Audio.translate(
                model="whisper-1", file=f, prompt=prompt, response_format="verbose_json"
            )

        responses.append(response)

    return merge(responses)
