# Grass GN Math self-hosting

Your current game links point at jsDelivr. The `gn-math` user is currently being blocked there, so loading the game HTML through those URLs can fail even when cover images still load.

This package changes the architecture so the game HTML and covers are stored on your own GitHub Pages site.

## Setup

1. Put `sync_safe_gnmath.py` and `safe_game_ids.txt` in the root of your Grass repository.
2. Install Python 3.10+ and `requests`.
3. Run:

   python sync_safe_gnmath.py

4. The script creates:
   - `games/gnmath/` for game HTML
   - `covers/gnmath/` for covers
   - `games.json` for the Grass catalog
5. Keep the generated paths in `games.json` relative to the Grass site.

Important: this importer is intentionally allowlist-based. Add only game IDs you are permitted to host and that are appropriate for your site. It does not attempt to mirror the entire upstream catalog automatically.
