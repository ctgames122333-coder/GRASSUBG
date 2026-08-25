#!/usr/bin/env python3
"""
Generate games.json from your local game folders.
Can be run from anywhere - just provide the path to your game folders.

Usage:
    python3 generate-games.py
    
    Or with a custom path:
    python3 generate-games.py "C:\Users\corby\Downloads\Gn math"
"""

import os
import json
import sys
from pathlib import Path

def generate_games_json(base_path=".", output_file="games.json"):
    """
    Scan the game folders and generate games.json
    
    Expected folder structure:
    base_path/
    ├── html-main/
    ├── covers-main/
    └── assets-main/
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
    
    games = []
    
    # Get all HTML files and extract game numbers
    html_files = sorted([f.stem for f in html_dir.glob("*.html")])
    print(f"🎮 Found {len(html_files)} HTML files")
    
    for html_name in html_files:
        try:
            game_num = int(html_name)
        except ValueError:
            # Skip non-numeric files like "9.html" vs "9-f.html"
            continue
        
        # Build the game object
        game = {
            "id": game_num,
            "name": f"Game {game_num}",  # Default name
            "html": f"https://your-cdn.com/html-main/{game_num}.html",
            "cover": f"https://your-cdn.com/covers-main/{game_num}.png",
            "assets": f"https://your-cdn.com/assets-main/{game_num}/",
            "hasAssets": False
        }
        
        # Check if cover exists
        cover_file = covers_dir / f"{game_num}.png"
        if cover_file.exists():
            game["cover"] = f"https://your-cdn.com/covers-main/{game_num}.png"
            game["hasCover"] = True
        else:
            game["hasCover"] = False
        
        # Check if assets folder exists
        assets_folder = assets_dir / str(game_num)
        if assets_folder.exists() and assets_folder.is_dir():
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
    print("\n⚠️  NEXT STEPS:")
    print("   1. Replace 'https://your-cdn.com' with your actual CDN URL")
    print("   2. Upload html-main/, covers-main/, assets-main/ to your CDN")
    print("   3. Run this script again to update the URLs")
    print("\n🌐 CDN Options: Netlify, Vercel, AWS S3, Cloudinary, or GitHub Releases")
    
    return True

if __name__ == "__main__":
    # Get path from command line argument or use current directory
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = "."
    
    generate_games_json(base_path)
