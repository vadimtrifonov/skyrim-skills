#!/usr/bin/env python3
"""Create a new Mutagen C# scratch project under the system temp directory."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path


def task_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("task name must contain a letter or number")
    return slug[:48].rstrip("-")


def mutagen_project(root: Path) -> Path:
    return root / "Mutagen.Bethesda.Skyrim" / "Mutagen.Bethesda.Skyrim.csproj"


def create_project(task_name: str, output: Path | None = None) -> Path:
    mutagen_root_text = os.environ.get("MUTAGEN_ROOT", "").strip()
    if not mutagen_root_text:
        raise RuntimeError("MUTAGEN_ROOT is unset; run this command through mise")

    mutagen_root = Path(mutagen_root_text)
    if not mutagen_project(mutagen_root).is_file():
        raise RuntimeError("Mutagen is not set up; run 'mise run setup' in the skill directory")

    slug = task_slug(task_name)
    if output is None:
        destination = Path(tempfile.mkdtemp(prefix=f"skyrim-mutagen-{slug}-"))
    else:
        destination = output.expanduser().resolve()
        if destination.exists():
            raise FileExistsError(f"output already exists: {destination}")
        destination.mkdir(parents=True)

    template_root = Path(__file__).resolve().parent.parent / "templates"
    try:
        for name in ("Scratch.csproj", "Program.cs"):
            source = template_root / name
            if not source.is_file():
                raise FileNotFoundError(f"template does not exist: {source}")
            shutil.copyfile(source, destination / name)
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise

    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_name", nargs="?", default="scratch")
    parser.add_argument(
        "--output",
        type=Path,
        help="new destination directory; defaults to a unique directory under the system temp folder",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        destination = create_project(args.task_name, args.output)
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
