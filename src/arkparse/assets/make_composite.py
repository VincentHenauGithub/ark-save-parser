#!/usr/bin/env python3
"""
make_composite.py

Downloads map tiles from a tile server and composites them into a single image.
Auto-detects grid size using binary search.

Requires: Pillow (PIL)
  pip install pillow
"""
from __future__ import annotations

import io
import os
import sys
from typing import List
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from pathlib import Path

try:
    from PIL import Image
except Exception as e:
    print("Pillow is required: pip install pillow", file=sys.stderr)
    raise

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Referer": "https://wikily.gg/",
}

TILE_SIZE = 256


def tile_exists(base_url: str, zoom: int, x: int, y: int) -> bool:
    """Check if a tile exists at the given coordinates."""
    url = f"{base_url}/{zoom}/{x}/{y}.png"
    try:
        req = Request(url, headers=HEADERS, method='HEAD')
        with urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except HTTPError:
        return False
    except Exception:
        # Try GET as fallback (some servers don't support HEAD)
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except:
            return False


def find_grid_size(base_url: str, zoom: int) -> int:
    """
    Binary search to find the grid size (number of tiles per side).
    Assumes square grid starting at 0,0.
    """
    print(f"Detecting grid size for zoom {zoom}...")
    
    # First, verify tile 0,0 exists
    if not tile_exists(base_url, zoom, 0, 0):
        raise SystemExit(f"Tile 0,0 does not exist at {base_url}/{zoom}/")
    
    # Binary search for max coordinate
    low, high = 1, 256  # reasonable upper bound
    
    # First find an upper bound that doesn't exist
    while tile_exists(base_url, zoom, high - 1, 0):
        high *= 2
        if high > 1024:
            raise SystemExit("Grid size exceeds reasonable limit (1024)")
    
    # Binary search
    while low < high:
        mid = (low + high) // 2
        if tile_exists(base_url, zoom, mid, 0):
            low = mid + 1
        else:
            high = mid
    
    grid_size = low
    print(f"Detected grid size: {grid_size}x{grid_size} tiles")
    return grid_size


def download_image(url: str) -> Image.Image:
    """Download an image from URL and return as PIL Image."""
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
    return Image.open(io.BytesIO(data)).convert("RGBA")


def compose_map(base_url: str, zoom: int, out_path: str) -> None:
    """Download all tiles for a zoom level and compose into single image."""
    grid_size = find_grid_size(base_url, zoom)
    
    width = grid_size * TILE_SIZE
    height = grid_size * TILE_SIZE
    total_tiles = grid_size * grid_size
    
    print(f"Canvas size: {width}x{height} ({total_tiles} tiles)")
    
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    downloaded = 0
    failed = 0
    
    for y in range(grid_size):
        for x in range(grid_size):
            tile_num = y * grid_size + x + 1
            url = f"{base_url}/{zoom}/{x}/{y}.png"
            print(f"Downloading tile {tile_num}/{total_tiles}: {zoom}/{x}/{y}.png", end="")
            
            try:
                img = download_image(url)
                if img.size != (TILE_SIZE, TILE_SIZE):
                    img = img.resize((TILE_SIZE, TILE_SIZE))
                
                paste_x = x * TILE_SIZE
                paste_y = y * TILE_SIZE
                canvas.paste(img, (paste_x, paste_y))
                downloaded += 1
                print(" OK")
            except Exception as e:
                print(f" FAILED: {e}")
                failed += 1
    
    print(f"\nDownloaded: {downloaded}, Failed: {failed}")
    
    # Save
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    canvas.convert("RGB").save(out_path, format="PNG")
    print(f"Saved -> {out_path}")


def main() -> None:
    # Configuration
    output_dir = Path(__file__).parent
    zoom = 5
    
    # List of maps to download: (base_url, output_name)
    maps: List[tuple[str, str]] = [
        ("https://r2.wikily.gg/images/ark/maps/lost_colony_tiles", "LOST_COLONY.png"),
        ("https://r2.wikily.gg/images/ark/maps/valguero_tiles", "VALGUERO.png"),
        ("https://r2.wikily.gg/images/ark/maps/aberration_tiles", "ABERRATION.png"),
        ("https://r2.wikily.gg/images/ark/maps/ragnarok_tiles", "RAGNAROK.png"),
        ("https://r2.wikily.gg/images/ark/maps/the_island_tiles", "THE_ISLAND.png"),
        ("https://r2.wikily.gg/images/ark/maps/genesis_tiles", "GENESIS_BIOMES.png"),
        ("https://r2.wikily.gg/images/ark/maps/genesisocean_tiles", "GENESIS_OCEAN.png"),
    ]
    
    for base_url, output_name in maps:
        print(f"\n{'='*60}")
        print(f"Processing: {output_name}")
        print(f"Base URL: {base_url}")
        print(f"Zoom: {zoom}")
        print('='*60)
        
        out_path = os.path.join(output_dir, output_name)
        try:
            compose_map(base_url, zoom, out_path)
        except Exception as e:
            print(f"ERROR processing {output_name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
