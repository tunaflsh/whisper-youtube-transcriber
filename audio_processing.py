import json
import re
import subprocess
import logging

logger = logging.getLogger(__name__)


def extract_metadata(file_path):
    meta_data = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            file_path,
        ],
        check=True,
        capture_output=True,
    ).stdout
    return json.loads(meta_data)


def extract_url(file_path):
    logger.debug(f"Trying to extract URL from {file_path}")

    metadata = extract_metadata(file_path)
    try:
        url = metadata["format"]["tags"]["comment"]
    except KeyError as e:
        file = file_path.replace('"', '\\"')
        logger.warning(f'KeyError: {e} in the metadata of "{file}"')
        url = None
    return url


def getid(url):
    video_id = subprocess.run(
        ["yt-dlp", "--get-id", url], text=True, check=True, capture_output=True
    ).stdout.strip()
    return video_id


def yt_dlp(url):
    logger.debug(f"Downloading {url}")

    output = subprocess.run(
        [
            "yt-dlp",
            "--format",
            "bestaudio.2/bestaudio/best.2/best",
            # "--format-sort",
            # "+size,+br,+res,+fps",
            "--extract-audio",
            "--paths",
            "./audios",
            "--output",
            "%(id)s.%(ext)s",
            "--embed-metadata",
            url,
        ],
        text=True,
        check=True,
        capture_output=True,
    ).stdout
    destination = re.findall(
        r"\[(?:.*)\] (?:Destination: (.*)|(.*) has already been downloaded)",
        output,
    )[-1]
    destination = destination[0] or destination[1]

    logger.debug(f"Downloaded {url} to {destination}")
    return destination
