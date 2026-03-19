#!/usr/bin/env python3

from __future__ import annotations

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


def migrate_record(data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False

    # Example 1: bump schema_version if missing or old
    if data.get("schema_version") != "1.1.0":
        data["schema_version"] = "1.1.0"
        changed = True

    # Example 2: ensure notes exists only if you want it normalized
    # Uncomment if you want every record to always have notes
    #
    # if "notes" not in data:
    #     data["notes"] = []
    #     changed = True

    # Example 3: rename old field if it exists
    # if "metadata" in data and "mouse_metadata" not in data:
    #     data["mouse_metadata"] = data.pop("metadata")
    #     changed = True

    return data, changed


def main() -> None:
    json_files = sorted(MICE_DIR.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in {MICE_DIR}")
        return

    changed_count = 0

    for path in json_files:
        data = load_json(path)
        new_data, changed = migrate_record(data)

        if changed:
            dump_json(path, new_data)
            changed_count += 1
            print(f"UPDATED {path.name}")
        else:
            print(f"OK      {path.name}")

    print(f"\nChanged {changed_count} file(s).")


if __name__ == "__main__":
    main()