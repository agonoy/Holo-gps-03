#!/usr/bin/env python3
"""Generate an OpenStreetMap tile manifest for Oahu.

Use this helper with Python 3.12 (attached runtime) to inspect tile counts,
preview URL lists, or write a manifest file for offline preparation workflows.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Bounds:
    north: float
    south: float
    west: float
    east: float


OAHU_BOUNDS = Bounds(
    north=21.78,
    south=21.22,
    west=-158.33,
    east=-157.58,
)


def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    lat_rad = math.radians(lat)
    n = 2**zoom
    tile_x = int((lon + 180.0) / 360.0 * n)
    tile_y = int((1.0 - math.log(math.tan(lat_rad) + (1.0 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return tile_x, tile_y


def build_urls(bounds: Bounds, min_zoom: int, max_zoom: int) -> list[str]:
    urls: list[str] = []
    for zoom in range(min_zoom, max_zoom + 1):
        top_left_x, top_left_y = lat_lon_to_tile(bounds.north, bounds.west, zoom)
        bottom_right_x, bottom_right_y = lat_lon_to_tile(bounds.south, bounds.east, zoom)

        for tile_x in range(top_left_x, bottom_right_x + 1):
            for tile_y in range(top_left_y, bottom_right_y + 1):
                urls.append(f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png")

    return urls


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Oahu OSM tile URL manifest")
    parser.add_argument("--min-zoom", type=int, default=11, help="Minimum zoom level (default: 11)")
    parser.add_argument("--max-zoom", type=int, default=14, help="Maximum zoom level (default: 14)")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.min_zoom > args.max_zoom:
        raise SystemExit("--min-zoom must be <= --max-zoom")

    urls = build_urls(OAHU_BOUNDS, args.min_zoom, args.max_zoom)

    payload = {
        "name": "oahu-osm-tile-pack",
        "minZoom": args.min_zoom,
        "maxZoom": args.max_zoom,
        "tileCount": len(urls),
        "urls": urls,
    }

    print(f"Generated {len(urls)} tile URLs for Oahu (z{args.min_zoom}..z{args.max_zoom}).")

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Manifest written to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
