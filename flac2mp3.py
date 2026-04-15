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
parser.add_argument('--config', type=Path, default=Path.home().joinpath('.config/flac2mp3/flac2mp3.json'))
args = parser.parse_args()

def convert(input_file: Path, output_file: Path, overwrite: bool):
    output_dir = output_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_file.is_file() and not overwrite:
        print(f"'{output_file}' already exists, skipping...")
    else:
        # `-map a` don't copy album covers
        subprocess.run(['ffmpeg', '-y', '-i', input_file, '-ab', '320k', '-id3v2_version', '3', '-map', 'a', output_file], check=True, stderr=subprocess.DEVNULL)

with open(args.config, 'r') as c:
    config = json.load(c)

with concurrent.futures.ThreadPoolExecutor() as executor:
    for input_file in args.input_dir.rglob('*.flac'):
        exclude = False
        for part in input_file.parts:
            if part in config.get('exclusions', []):
                exclude = True

        if not exclude:
            output_file = args.output_dir.joinpath(input_file.relative_to(args.input_dir)).with_suffix('.mp3')
            executor.submit(convert, input_file, output_file, args.overwrite)
        else:
            print(f"'{input_file}' in exclusions, skipping...")
