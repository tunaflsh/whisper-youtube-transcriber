# Whisper YouTube Transcriber

Transcribes an audio source to text using the OpenAI's Whisper API. The result is saved in the `timestamps/` folder as a
Markdown file. In case the input is a YouTube URL, the timestamps link to the video at the corresponding time.

## Result Folders

- `audios/` folder contains extracted audio files from YouTube videos when the input is a YouTube URL.
- `jsons/` folder contains raw responses from Whisper API transcribing/translating the audio files. The structure of the responses is shown in [`transcript.example.json`](https://github.com/tunaflsh/whisper-youtube-transcriber/blob/main/transcript.example.json).
- `timestamps/` folder contains the resulting Markdown files, that includes transcription and their timestamps. The timestamps link to the YouTube video at the matching times when the input when the input is a YouTube URL or the input file has the source YouTube URL embedded to the metadata under `format:tags:comment`.

## Usage

```
python main.py [-h] [-p PROMPT] [-l LANGUAGE] [-t] input

positional arguments:
  input                 Path or URL to the audio source to transcribe, in one of these formats: mp3, mp4, mpeg, mpga,
                        m4a, wav, or webm.

options:
  -h, --help            show this help message and exit
  -p PROMPT, --prompt PROMPT
                        An optional text to guide the model's style or continue a previous audio segment. The prompt
                        should match the audio language.
  -l LANGUAGE, --language LANGUAGE
                        The language of the input audio. Supplying the input language in ISO-639-1 format will improve
                        accuracy and latency.
  -t, --translate       Translate the audio file to English.
```

For practices and examples how to `--prompt` the Whisper model, look at [`prompt.example.md`](https://github.com/tunaflsh/whisper-youtube-transcriber/blob/main/prompt.example.md).\
**TAKE WITH A GRAIN OF SALT! It's incomplete and may not be accurate or work differently depending on the context.**
