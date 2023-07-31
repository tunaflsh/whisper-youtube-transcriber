import argparse
import os
import subprocess
import json


parser = argparse.ArgumentParser(description='Tagger')
parser.add_argument('file', type=str, help='Audio file to tag')
args = parser.parse_args()

basename = os.path.basename(args.file)
basename = os.path.splitext(basename)[0]
json_file = f"jsons/{basename}.json"
tag_file = f"timestamps/{basename}.md"


def extract_metadata(file_path):
    meta_data = subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path])
    return json.loads(meta_data)


metadata = extract_metadata(args.file)
try:
    url = metadata['format']['tags']['PURLf']
except KeyError as e:
    file = args.file.replace('"', '\\"')
    print(f'KeyError: {e} in the metadata of "{file}"')
    url = None

with open(json_file) as f:
    transcript = json.load(f)

tags = []
for segment in transcript['segments']:
    timestamp = int(segment['start'])
    m, s = divmod(timestamp, 60)
    h, m = divmod(m, 60)
    formatted_timestamp = (
        f"{h:d}:{m:02d}:{s:02d}" if h
        else f"{m:d}:{s:02d}"
    )
    timestamped_url = f"{url}&t={timestamp}s" if url else ''
    text = segment['text']
    tags.append(f"[{formatted_timestamp}]({timestamped_url}) {text}")

with open(tag_file, 'w') as f:
    print(*tags, sep='\\\n', file=f, end='\n')
