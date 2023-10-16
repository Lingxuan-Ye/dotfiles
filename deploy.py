#!/usr/bin/env python3

from pathlib import Path
import sys
from time import time

import tomllib
from typing import Generator

ROOT = Path(__file__).parent
CONFIG = ROOT / 'mapping.toml'
SOURCE = ROOT / 'source'
BACKUPS = ROOT / 'backups'

RESET = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'

SUCCESS = GREEN + 'Success'.rjust(8) + RESET
WARNING = YELLOW + 'Warning'.rjust(8) + RESET
NOTICE = YELLOW + 'Notice'.rjust(8) + RESET
ERROR = RED + 'Error'.rjust(8) + RESET


def highlight_path(path: Path | str) -> str:
    return BLUE + str(path) + RESET


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def read_mapping(tree: dict) -> Generator[tuple[Path, Path], None, None]:
    for directory, value in tree.items():
        if isinstance(value, list):
            for record in value:
                source = Path(directory) / record['filename']
                destination = Path(record['destination']).expanduser()
                yield (source, destination)
        elif isinstance(value, dict):
            for source, destination in read_mapping(value):
                source = Path(directory) / source
                yield (source, destination)
        else:
            eprint(
                f'{ERROR}: found invalid scalar '
                f'in {highlight_path("mapping.toml")}.'
            )


def backup(path: Path) -> None:
    timestamp_ms = str(int(time() * 1000))
    backup_to = BACKUPS / timestamp_ms / path.relative_to(Path.home())
    backup_to.parent.mkdir(parents=True, exist_ok=True)
    path.rename(backup_to)


def main() -> None:

    with open(CONFIG, 'rb') as f:
        config = tomllib.load(f)

    for source, destination in read_mapping(config):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_dir() or destination.is_file():
            backup(destination)
            print(
                f'{NOTICE}: existing {highlight_path(destination)} '
                f'has been backed up under {highlight_path(BACKUPS)}.'
            )
        elif destination.exists():
            eprint(
                f'{ERROR}: {highlight_path(source)} has been skipped, '
                f'as {highlight_path(destination)} does already exist '
                'and is neither a directory nor a file, '
                'nor a symbolic link pointing to them.'
            )
            continue
        elif destination.is_symlink():
            destination.unlink()
            eprint(
                f'{WARNING}: found invalid symlink '
                f'at {highlight_path(destination)}, '
                'and now it has been removed.'
            )

        if (SOURCE / source).exists():
            destination.symlink_to(SOURCE / source)
            print(
                f'{SUCCESS}: {highlight_path(source)} has been '
                f'successfully deployed to {highlight_path(destination)}.'
            )
        else:
            eprint(f'{ERROR}: {highlight_path(source)} does not exist.')


if __name__ == '__main__':
    main()
