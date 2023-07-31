#!/usr/bin/env python
import argparse
import os
import json
import openai
import tiktoken


# Load your OpenAI API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


def transcribe_audio_to_text(file, prompt=None, language=None):
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

    # Return the transcription text
    return response


def translate_audio_to_english(file, prompt=None):
    # Open the audio file
    with open(file, "rb") as f:
        # Translate the audio file to English using the Whisper model
        response = openai.Audio.translate(
            model="whisper-1", file=f, prompt=prompt, response_format="verbose_json"
        )

    # Return the translation text
    return response


def write_transcript_to_file(transcript, filename):
    with open(filename, "w") as file:
        file.write(transcript)


def split(transcript, split_size):
    # Split the transcript into chunks of {split_size} tokens or less
    encoding = tiktoken.get_encoding("cl100k_base")

    chunk_ids = [0]
    if split_size:
        current_size = 0
        for i, segment in enumerate(transcript["segments"]):
            if (s := len(encoding.encode(segment["text"]))) > split_size:
                raise ValueError(f"Segment {i} has more than {split_size} tokens.")
            current_size += s
            if current_size > split_size:
                chunk_ids.append(i)
                current_size = s
    chunk_ids.append(len(transcript["segments"]))

    chunks = []
    for i, j in zip(chunk_ids[:-1], chunk_ids[1:]):
        chunks.append(
            {
                "chunk_id": i,
                "start": transcript["segments"][i]["start"],
                "end": transcript["segments"][j - 1]["end"],
                "tokens": sum(
                    [
                        len(encoding.encode(segment["text"]))
                        for segment in transcript["segments"][i:j]
                    ]
                ),
                "text": "".join(
                    [segment["text"] for segment in transcript["segments"][i:j]]
                ),
            }
        )

    return {
        "split": split_size,
        "num_chunks": len(chunks),
        "total_tokens": sum([chunk["tokens"] for chunk in chunks]),
        "chunks": chunks,
    }


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file to text using the OpenAI API."
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to the audio file to transcribe, in one of these formats: mp3, mp4, mpeg, mpga, m4a, wav, or webm.",
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
    parser.add_argument(
        "-s",
        "--split",
        type=int,
        help="Create a json file splitting the transcript into chunks of {split} tokens or less. The format of the output file is: {'split': int, 'num_chunks': int, 'total_tokens': int, 'chunks': [{'chunk_id': int, 'start': float, 'end': float, 'tokens': int, 'text': str}, ...]}",
        default=None,
    )

    args = parser.parse_args()

    # Get the base name of the audio file
    base_name, extension = os.path.splitext(os.path.basename(args.file))

    if extension in [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]:
        if args.translate:
            # Translate the audio file to English
            transcript = translate_audio_to_english(args.file, args.prompt)
            base_name += "[English]"
        else:
            # Transcribe the audio file to text
            transcript = transcribe_audio_to_text(args.file, args.prompt, args.language)

        # Write the transcript to a file
        with open(base_name + ".json", "w") as file:
            json.dump(transcript, file, indent=4, ensure_ascii=False)

    elif extension == ".json":
        # Get the transcript from the file
        with open(args.file, "r") as file:
            transcript = json.load(file)

    if args.split:
        # Split the transcript into chunks of {split} tokens or less
        split_transcripts = split(transcript, args.split)
        with open(base_name + f"-split{args.split}.json", "w") as file:
            json.dump(split_transcripts, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
