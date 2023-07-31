import argparse
import os
import subprocess
import json
import re


parser = argparse.ArgumentParser(description='Tagger')
parser.add_argument('file', type=str, help='Audio file to tag')
args = parser.parse_args()

basename = os.path.basename(args.file)
basename = os.path.splitext(basename)[0]
json_file = f"jsons/{basename}.json"
tag_file = f"timestamps/{basename}.md"


def extract_metadata(file_path):
    meta_data = subprocess.check_output(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path])
    return json.loads(meta_data)


metadata = extract_metadata(args.file)


def get_json_skeleton(data, root=True):
    if type(data) == dict:
        return {
            k: get_json_skeleton(v) for k, v in data.items()
        }
    if type(data) != list:
        return type(data).__name__
    if any(type(item) != type(data[0]) for item in data):
        raise ValueError("List items must be of the same type")
    
    skeleton = {}
    if type(data[0]) == dict:
        common_keys = set.intersection(*[set(k for k in item if not re.match(r'\[.*\]', k))
                                         for item in data])
        optional_keys = set.union(*[set(item.keys()) for item in data]) - common_keys
        if root:
            skeleton['len'] = len(data)
        skeleton['items'] = {}
        skeleton['items'].update({
            k: get_json_skeleton([item[k] for item in data], root=False)
            for k in common_keys
        })
        skeleton['items'].update({
            re.sub(r'\[?([^\[\]]+)\]?', '[\1]', k):
                get_json_skeleton([item[k] for item in data], root=False)
            for k in optional_keys
        })
        return skeleton
    if type(data[0]) == list:
        lengths = [len(item) for item in data]
        if root:
            skeleton['len'] = len(data)
        skeleton['range'] = (min(lengths), max(lengths))
        skeleton['items'] = get_json_skeleton(
            [x for item in data for x in item], root=False
        )
        return skeleton
    
    if not root:
        return type(data[0]).__name__
    skeleton['len'] = len(data)
    skeleton['items'] = type(data[0]).__name__
    return skeleton


url = metadata['format']['tags']['PURL']

with open(json_file) as f:
    transcript = json.load(f)

with open(tag_file, 'w') as f:
    for segment in transcript['segments']:
        timestamp = int(segment['start'])
        m, s = divmod(timestamp, 60)
        h, m = divmod(m, 60)
        formatted_timestamp = (
            f"{h:2d}:{m:02d}:{s:02d}" if h
            else f"   {m:2d}:{s:02d}"
        )
        text = segment['text']
        f.write(f"[{formatted_timestamp}]({url}&t={timestamp}s) {text}\\\n")
