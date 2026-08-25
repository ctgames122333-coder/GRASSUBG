#!/usr/bin/env python3
"""
Generate games.json from your local game folders.
Handles nested folder structures automatically.

Usage:
    python3 generate-games.py "C:\Users\corby\Downloads\Gn math"
"""

import os
import json
import sys
from pathlib import Path

def find_files_in_nested_folder(parent_dir, extension=""):
    """
    Find all files in a folder, handling nested structures.
    Returns a dict of {filename_stem: full_path}
    """
    parent_dir = Path(parent_dir)
    files = {}
    
    # First, check if files are directly in this folder
    if parent_dir.exists():
        if extension:
            pattern = f"*{extension}"
        else:
            pattern = "*"
        
        direct_files = list(parent_dir.glob(pattern))
        if direct_files:
            for f in direct_files:
                if f.is_file():
                    files[f.stem] = f
        
        # If no direct files, check nested folders (one level deep)
        if not files:
            for subfolder in parent_dir.iterdir():
                if subfolder.is_dir():
                    nested_files = list(subfolder.glob(pattern))
                    for f in nested_files:
                        if f.is_file():
                            files[f.stem] = f
    
    return files

def generate_games_json(base_path=".", output_file="games.json"):
    """
    Scan the game folders and generate games.json
    Handles both flat and nested folder structures.
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
    
    # Find HTML files (handling nested structure)
    html_files = find_files_in_nested_folder(html_dir, ".html")
    print(f"🎮 Found {len(html_files)} HTML files")
    
    if len(html_files) == 0:
        print(f"❌ No HTML files found in {html_dir}")
        print(f"   Checked: direct files and one level of subfolders")
        return False
    
    # Find covers (handling nested structure)
    covers_files = find_files_in_nested_folder(covers_dir, ".png")
    print(f"🖼️  Found {len(covers_files)} cover images")
    
    # Find assets folders
    assets_folders = {}
    if assets_dir.exists():
        for item in assets_dir.rglob("*"):
            if item.is_dir() and item.name.isdigit():
                assets_folders[item.name] = item
    print(f"📦 Found {len(assets_folders)} asset folders")
    
    games = []
    
    # Process each HTML file
    for html_stem in sorted(html_files.keys()):
        try:
            game_num = int(html_stem)
        except ValueError:
            # Skip non-numeric files
            continue
        
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
        if str(game_num) in covers_files:
            game["hasCover"] = True
        
        # Check if assets folder exists
        if str(game_num) in assets_folders:
            game["hasAssets"] = True
        
        games.append(game)
    
    # Sort by ID
    games.sort(key=lambda x: x["id"])
    
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
