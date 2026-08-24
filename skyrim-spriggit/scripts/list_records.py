#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterator


FORM_KEY = re.compile(r"^[0-9A-Fa-f]{6}:.+$")
# Skyrim group names that do not map to record types by regular singularization.
ROOT_TYPE_OVERRIDES = {
    "Actions": "ActionRecord",
    "AlchemicalApparatuses": "AlchemicalApparatus",
    "BodyParts": "BodyPartData",
    "Colors": "ColorRecord",
    "Debris": "Debris",
    "Eyes": "Eyes",
    "Florae": "Flora",
    "ReverbParameters": "ReverbParameters",
    "WordsOfPower": "WordOfPower",
}


class RecordListError(RuntimeError):
    pass


def native_path(path: Path) -> str:
    """Return an absolute path that supports long file names on Windows."""
    absolute = os.path.abspath(os.fspath(path))
    if os.name != "nt" or absolute.startswith("\\\\?\\"):
        return absolute
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute[2:]
    return "\\\\?\\" + absolute


def load_json(path: Path) -> Any:
    try:
        with open(native_path(path), encoding="utf-8") as stream:
            return json.load(stream)
    except json.JSONDecodeError as error:
        raise RecordListError(f"invalid JSON in {path}: {error}") from error
    except OSError as error:
        raise RecordListError(f"cannot read {path}: {error}") from error


def singularize(category: str) -> str:
    if category.endswith(("sses", "shes", "ches", "xes")):
        return category[:-2]
    if category.endswith("ies"):
        return category[:-3] + "y"
    if category.endswith("s"):
        return category[:-1]
    return category


def root_record_type(relative_parts: tuple[str, ...]) -> str:
    category = relative_parts[0]
    if category == "DialogTopics" and relative_parts[-2] == "Responses":
        return "DialogResponses"
    if category == "Worldspaces" and len(relative_parts) > 3:
        return "Cell"
    return ROOT_TYPE_OVERRIDES.get(category, singularize(category))


def record_type(record: dict[str, Any], relative_parts: tuple[str, ...], pointer: tuple[Any, ...]) -> str:
    explicit = record.get("MutagenObjectType")
    if isinstance(explicit, str) and explicit:
        return explicit

    if not pointer:
        return root_record_type(relative_parts)

    field_names = [part for part in pointer if isinstance(part, str)]
    if field_names and field_names[-1] == "TopCell":
        return "Cell"
    if field_names and field_names[-1] == "Landscape":
        return "Landscape"
    if "NavigationMeshes" in field_names:
        return "NavigationMesh"

    location = ".".join(str(part) for part in pointer)
    raise RecordListError(
        f"cannot infer the record type at {'/'.join(relative_parts)}:{location}"
    )


def is_deleted(record: dict[str, Any]) -> bool:
    flags = record.get("SkyrimMajorRecordFlags", [])
    if isinstance(flags, str):
        flags = [flags]
    if isinstance(flags, list) and any(
        isinstance(flag, str) and flag.casefold() == "deleted" for flag in flags
    ):
        return True

    raw = record.get("MajorRecordFlagsRaw")
    try:
        raw_value = int(raw, 0) if isinstance(raw, str) else int(raw)
    except (TypeError, ValueError):
        return False
    return bool(raw_value & 0x20)


def walk_records(
    value: Any,
    relative_parts: tuple[str, ...],
    mod_key: str,
    pointer: tuple[Any, ...] = (),
) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        form_key = value.get("FormKey")
        if isinstance(form_key, str) and FORM_KEY.fullmatch(form_key):
            _, owner = form_key.split(":", 1)
            editor_id = value.get("EditorID")
            yield {
                "type": record_type(value, relative_parts, pointer),
                "formKey": form_key,
                "editorId": editor_id if isinstance(editor_id, str) else None,
                "kind": "new" if owner.casefold() == mod_key.casefold() else "override",
                "deleted": is_deleted(value),
            }

        for name, child in value.items():
            yield from walk_records(child, relative_parts, mod_key, pointer + (name,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_records(child, relative_parts, mod_key, pointer + (index,))


def list_records(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise RecordListError(f"input is not a Spriggit directory: {root}")

    metadata_path = root / "RecordData.json"
    if not metadata_path.is_file():
        raise RecordListError(f"missing root metadata file: {metadata_path}")

    metadata = load_json(metadata_path)
    mod_key = metadata.get("ModKey") if isinstance(metadata, dict) else None
    if not isinstance(mod_key, str) or not mod_key:
        raise RecordListError(f"missing ModKey in {metadata_path}")

    files = sorted(root.rglob("*.json"), key=lambda path: str(path).casefold())
    records: list[dict[str, Any]] = []
    for path in files:
        relative = path.relative_to(root)
        if relative.parts == ("RecordData.json",):
            continue
        if path.name in {"GroupRecordData.json", "spriggit-meta.json"}:
            continue

        data = load_json(path)
        records.extend(walk_records(data, relative.parts, mod_key))

    records.sort(
        key=lambda record: (
            record["type"].casefold(),
            record["formKey"].casefold(),
            (record["editorId"] or "").casefold(),
        )
    )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List every major record in a Spriggit JSON tree as JSONL."
    )
    parser.add_argument("input", type=Path, help="Spriggit output directory")
    args = parser.parse_args()

    try:
        records = list_records(args.input)
    except RecordListError as error:
        parser.exit(1, f"error: {error}\n")

    for record in records:
        sys.stdout.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
