#!/usr/bin/env python3

import sys
import tomllib
from os.path import expanduser, expandvars
from pathlib import Path
from time import time
from typing import Generator

ROOT = Path(__file__).parent
CONFIG = ROOT / "mapping.toml"
SOURCE = ROOT / "source"
BACKUPS = ROOT / "backups"

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"


def _padding(label: str) -> str:
    return label.rjust(8) + " "


def success(message: str) -> None:
    message = GREEN + BOLD + _padding("SUCCESS") + RESET + message
    print(message)


def info(message: str) -> None:
    message = CYAN + BOLD + _padding("INFO") + RESET + message
    print(message)


def warning(message: str) -> None:
    message = YELLOW + BOLD + _padding("WARNING") + RESET + message
    print(message, file=sys.stderr)


def error(message: str) -> None:
    message = RED + BOLD + _padding("ERROR") + RESET + message
    print(message, file=sys.stderr)


def highlight_path(path: Path | str) -> str:
    return BLUE + str(path) + RESET


def read_mapping(tree: dict) -> Generator[tuple[Path, Path], None, None]:
    for directory, value in tree.items():
        if isinstance(value, list):
            for record in value:
                source = Path(directory) / record["filename"]
                destination = Path(
                    expanduser(expandvars(record["destination"]))
                )
                yield (source, destination)
        elif isinstance(value, dict):
            for source, destination in read_mapping(value):
                source = Path(directory) / source
                yield (source, destination)
        else:
            error(f"found invalid scalar in {highlight_path('mapping.toml')}.")


def backup(path: Path) -> None:
    timestamp_ms = str(int(time() * 1000))
    backup_to = BACKUPS / timestamp_ms / path.relative_to(Path.home())
    backup_to.parent.mkdir(parents=True, exist_ok=True)
    path.rename(backup_to)


def main() -> None:

    with open(CONFIG, "rb") as f:
        config = tomllib.load(f)

    for source, destination in read_mapping(config):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_dir() or destination.is_file():
            backup(destination)
            info(
                f"existing {highlight_path(destination)} has been "
                f"backed up to {highlight_path(BACKUPS)}."
            )
        elif destination.exists():
            error(
                f"{highlight_path(source)} has been skipped, "
                f"as {highlight_path(destination)} does already exist "
                "and is neither a directory nor a file, "
                "nor a symbolic link pointing to them."
            )
            continue
        elif destination.is_symlink():
            destination.unlink()
            warning(
                f"found invalid symlink at {highlight_path(destination)}, "
                "and now it has been removed."
            )

        if (SOURCE / source).exists():
            destination.symlink_to(SOURCE / source)
            success(
                f"{highlight_path(source)} has been "
                f"successfully deployed to {highlight_path(destination)}."
            )
        else:
            error(f"{highlight_path(source)} does not exist.")


if __name__ == "__main__":
    main()
