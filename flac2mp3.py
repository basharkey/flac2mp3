#!/usr/bin/env python3

from pathlib import Path
import subprocess
import argparse
import concurrent.futures

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input-dir', type=Path, default=Path.home().joinpath('Music/artists'))
parser.add_argument('-o', '--output-dir', type=Path, default=Path('mp3'))
parser.add_argument('--overwrite', action='store_true')
args = parser.parse_args()

def convert(input_file: Path, output_file: Path, overwrite: bool):
    output_dir = output_file.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_file.is_file() and not overwrite:
        print(f"'{output_file}' already exists skipping...")
    else:
        subprocess.run(['ffmpeg', '-y', '-i', input_file, '-ab', '320k', '-id3v2_version', '3', '-map', 'a', output_file], check=True, stderr=subprocess.DEVNULL)

with concurrent.futures.ThreadPoolExecutor() as executor:
    for input_file in args.input_dir.rglob('*.flac'):
        output_file = args.output_dir.joinpath(input_file.relative_to(args.input_dir)).with_suffix('.mp3')
        executor.submit(convert, input_file, output_file, args.overwrite)
