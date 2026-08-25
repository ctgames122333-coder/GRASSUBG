#!/usr/bin/env python3
"""
Generate games.json from netlify-upload folder with real Netlify CDN URLs

Usage:
    python3 generate-from-netlify.py "C:/Users/corby/Downloads/netlify-upload"
"""

import json
import sys
import re
from pathlib import Path

# ===== CONFIGURATION =====
NETLIFY_URL = "https://jolly-kangaroo-911b90.netlify.app"
# =========================

def extract_game_number(filename):
    """Extract game number from filenames like 1-fde.html -> 1"""
    name = Path(filename).stem
    match = re.match(r'^(\d+)', name)
    if match:
        return int(match.group(1))
    return None

def find_files_recursive(parent_dir, extension=".html"):
    """Find all files with given extension"""
    parent_dir = Path(parent_dir).resolve()
    files = {}
    
    if not parent_dir.exists():
        print(f"❌ Directory not found: {parent_dir}")
        return files
    
    for file_path in parent_dir.rglob(f"*{extension}"):
        if file_path.is_file():
            game_num = extract_game_number(file_path.name)
            if game_num is not None:
                if game_num not in files:
                    files[game_num] = file_path
    
    return files

def find_asset_folders(parent_dir):
    """Find all numbered asset folders"""
    parent_dir = Path(parent_dir).resolve()
    folders = {}
    
    if not parent_dir.exists():
        return folders
    
    for item in parent_dir.rglob("*"):
        if item.is_dir():
            try:
                folder_num = int(item.name)
                if folder_num not in folders:
                    folders[folder_num] = item
            except ValueError:
                pass
    
    return folders

def generate_games_json(netlify_upload_path, output_file="games.json"):
    """Generate games.json with real CDN URLs"""
    
    netlify_path = Path(netlify_upload_path).resolve()
    
    print("\n" + "=" * 60)
    print("📝 GENERATING GAMES.JSON")
    print("=" * 60)
    print(f"\n📂 Scanning: {netlify_path}")
    
    html_dir = netlify_path / "html-main"
    covers_dir = netlify_path / "covers-main"
    assets_dir = netlify_path / "assets-main"
    
    # Find all files
    print("\n🔍 Finding files...")
    html_files = find_files_recursive(html_dir, ".html")
    covers_files = find_files_recursive(covers_dir, ".png")
    assets_folders = find_asset_folders(assets_dir)
    
    print(f"   🎮 HTML files: {len(html_files)}")
    print(f"   🖼️  Cover images: {len(covers_files)}")
    print(f"   📦 Asset folders: {len(assets_folders)}")
    
    if len(html_files) == 0:
        print(f"\n❌ No HTML files found in {html_dir}")
        print(f"   Make sure files are in: netlify-upload/html-main/")
        return False
    
    games = []
    
    # Process each HTML file
    for game_num in sorted(html_files.keys()):
        game = {
            "id": game_num,
            "name": f"Game {game_num}",
            "html": f"{NETLIFY_URL}/html-main/{game_num}.html",
            "cover": f"{NETLIFY_URL}/covers-main/{game_num}.png",
            "assets": f"{NETLIFY_URL}/assets-main/{game_num}/",
            "hasCover": game_num in covers_files,
            "hasAssets": game_num in assets_folders
        }
        games.append(game)
    
    # Write to JSON file
    output_path = netlify_path / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Generated {output_file}")
    print(f"📁 Saved to: {output_path}")
    
    # Print summary
    games_with_covers = sum(1 for g in games if g["hasCover"])
    games_with_assets = sum(1 for g in games if g["hasAssets"])
    print(f"\n📊 Summary:")
    print(f"   Total games: {len(games)}")
    print(f"   With covers: {games_with_covers}")
    print(f"   With assets: {games_with_assets}")
    if games:
        print(f"   Game ID range: {games[0]['id']} - {games[-1]['id']}")
    
    print(f"\n🌐 CDN URL: {NETLIFY_URL}")
    print(f"   Sample 1: {games[0]['html']}")
    print(f"   Sample 2: {games[0]['cover']}")
    
    print(f"\n" + "=" * 60)
    print("✅ READY TO DEPLOY!")
    print("=" * 60)
    print(f"\n1. Drag netlify-upload folder to: https://app.netlify.app")
    print(f"2. Or update existing site at: https://app.netlify.com")
    print(f"3. Use games.json in your app!")
    
    return True

def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("Usage: python generate-from-netlify.py <path-to-netlify-upload>")
        print("Example: python generate-from-netlify.py C:/Users/corby/Downloads/netlify-upload")
        sys.exit(1)
    
    netlify_path = sys.argv[1]
    success = generate_games_json(netlify_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
