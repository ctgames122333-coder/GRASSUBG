#!/usr/bin/env python3
"""
Generate games.json from your local game folders.
Handles nested folder structures and various file naming patterns.

Usage:
    python3 generate-games.py "C:\Users\corby\Downloads\Gn math"
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

def find_files_in_nested_folder(parent_dir, extension=""):
    """
    Find all files in a folder, handling nested structures.
    Returns a dict of {game_number: full_path}
    """
    parent_dir = Path(parent_dir)
    files = {}
    
    # Search recursively for files with the given extension
    if parent_dir.exists():
        if extension:
            pattern = f"**/*{extension}"
        else:
            pattern = "**/*"
        
        for file_path in parent_dir.glob(pattern):
            if file_path.is_file():
                game_num = extract_game_number(file_path.name)
                if game_num is not None:
                    # If duplicate number, keep the first one
                    if game_num not in files:
                        files[game_num] = file_path
    
    return files

def generate_games_json(base_path=".", output_file="games.json"):
    """
    Scan the game folders and generate games.json
    Handles nested structures and various naming patterns.
    """
    
    base_path = Path(base_path).resolve()
    print(f"📂 Scanning: {base_path}")
    
    html_dir = base_path / "html-main"
    covers_dir = base_path / "covers-main"
    assets_dir = base_path / "assets-main"
    
    # Check if folders exist
    if not html_dir.exists():
        print(f"❌ Error: {html_dir} not found!")
        return False
    
    # Find HTML files (handling nested structure and various naming)
    html_files = find_files_in_nested_folder(html_dir, ".html")
    print(f"🎮 Found {len(html_files)} HTML files")
    
    if len(html_files) == 0:
        print(f"❌ No HTML files found in {html_dir}")
        return False
    
    # Find covers (handling nested structure)
    covers_files = find_files_in_nested_folder(covers_dir, ".png")
    print(f"🖼️  Found {len(covers_files)} cover images")
    
    # Find assets folders
    assets_folders = {}
    if assets_dir.exists():
        for item in assets_dir.rglob("*"):
            if item.is_dir():
                try:
                    folder_num = int(item.name)
                    assets_folders[folder_num] = item
                except ValueError:
                    pass
    print(f"📦 Found {len(assets_folders)} asset folders")
    
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
            "hasCover": False,
            "hasAssets": False
        }
        
        # Check if cover exists
        if game_num in covers_files:
            game["hasCover"] = True
        
        # Check if assets folder exists
        if game_num in assets_folders:
            game["hasAssets"] = True
        
        games.append(game)
    
    # Write to JSON file
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
    
    generate_games_json(base_path)
