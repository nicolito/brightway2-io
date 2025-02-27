from tqdm import tqdm
import requests
import re
from pathlib import Path


def get_filename(response):
    if "Content-Disposition" in response.headers.keys():
        filename = re.findall("filename=(.+)", response.headers["Content-Disposition"])[0]
    else:
        filename = url.split("/")[-1]
    if filename[0] in "'\"":
        filename = filename[1:]
    if filename[-1] in "'\"":
        filename = filename[:-1]
    if not filename:
        raise ValueError("Can't determine suitable filename")
    return filename


def download_with_progressbar(url, filename=None, dirpath=None, chunk_size=4096 * 8):
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise ValueError(
            f"URL {url} returns status code {response.status_code}"
        )

    if not filename:
        filename = get_filename(response)

    total_length = response.headers.get('content-length')

    filepath = (Path(dirpath) / filename) if dirpath else (Path.cwd() / filename)

    with open(filepath, "wb") as f:
        print(f"Downloading {filename} to {filepath}")
        if not total_length:
            f.write(response.content)
        else:
            total_length = int(total_length)
            with tqdm(total=total_length) as pbar:
                for data in response.iter_content(chunk_size=chunk_size):
                    f.write(data)
                    pbar.update(chunk_size)

    return filepath
