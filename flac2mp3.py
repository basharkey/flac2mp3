#!/usr/bin/env python3

from pathlib import Path
import subprocess
import argparse
import concurrent.futures
import json

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input-dir', type=Path, default=Path.home().joinpath('Music/artists'))
parser.add_argument('-o', '--output-dir', type=Path, default=Path('mp3'))
parser.add_argument('--overwrite', action='store_true')
parser.add_argument('--config', type=Path, default=Path.home().joinpath('.config/flac2mp3.json'))
args = parser.parse_args()

def convert(input_file: Path, output_file: Path, overwrite: bool):
    output_dir = output_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_file.is_file() and not overwrite:
        print(f"'{output_file}' already exists, skipping...")
    else:
        # `-map a` don't copy album covers
        subprocess.run(['ffmpeg', '-y', '-i', input_file, '-ab', '320k', '-id3v2_version', '3', '-map', 'a', output_file], check=True, stderr=subprocess.DEVNULL)

def sanitize_path(input_path: Path) -> Path:
    char_replacements = {
        ':': ';'
    }
    output_path = str(input_path.resolve())
    for char_invalid, char_valid in char_replacements.items():
        output_path = output_path.replace(char_invalid, char_valid)
    return Path(output_path)

try:
    with open(args.config, 'r') as c:
        config = json.load(c)
except FileNotFoundError as e:
    config = {}

with concurrent.futures.ThreadPoolExecutor() as executor:
    for input_file in args.input_dir.rglob('*.flac'):
        exclude = any(part in config.get('exclusions', []) for part in input_file.parts)

        if not exclude:
            output_file = args.output_dir.joinpath(input_file.relative_to(args.input_dir)).with_suffix('.mp3')
            executor.submit(convert, input_file, sanitize_path(output_file), args.overwrite)
        else:
            print(f"'{input_file}' in exclusions, skipping...")
