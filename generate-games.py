#!/usr/bin/env python3
"""
Generate games.json from your local game folders.
Handles nested folder structures and various file naming patterns.

Usage:
    python3 generate-games.py "C:/Users/corby/Downloads/Gn math"
"""

import os
import json
import sys
import re
from pathlib import Path

def extract_game_number(filename):
    """
    Extract the game number from filenames like:
    - 0.html -> 0
    - 1-fde.html -> 1
    - 10.html -> 10
    - 100-f.html -> 100
    - 101.html -> 101
    
    Returns the number or None if it can't be extracted
    """
    # Remove extension
    name = Path(filename).stem
    
    # Try to extract leading digits
    match = re.match(r'^(\d+)', name)
    if match:
        return int(match.group(1))
    
    return None

def find_files_recursive(parent_dir, extension=".html"):
    """
    Recursively find all files with the given extension.
    Returns a dict of {game_number: full_path}
    """
    parent_dir = Path(parent_dir).resolve()
    files = {}
    
    print(f"   Scanning: {parent_dir}")
    
    if not parent_dir.exists():
        print(f"   ❌ Directory does not exist: {parent_dir}")
        return files
    
    # Recursively find all files with the extension
    for file_path in parent_dir.rglob(f"*{extension}"):
        if file_path.is_file():
            game_num = extract_game_number(file_path.name)
            if game_num is not None:
                # If duplicate number, keep the first one
                if game_num not in files:
                    files[game_num] = file_path
    
    return files

def find_asset_folders(parent_dir):
    """
    Find all numbered asset folders.
    Returns a dict of {game_number: folder_path}
    """
    parent_dir = Path(parent_dir).resolve()
    folders = {}
    
    print(f"   Scanning: {parent_dir}")
    
    if not parent_dir.exists():
        print(f"   ❌ Directory does not exist: {parent_dir}")
        return folders
    
    # Find all folders with numeric names
    for item in parent_dir.rglob("*"):
        if item.is_dir():
            try:
                folder_num = int(item.name)
                if folder_num not in folders:
                    folders[folder_num] = item
            except ValueError:
                pass
    
    return folders

def generate_games_json(base_path=".", output_file="games.json"):
    """
    Scan the game folders and generate games.json
    Handles nested structures and various naming patterns.
    """
    
    base_path = Path(base_path).resolve()
    print(f"📂 Base path: {base_path}")
    
    html_dir = base_path / "html-main"
    covers_dir = base_path / "covers-main"
    assets_dir = base_path / "assets-main"
    
    # Check if folders exist
    if not html_dir.exists():
        print(f"❌ Error: {html_dir} not found!")
        return False
    
    print(f"\n🎮 Searching for HTML files...")
    html_files = find_files_recursive(html_dir, ".html")
    print(f"   ✅ Found {len(html_files)} HTML files")
    
    if len(html_files) == 0:
        print(f"❌ No HTML files found!")
        return False
    
    print(f"\n🖼️  Searching for cover images...")
    covers_files = find_files_recursive(covers_dir, ".png")
    print(f"   ✅ Found {len(covers_files)} cover images")
    
    print(f"\n📦 Searching for asset folders...")
    assets_folders = find_asset_folders(assets_dir)
    print(f"   ✅ Found {len(assets_folders)} asset folders")
    
    games = []
    
    # Process each HTML file
    for game_num in sorted(html_files.keys()):
        # Build the game object
        game = {
            "id": game_num,
            "name": f"Game {game_num}",
            "html": f"https://your-cdn.com/html-main/{game_num}.html",
            "cover": f"https://your-cdn.com/covers-main/{game_num}.png",
            "assets": f"https://your-cdn.com/assets-main/{game_num}/",
            "hasCover": game_num in covers_files,
            "hasAssets": game_num in assets_folders
        }
        
        games.append(game)
    
    # Write to JSON file in the base_path
    output_path = base_path / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Generated {output_file} with {len(games)} games")
    print(f"📁 File saved to: {output_path}")
    
    # Print summary
    games_with_covers = sum(1 for g in games if g["hasCover"])
    games_with_assets = sum(1 for g in games if g["hasAssets"])
    print(f"\n📊 Summary:")
    print(f"   Total games: {len(games)}")
    print(f"   With covers: {games_with_covers}")
    print(f"   With assets: {games_with_assets}")
    if games:
        print(f"   Game ID range: {games[0]['id']} - {games[-1]['id']}")
    
    print(f"\n⚠️  NEXT STEPS:")
    print(f"   1. Replace 'https://your-cdn.com' with your actual CDN URL")
    print(f"   2. Upload html-main/, covers-main/, assets-main/ to your CDN")
    print(f"   3. Update the URLs in {output_file}")
    print(f"\n🌐 CDN Options: Netlify, Vercel, AWS S3, Cloudinary, or GitHub Releases")
    
    return True

if __name__ == "__main__":
    # Get path from command line argument or use current directory
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "."
    
    success = generate_games_json(base_path)
    sys.exit(0 if success else 1)
