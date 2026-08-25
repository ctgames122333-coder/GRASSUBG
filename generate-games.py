#!/usr/bin/env python3
"""
Generate games.json from your local game folders.
Place this script in the same parent directory as html-main, covers-main, and assets-main.

Usage:
    python3 generate-games.py
"""

import os
import json
from pathlib import Path

def generate_games_json(base_path=".", output_file="games.json"):
    """
    Scan the game folders and generate games.json
    
    Expected folder structure:
    .
    ├── html-main/
    ├── covers-main/
    └── assets-main/
    """
    
    html_dir = Path(base_path) / "html-main"
    covers_dir = Path(base_path) / "covers-main"
    assets_dir = Path(base_path) / "assets-main"
    
    games = []
    
    # Get all HTML files and extract game numbers
    if html_dir.exists():
        html_files = sorted([f.stem for f in html_dir.glob("*.html") if f.stem.isdigit()])
        
        for html_name in html_files:
            game_num = html_name
            
            # Build the game object
            game = {
                "id": int(game_num),
                "name": f"Game {game_num}",  # Default name
                "html": f"https://your-cdn.com/html-main/{game_num}.html",
                "cover": f"https://your-cdn.com/covers-main/{game_num}.png",
                "assets": f"https://your-cdn.com/assets-main/{game_num}/"
            }
            
            # Check if cover exists
            cover_file = covers_dir / f"{game_num}.png"
            if cover_file.exists():
                game["cover"] = f"https://your-cdn.com/covers-main/{game_num}.png"
            
            # Check if assets folder exists
            assets_folder = assets_dir / game_num
            if assets_folder.exists():
                game["hasAssets"] = True
            else:
                game["hasAssets"] = False
            
            games.append(game)
    
    # Sort by ID
    games.sort(key=lambda x: x["id"])
    
    # Write to JSON file
    output_path = Path(base_path) / output_file
    with open(output_path, 'w') as f:
        json.dump(games, f, indent=2)
    
    print(f"✅ Generated {output_file} with {len(games)} games")
    print(f"📁 File saved to: {output_path.absolute()}")
    print("\n⚠️  IMPORTANT: Replace 'https://your-cdn.com' with your actual CDN URL")
    print("   Options: Netlify, Vercel, AWS S3, Cloudinary, or GitHub Releases")

if __name__ == "__main__":
    # Modify this path if the script is not in the parent directory
    generate_games_json(base_path=".")
