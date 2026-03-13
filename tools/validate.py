#!/usr/bin/env python3

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "mouse.schema.json"
MICE_DIR = REPO_ROOT / "mice"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    try:
        schema = load_json(SCHEMA_PATH)
    except Exception as e:
        print(f"Failed to load schema: {SCHEMA_PATH}\n{e}", file=sys.stderr)
        sys.exit(1)

    validator = Draft202012Validator(schema)

    json_files = sorted(MICE_DIR.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {MICE_DIR}")
        sys.exit(0)

    any_errors = False

    for path in json_files:
        try:
            data = load_json(path)
        except Exception as e:
            print(f"FAIL {path.name}: invalid JSON\n  {e}")
            any_errors = True
            continue

        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

        if errors:
            any_errors = True
            print(f"FAIL {path.name}")
            for error in errors:
                location = ".".join(str(x) for x in error.path) or "<root>"
                print(f"  - {location}: {error.message}")
        else:
            print(f"OK   {path.name}")

    sys.exit(1 if any_errors else 0)


if __name__ == "__main__":
    main()