"""High-detail turret sprites (jababarium/ExoGenesis scale), stem names only."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

SPR = Path(__file__).resolve().parents[1] / "sprites" / "blocks"


def pad_canvas(size: int) -> Image.Image:
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def draw_turret(size_tiles: int, palette, style: str = "duo") -> Image.Image:
    """Draw a top-down turret with margin for Mindustry outline."""
    dark, mid, hi, accent = palette
    px = 32 * size_tiles
    im = pad_canvas(px)
    d = ImageDraw.Draw(im)
    m = max(4, px // 16)  # outline margin
    cx, cy = px // 2, px // 2

    # base ring
    d.ellipse([m, m, px - 1 - m, px - 1 - m], fill=dark, outline=hi)
    d.ellipse([m + 3, m + 3, px - 4 - m, px - 4 - m], outline=mid)

    if style in ("duo", "scatter", "flak"):
        barrel_w = max(6, px // 8)
        barrel_h = max(14, px // 2 - m)
        # twin or multi barrels
        barrels = 2 if style == "duo" else (3 if style == "scatter" else 4)
        spread = max(8, px // 10)
        for i in range(barrels):
            ox = (i - (barrels - 1) / 2) * spread
            x0 = int(cx + ox - barrel_w // 2)
            d.rounded_rectangle([x0, m + 2, x0 + barrel_w, cy + 4], radius=2, fill=mid, outline=hi)
            d.rectangle([x0 + 2, m + 2, x0 + barrel_w - 2, m + 8], fill=accent)
        # breech
        d.ellipse([cx - px // 6, cy - px // 8, cx + px // 6, cy + px // 5], fill=dark, outline=hi)
        d.ellipse([cx - 4, cy - 3, cx + 4, cy + 5], fill=accent)
    elif style == "laser":
        bw = max(8, px // 7)
        d.rounded_rectangle([cx - bw // 2, m + 2, cx + bw // 2, cy + 6], radius=3, fill=mid, outline=hi)
        d.rectangle([cx - 2, m + 2, cx + 2, cy], fill=accent)
        d.ellipse([cx - px // 5, cy - 2, cx + px // 5, cy + px // 4], fill=dark, outline=hi)
        # emitter crystal
        d.polygon([(cx, cy - 6), (cx + 8, cy + 4), (cx, cy + 10), (cx - 8, cy + 4)], fill=accent, outline=hi)
    elif style == "rail":
        bw = max(10, px // 6)
        d.rounded_rectangle([cx - bw // 2, m, cx + bw // 2, cy + 8], radius=2, fill=mid, outline=hi)
        d.rectangle([cx - bw // 2 + 2, m + 4, cx + bw // 2 - 2, cy], fill=accent)
        # coils
        for y in range(cy - px // 5, cy + px // 6, max(6, px // 12)):
            d.ellipse([cx - bw // 2 - 4, y, cx + bw // 2 + 4, y + 5], outline=hi)
        d.ellipse([cx - px // 5, cy + 4, cx + px // 5, cy + px // 4], fill=dark, outline=hi)
    elif style == "missile":
        for i, ox in enumerate((-px // 6, 0, px // 6)):
            d.ellipse([cx + ox - 5, m + 4, cx + ox + 5, m + 18], fill=accent, outline=hi)
            d.rectangle([cx + ox - 3, m + 16, cx + ox + 3, cy + 4], fill=mid, outline=hi)
        d.rounded_rectangle([cx - px // 4, cy, cx + px // 4, cy + px // 4], radius=4, fill=dark, outline=hi)
    elif style == "artillery":
        bw = max(12, px // 5)
        d.ellipse([cx - bw, cy - bw // 2, cx + bw, cy + bw], fill=dark, outline=hi)
        d.rounded_rectangle([cx - bw // 3, m + 2, cx + bw // 3, cy + 4], radius=4, fill=mid, outline=hi)
        d.ellipse([cx - 6, m + 2, cx + 6, m + 14], fill=accent, outline=hi)
    else:  # fortress
        d.polygon([(cx, m + 2), (px - m - 2, cy), (cx, px - m - 2), (m + 2, cy)], fill=mid, outline=hi)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=dark, outline=accent)

    return im


def heat_overlay(size_tiles: int) -> Image.Image:
    px = 32 * size_tiles
    im = pad_canvas(px)
    d = ImageDraw.Draw(im)
    cx, cy = px // 2, px // 2
    d.ellipse([cx - px // 6, cy - px // 6, cx + px // 6, cy + px // 6], fill=(255, 90, 40, 200))
    return im


def save(name: str, size: int, palette, style: str) -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    draw_turret(size, palette, style).save(SPR / f"{name}.png")
    heat_overlay(size).save(SPR / f"{name}-heat.png")
    print("turret", name, f"{size}x{size}")


VOID = ((28, 22, 40, 255), (70, 55, 110, 255), (200, 180, 255, 255), (160, 120, 255, 255))
AETH = ((18, 40, 48, 255), (40, 110, 130, 255), (140, 230, 240, 255), (80, 220, 255, 255))
GOLD = ((40, 30, 16, 255), (120, 90, 35, 255), (255, 210, 100, 255), (255, 160, 60, 255))
CER = ((40, 18, 16, 255), (120, 50, 40, 255), (230, 150, 90, 255), (255, 100, 70, 255))
STEEL = ((30, 34, 42, 255), (70, 80, 95, 255), (180, 195, 210, 255), (120, 200, 255, 255))
CRIM = ((40, 10, 14, 255), (110, 25, 35, 255), (220, 60, 70, 255), (255, 180, 80, 255))


def main() -> None:
    save("shard-turret", 1, VOID, "duo")
    save("wave-scatter", 2, AETH, "scatter")
    save("eclipse-beam", 2, GOLD, "laser")
    save("tyrant-rail", 3, CER, "rail")
    save("void-flak", 2, VOID, "flak")
    save("aether-missile", 3, AETH, "missile")
    save("ceramite-howitzer", 3, CER, "artillery")
    save("singularity-lance", 4, GOLD, "laser")
    save("abyss-fortress", 4, CRIM, "fortress")
    save("storm-battery", 3, STEEL, "scatter")
    NOCT = ((28, 20, 42, 255), (90, 70, 130, 255), (180, 150, 230, 255), (140, 100, 255, 255))
    TIDE = ((16, 48, 42, 255), (40, 140, 120, 255), (100, 230, 200, 255), (80, 255, 220, 255))
    save("nocturne-bolt", 2, NOCT, "duo")
    save("tide-pulse", 3, TIDE, "scatter")


if __name__ == "__main__":
    main()
