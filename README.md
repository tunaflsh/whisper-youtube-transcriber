# Whisper YouTube Transcriber

Transcribes an audio source to text using the OpenAI's Whisper API. The result is saved in the `timestamps/` folder as a
Markdown file. The input can be URL to a video source, it will use [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) to download the video and proceed with transcribing.

## Result Folders

- `audios/` folder contains extracted audio files from YouTube videos when the input is a YouTube URL. Large audio files are split into smaller chunks are also saved here.
- `jsons/` folder contains responses from Whisper API transcribing/translating the audio files. The data follows the schema in [`transcription.schema.json`](https://github.com/tunaflsh/whisper-youtube-transcriber/blob/main/transcription.example.json). Some non-speech audio segments may be falsely transcribed as speech by the Whisper model. These segments are filtered out and saved into `json/*-no_speech.json` and `json/*-speech.json` files.
- `timestamps/` folder contains the resulting Markdown files, that includes transcription and their timestamps. The timestamps link to the YouTube video at the matching times when the input when the input is a YouTube URL or the input file has the source YouTube URL embedded to the metadata under `format:tags:comment`. The `*-no_speech.json` and `*-speech.json` files are also timestamped and saved here as `timestamps/*-no_speech.md` and `timestamps/*-speech.md`.

## Usage

```python console
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

Prompt examples can be found in [`prompt.example.md`](https://github.com/tunaflsh/whisper-youtube-transcriber/blob/main/prompt.example.md).
> [!NOTE]
> The examples are not comprehensive and may not work in some contexts.
