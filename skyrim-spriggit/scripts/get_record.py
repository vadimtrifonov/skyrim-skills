#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from spriggit_tree import FORM_KEY, RecordObject, SpriggitTree, SpriggitTreeError


class RecordLookupError(RuntimeError):
    pass


def record_location(item: RecordObject) -> str:
    path = json.dumps(list(item.path), ensure_ascii=False, separators=(",", ":"))
    return f"{item.source.as_posix()} path={path}"


def get_record(root: Path, form_key: str) -> dict[str, Any]:
    if not FORM_KEY.fullmatch(form_key):
        raise RecordLookupError(
            f"invalid FormKey {form_key!r}. Expected 000000:Plugin.ext"
        )

    matches = [
        item
        for item in SpriggitTree(root).records()
        if item.data["FormKey"].casefold() == form_key.casefold()
    ]
    if not matches:
        raise RecordLookupError(f"record not found: {form_key}")
    if len(matches) > 1:
        locations = " | ".join(record_location(item) for item in matches)
        raise RecordLookupError(f"multiple records found for {form_key}: {locations}")

    match = matches[0]
    return {
        "source": match.source.as_posix(),
        "path": list(match.path),
        "record": match.data,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Get one complete major record from a Spriggit JSON tree."
    )
    parser.add_argument("input", type=Path, help="Spriggit output directory")
    parser.add_argument("form_key", help="FormKey in 000000:Plugin.ext format")
    args = parser.parse_args()

    try:
        result = get_record(args.input, args.form_key)
    except (RecordLookupError, SpriggitTreeError) as error:
        parser.exit(1, f"error: {error}\n")

    sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
