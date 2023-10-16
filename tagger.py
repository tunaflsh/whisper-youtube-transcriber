import argparse
import os
import re

import json
from audio_processing import extract_url_from_metadata


def format_seconds(seconds: int):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def create_tags_from_transcription(url, transcription):
    tags = []
    for segment in transcription["segments"]:
        timestamp = int(segment["start"])
        formatted_timestamp = format_seconds(timestamp)
        timestamped_url = f"{url}&t={timestamp}s" if is_yt(url) else ""
        text = segment["text"]
        tags.append(f"[{formatted_timestamp}]({timestamped_url}) {text}")
    return tags


def is_yt(url):
    return re.match(r"^https?://(www\.)?youtu(\.be|be\.com)", url or "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tagger")
    parser.add_argument("file", type=str, help="Audio file to tag")
    args = parser.parse_args()

    basename = os.path.basename(args.file)
    basename = os.path.splitext(basename)[0]
    json_file = f"jsons/{basename}.json"
    tag_file = f"timestamps/{basename}.md"

    url = extract_url_from_metadata(args)

    with open(json_file) as f:
        transcription = json.load(f)

    tags = create_tags_from_transcription(url, transcription)

    with open(tag_file, "w") as f:
        print(*tags, sep="\\\n", file=f, end="\n")
