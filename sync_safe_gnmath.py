#!/usr/bin/env python3
"""
Grass GN Math self-hosting importer.

Purpose:
- Avoid depending on the blocked jsDelivr URL for the game HTML.
- Read GN Math's public zones.json.
- Download only the game IDs you explicitly place in safe_game_ids.txt.
- Store HTML and cover files locally so Grass can load them from your own GitHub Pages site.

Usage:
    python sync_safe_gnmath.py

Requires:
    Python 3.10+
    requests
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote
import requests

ROOT = Path(__file__).resolve().parent
GAMES_DIR = ROOT / "games" / "gnmath"
COVERS_DIR = ROOT / "covers" / "gnmath"
ALLOWLIST = ROOT / "safe_game_ids.txt"
OUTPUT_JSON = ROOT / "games.json"

ZONES_URL = "https://raw.githubusercontent.com/gn-math/assets/main/zones.json"
HTML_RAW = "https://raw.githubusercontent.com/gn-math/html/main/{filename}"
COVER_RAW = "https://raw.githubusercontent.com/gn-math/covers/main/{id}.png"

# These are intentionally explicit. Add only games you have checked and are
# comfortable hosting. The importer never downloads anything not on this list.
DEFAULT_SAFE_IDS = {
    1, 2, 3, 5, 6, 7, 15, 18, 24, 31, 33, 34, 36, 37
}

session = requests.Session()
session.headers.update({"User-Agent": "Grass-GNMath-Importer/1.0"})


def get_json(url: str):
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def get_text(url: str) -> str:
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def get_bytes(url: str) -> bytes:
    r = session.get(url, timeout=60)
    r.raise_for_status()
    return r.content


def load_allowlist() -> set[int]:
    if not ALLOWLIST.exists():
        ALLOWLIST.write_text(
            "# One GN Math numeric ID per line.\n"
            "# The importer only downloads IDs listed here.\n"
            + "\n".join(str(x) for x in sorted(DEFAULT_SAFE_IDS))
            + "\n",
            encoding="utf-8",
        )
    ids = set()
    for raw in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        if raw.isdigit():
            ids.add(int(raw))
    return ids


def find_entries(zones: list[dict], ids: set[int]) -> list[dict]:
    by_id = {}
    for item in zones:
        try:
            by_id[int(item.get("id"))] = item
        except (TypeError, ValueError):
            continue
    return [by_id[i] for i in sorted(ids) if i in by_id]


def html_filename(item: dict) -> str | None:
    url = str(item.get("url", ""))
    if "{HTML_URL}/" in url:
        return url.split("{HTML_URL}/", 1)[1]
    return None


def safe_slug(name: str, game_id: int) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{base or 'game'}-{game_id}"


def main() -> None:
    zones = get_json(ZONES_URL)
    ids = load_allowlist()
    entries = find_entries(zones, ids)

    GAMES_DIR.mkdir(parents=True, exist_ok=True)
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    catalog = []

    for item in entries:
        gid = int(item["id"])
        name = str(item.get("name") or f"Game {gid}")
        filename = html_filename(item)

        # Some catalog entries use a different/non-single-file system.
        if not filename:
            continue

        slug = safe_slug(name, gid)
        local_html = GAMES_DIR / f"{slug}.html"
        local_cover = COVERS_DIR / f"{gid}.png"

        print(f"[HTML] {name} <- {filename}")
        html = get_text(HTML_RAW.format(filename=quote(filename)))

        # Keep the game self-hosted for the files we are importing.
        # GN Math pages sometimes reference their own jsDelivr HTML/assets;
        # rewrite the common GN Math HTML/COVERS bases to local site paths.
        html = html.replace(
            "https://cdn.jsdelivr.net/gh/gn-math/html@main/",
            "/GRASSUBG/games/gnmath/",
        )
        html = html.replace(
            "https://cdn.jsdelivr.net/gh/gn-math/covers@main/",
            "/GRASSUBG/covers/gnmath/",
        )
        html = html.replace(
            "https://cdn.jsdelivr.net/gh/gn-math/assets@main/",
            "/GRASSUBG/games/gnmath/assets/",
        )

        local_html.write_text(html, encoding="utf-8")

        try:
            print(f"[COVER] {gid}")
            local_cover.write_bytes(get_bytes(COVER_RAW.format(id=gid)))
            cover_path = f"covers/gnmath/{gid}.png"
            has_cover = True
        except requests.RequestException:
            cover_path = ""
            has_cover = False

        catalog.append(
            {
                "id": gid,
                "name": name,
                "category": "GN Math",
                "cover": cover_path,
                "url": f"games/gnmath/{local_html.name}",
                "hasCover": has_cover,
                "source": "gn-math",
                "author": item.get("author", ""),
                "authorLink": item.get("authorLink", ""),
            }
        )

    OUTPUT_JSON.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"\nWrote {len(catalog)} games to {OUTPUT_JSON}")
    print(f"Edit {ALLOWLIST} to add more permitted game IDs.")


if __name__ == "__main__":
    main()
