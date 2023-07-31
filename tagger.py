import argparse
import json
import os

from utils import extract_url_from_metadata


def create_tags_from_transcript(url, transcript):
    tags = []
    for segment in transcript["segments"]:
        timestamp = int(segment["start"])
        m, s = divmod(timestamp, 60)
        h, m = divmod(m, 60)
        formatted_timestamp = f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"
        timestamped_url = f"{url}&t={timestamp}s" if url else ""
        text = segment["text"]
        tags.append(f"[{formatted_timestamp}]({timestamped_url}) {text}")
    return tags


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
        transcript = json.load(f)

    tags = create_tags_from_transcript(url, transcript)

    with open(tag_file, "w") as f:
        print(*tags, sep="\\\n", file=f, end="\n")
