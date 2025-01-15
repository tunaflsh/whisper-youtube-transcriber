import argparse
import json
import logging
import os
import re

from audio_processing import extract_url

logger = logging.getLogger(__name__)


def format_seconds(seconds: int):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def create_tags(url, transcription):
    logger.debug(f"Creating tags ({url=}).")

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

    url = extract_url(args)

    with open(json_file) as f:
        transcription = json.load(f)

    tags = create_tags(url, transcription)

    os.makedirs(os.path.dirname(tag_file), exist_ok=True)
    with open(tag_file, "w") as f:
        print(*tags, sep="\\\n", file=f, end="\n")
