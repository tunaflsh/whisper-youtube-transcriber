import glob
import json
import re
import subprocess


def extract_metadata(file_path):
    meta_data = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            file_path,
        ]
    )
    return json.loads(meta_data)


def extract_url_from_metadata(file_path):
    metadata = extract_metadata(file_path)
    try:
        url = metadata["format"]["tags"]["comment"]
    except KeyError as e:
        file = file_path.replace('"', '\\"')
        print(f'KeyError: {e} in the metadata of "{file}"')
        url = None
    return url


def yt_dlp(url):
    result = subprocess.run(['yt-dlp', '--get-id', url],
                            text=True, capture_output=True, check=True)
    video_id = result.stdout.strip()

    # check if ./audios/{video_id}.* exists
    if files := glob.glob(f'./audios/{video_id}.*'):
        while True:
            overwrite = input(
                f'File "{files[0]}" already exists. Overwrite? [(y)es/(n)o] ')
            if overwrite.lower() in ['n', 'no']:
                return files[0]
            if overwrite.lower() in ['y', 'yes']:
                break

    output = subprocess.check_output(
        [
            "yt-dlp",
            "--format",
            "139",
            "--paths",
            "./audios",
            "--output",
            "%(id)s.%(ext)s",
            "--embed-metadata",
            url,
        ]
    )
    destination = re.search(
        r"\[download\] (?:Destination: (.*)|(.*) has already been downloaded)",
        output.decode("utf-8"),
    )
    return destination.group(1) or destination.group(2)
