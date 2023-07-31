import os

import openai

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
