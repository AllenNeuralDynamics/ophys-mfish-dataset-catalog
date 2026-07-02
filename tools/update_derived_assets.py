#!/usr/bin/env python3
"""Search Code Ocean for a derived-asset type and record the latest match per mouse.

For each target mouse, this finds the newest Code Ocean data asset carrying the
given tag whose name contains the mouse_id (as an underscore-delimited token) and
writes it into that mouse's ``derived_assets`` map.

    # update the pairwise-unmixing asset for two mice
    python tools/update_derived_assets.py pairwise-unmixing 800792 782149

    # refresh roi-shape-metrics for every record, previewing first
    python tools/update_derived_assets.py roi-shape-metrics --all --dry-run

The derived_assets key defaults to the tag with '-' -> '_' (so `pairwise-unmixing`
-> `pairwise_unmixing`, matching the existing `roi_shape_metrics` convention);
override with --key. Auth comes from the CODEOCEAN_DOMAIN + CODEOCEAN_TOKEN env
vars (loaded from a .env in the repo or workspace root if present).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence

from codeocean import CodeOcean
from codeocean.components import SearchFilter
from codeocean.data_asset import DataAsset, DataAssetSearchParams


REPO_ROOT = Path(__file__).resolve().parents[1]
MICE_DIR = REPO_ROOT / "mice"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def load_dotenv() -> None:
    """Load KEY=VALUE lines from a .env in the repo or workspace root (env wins)."""
    for candidate in (REPO_ROOT / ".env", REPO_ROOT.parent / ".env"):
        if not candidate.exists():
            continue
        with candidate.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def get_client() -> CodeOcean:
    load_dotenv()
    domain = os.environ.get("CODEOCEAN_DOMAIN")
    token = os.environ.get("CODEOCEAN_TOKEN")
    if not domain or not token:
        raise SystemExit("Set CODEOCEAN_DOMAIN and CODEOCEAN_TOKEN (env or .env).")
    return CodeOcean(domain=domain, token=token)


def search_by_tag(client: CodeOcean, tag: str, query: Optional[str] = None) -> Iterator[DataAsset]:
    """Yield assets carrying `tag` (newest first), paginating transparently."""
    next_token: Optional[str] = None
    while True:
        results = client.data_assets.search_data_assets(
            DataAssetSearchParams(
                query=query,
                filters=[SearchFilter(key="tags", value=tag)],
                sort_field="created",
                sort_order="desc",
                archived=False,
                limit=100,
                next_token=next_token,
            )
        )
        for asset in results.results:
            yield asset
        if not results.has_more or not results.next_token:
            break
        next_token = results.next_token


def name_matches_mouse(name: str, mouse_id: str) -> bool:
    """True if mouse_id appears as an underscore-delimited token in the asset name.

    Guards against `783552` matching `783552-01`: names embed the id as a whole
    token (`HCR_783552-01_...`, `HCR_800792_roi-shape-metrics_...`).
    """
    return mouse_id in name.split("_")


def latest_asset_for_mouse(client: CodeOcean, tag: str, mouse_id: str) -> Optional[DataAsset]:
    """Newest asset tagged `tag` whose name contains `mouse_id` as a token."""
    for asset in search_by_tag(client, tag, query=mouse_id):  # newest first
        if name_matches_mouse(asset.name, mouse_id):
            return asset
    return None


def target_records(mouse_ids: Sequence[str], use_all: bool) -> list[Path]:
    if use_all:
        return sorted(MICE_DIR.glob("*.json"))
    paths = []
    for mid in mouse_ids:
        path = MICE_DIR / f"{mid}.json"
        if not path.exists():
            print(f"MISSING {path.name}: no record for mouse {mid}")
            continue
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tag", help="Code Ocean asset tag to search, e.g. pairwise-unmixing")
    parser.add_argument("mouse_ids", nargs="*", help="mouse_ids to update (record filename stem)")
    parser.add_argument("--all", action="store_true", help="update every record in mice/")
    parser.add_argument("--key", help="derived_assets key (default: tag with '-' -> '_')")
    parser.add_argument("--dry-run", action="store_true", help="show changes without writing")
    args = parser.parse_args()

    if not args.all and not args.mouse_ids:
        parser.error("provide one or more mouse_ids, or --all")

    key = args.key or args.tag.replace("-", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
        parser.error(f"derived_assets key {key!r} must match ^[a-z][a-z0-9_]*$ (use --key)")

    paths = target_records(args.mouse_ids, args.all)
    if not paths:
        print("No records to update.")
        return

    client = get_client()
    changed_count = 0

    for path in paths:
        data = load_json(path)
        mouse_id = data.get("mouse_id", path.stem)

        asset = latest_asset_for_mouse(client, args.tag, mouse_id)
        if asset is None:
            print(f"NONE    {path.name}: no '{args.tag}' asset found for {mouse_id}")
            continue

        current = data.get("derived_assets", {}).get(key)
        if current == asset.name:
            print(f"SKIP    {path.name}: {key} already == {asset.name}")
            continue

        verb = "would set" if args.dry_run else "set"
        prev = f" (was {current})" if current else ""
        print(f"UPDATE  {path.name}: {verb} {key} = {asset.name}{prev}")

        if not args.dry_run:
            data.setdefault("derived_assets", {})[key] = asset.name
            dump_json(path, data)
        changed_count += 1

    suffix = " (dry run, nothing written)" if args.dry_run else ""
    print(f"\n{changed_count} record(s) to change{suffix}.")


if __name__ == "__main__":
    main()
