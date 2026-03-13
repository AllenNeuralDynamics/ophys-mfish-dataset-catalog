#!/usr/bin/env python3

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MICE_DIR = REPO_ROOT / "mice"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    json_files = sorted(MICE_DIR.glob("*.json"))

    if not json_files:
        print("No dataset files found.")
        return

    for path in json_files:
        data = load_json(path)

        mouse_id = data.get("mouse_id", "<missing>")
        nickname = data.get("mouse_metadata", {}).get("nickname", "<missing>")
        rounds = data.get("rounds", {})
        derived_assets = data.get("derived_assets", {})
        notes = data.get("notes", [])

        print(f"{mouse_id}")
        print(f"  nickname: {nickname}")
        print(f"  rounds: {len(rounds)}")
        print(f"  round_names: {', '.join(rounds.keys()) if rounds else '(none)'}")
        print(f"  derived_assets: {', '.join(derived_assets.keys()) if derived_assets else '(none)'}")
        print(f"  notes: {len(notes)}")
        print()
        

if __name__ == "__main__":
    main()