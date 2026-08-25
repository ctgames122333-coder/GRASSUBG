#!/usr/bin/env python3
"""
Complete automation script:
1. Copies all game files to netlify-upload folder
2. Generates games.json with real Netlify CDN URLs

Usage:
    python3 copy-and-generate.py "C:/Users/corby/Downloads/Gn math"
"""

import os
import json
import sys
import re
import shutil
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

def copy_files_to_netlify(base_path, netlify_upload_path):
    """Copy all game files from source to netlify-upload folder"""
    
    base_path = Path(base_path).resolve()
    netlify_path = Path(netlify_upload_path).resolve()
    
    print("\n📋 COPYING FILES TO NETLIFY-UPLOAD")
    print("=" * 50)
    
    folders = {
        "html": (base_path / "html-main", netlify_path / "html-main"),
        "covers": (base_path / "covers-main", netlify_path / "covers-main"),
        "assets": (base_path / "assets-main", netlify_path / "assets-main"),
    }
    
    total_copied = 0
    
    for folder_type, (src_dir, dst_dir) in folders.items():
        print(f"\n📁 {folder_type.upper()}")
        
        # Create destination folder if it doesn't exist
        dst_dir.mkdir(parents=True, exist_ok=True)
        print(f"   From: {src_dir}")
        print(f"   To:   {dst_dir}")
        
        if not src_dir.exists():
            print(f"   ❌ Source not found!")
            continue
        
        # Copy all files recursively
        copied_count = 0
        for src_file in src_dir.rglob("*"):
            if src_file.is_file():
                # Calculate relative path to preserve structure
                rel_path = src_file.relative_to(src_dir)
                dst_file = dst_dir / rel_path
                
                # Create subdirectories if needed
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                try:
                    shutil.copy2(src_file, dst_file)
                    copied_count += 1
                except Exception as e:
                    print(f"   ⚠️  Failed to copy {src_file.name}: {e}")
        
        print(f"   ✅ Copied {copied_count} files")
        total_copied += copied_count
    
    print(f"\n✅ Total files copied: {total_copied}")
    return total_copied > 0

def find_files_recursive(parent_dir, extension=".html"):
    """Find all files with given extension"""
    parent_dir = Path(parent_dir).resolve()
    files = {}
    
    if not parent_dir.exists():
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
    print("\n📝 GENERATING GAMES.JSON")
    print("=" * 50)
    
    html_dir = netlify_path / "html-main"
    covers_dir = netlify_path / "covers-main"
    assets_dir = netlify_path / "assets-main"
    
    print(f"\n🔍 Scanning netlify-upload folder...")
    
    # Find all files
    html_files = find_files_recursive(html_dir, ".html")
    covers_files = find_files_recursive(covers_dir, ".png")
    assets_folders = find_asset_folders(assets_dir)
    
    print(f"   🎮 HTML files: {len(html_files)}")
    print(f"   🖼️  Cover images: {len(covers_files)}")
    print(f"   📦 Asset folders: {len(assets_folders)}")
    
    if len(html_files) == 0:
        print(f"\n❌ No HTML files found in {html_dir}")
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
    
    print(f"\n🌐 CDN URL: {NETLIFY_URL}")
    print(f"   Sample HTML: {games[0]['html']}")
    print(f"   Sample cover: {games[0]['cover']}")
    
    return True

def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("Usage: python copy-and-generate.py <path-to-gn-math>")
        print("Example: python copy-and-generate.py C:/Users/corby/Downloads/Gn\\ math")
        sys.exit(1)
    
    base_path = sys.argv[1]
    
    # Determine netlify-upload path (in same Downloads folder)
    base_path_obj = Path(base_path).resolve()
    netlify_upload_path = base_path_obj.parent / "netlify-upload"
    
    print("\n" + "=" * 50)
    print("🚀 GAME FILES AUTOMATION")
    print("=" * 50)
    print(f"\n📂 Source folder: {base_path_obj}")
    print(f"📂 Upload folder: {netlify_upload_path}")
    print(f"🌐 Netlify URL: {NETLIFY_URL}")
    
    # Step 1: Copy files
    if not copy_files_to_netlify(base_path_obj, netlify_upload_path):
        print("\n❌ Failed to copy files!")
        return False
    
    # Step 2: Generate games.json
    if not generate_games_json(netlify_upload_path):
        print("\n❌ Failed to generate games.json!")
        return False
    
    print("\n" + "=" * 50)
    print("✅ ALL DONE!")
    print("=" * 50)
    print(f"\n📋 Your games.json is ready at:")
    print(f"   {netlify_upload_path / 'games.json'}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Drag the netlify-upload folder to https://app.netlify.app")
    print(f"   2. Or update your existing Netlify site with new files")
    print(f"   3. Use the games.json URLs in your app!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
