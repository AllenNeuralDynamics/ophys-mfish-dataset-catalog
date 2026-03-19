#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MICE_DIR = REPO_ROOT / "mice"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def parse_value(raw: str) -> Any:
    # Try to interpret JSON literals first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def set_nested_if_missing(data: dict[str, Any], field_path: str, value: Any) -> bool:
    parts = field_path.split(".")
    current: dict[str, Any] = data

    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        if not isinstance(current[part], dict):
            raise ValueError(
                f"Cannot create nested field under '{part}' because it is not an object"
            )
        current = current[part]

    leaf = parts[-1]
    if leaf in current:
        return False

    current[leaf] = value
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add a field to all mouse JSON records if missing."
    )
    parser.add_argument(
        "field_path",
        help="Field name or nested path, e.g. schema_version or mouse_metadata.sex",
    )
    parser.add_argument(
        "value",
        help='Default value to set. JSON literals allowed, e.g. "1.1.0", [] , {} , true',
    )
    args = parser.parse_args()

    value = parse_value(args.value)

    json_files = sorted(MICE_DIR.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {MICE_DIR}")
        return

    changed_count = 0

    for path in json_files:
        data = load_json(path)

        try:
            changed = set_nested_if_missing(data, args.field_path, value)
        except ValueError as e:
            print(f"ERROR   {path.name}: {e}")
            continue

        if changed:
            dump_json(path, data)
            changed_count += 1
            print(f"UPDATED {path.name}")
        else:
            print(f"SKIP    {path.name}")

    print(f"\nChanged {changed_count} file(s).")


if __name__ == "__main__":
    main()