"""Generate Aoen block sprites from vanilla templates."""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

MOD = Path(__file__).resolve().parents[1]
OUT = MOD / "sprites" / "blocks"
TMP = Path(os.environ.get("TEMP", ".")) / "mindustry-sprites"
BASE = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/units"

# File stems WITHOUT mod prefix (ground-fabricator.png → atlas aoen-ground-fabricator).
BLOCKS = {
    "ground-fabricator": ("ground-factory", False),
    "ground-reconstructor": ("additive-reconstructor", False),
    "ground-reconstructor-t3": ("additive-reconstructor", False),
    "ground-reconstructor-t4": ("multiplicative-reconstructor", False),
    "ground-reconstructor-t5": ("exponential-reconstructor", False),
    "ground-reconstructor-t6": ("exponential-reconstructor", False),
    "naval-fabricator": ("naval-factory", True),
    "naval-reconstructor": ("additive-reconstructor", True),
    "naval-reconstructor-t3": ("additive-reconstructor", True),
    "naval-reconstructor-t4": ("multiplicative-reconstructor", True),
    "naval-reconstructor-t5": ("exponential-reconstructor", True),
    "naval-reconstructor-t6": ("exponential-reconstructor", True),
}


def fetch(name: str) -> Image.Image:
    TMP.mkdir(parents=True, exist_ok=True)
    dest = TMP / f"block-{name}.png"
    if not dest.exists() or dest.stat().st_size < 50:
        urllib.request.urlretrieve(f"{BASE}/{name}.png", dest)
    return Image.open(dest).convert("RGBA")


def tint(im: Image.Image, naval: bool) -> Image.Image:
    r, g, b, a = im.split()
    rgb = ImageEnhance.Color(Image.merge("RGB", (r, g, b))).enhance(1.15 if naval else 1.05)
    rgb = ImageEnhance.Brightness(rgb).enhance(0.92)
    out = Image.merge("RGBA", (*rgb.split(), a))
    d = ImageDraw.Draw(out)
    cx, cy = out.width // 2, out.height // 2
    col = (80, 160, 200, 220) if naval else (120, 70, 180, 220)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=col)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for bid, (van, naval) in BLOCKS.items():
        try:
            base = tint(fetch(van), naval)
        except Exception:
            base = Image.new("RGBA", (96, 96), (40, 40, 50, 255))
            ImageDraw.Draw(base).rectangle([8, 8, 88, 88], outline=(200, 180, 120, 255))
        base.save(OUT / f"{bid}.png")
        if "reconstructor" in bid:
            base.save(OUT / f"{bid}-top.png")
            w, h = base.size
            inp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            outp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            inp.alpha_composite(base.crop((0, 0, w // 2, h)))
            outp.alpha_composite(base.crop((w // 2, 0, w, h)), (w // 2, 0))
            inp.save(OUT / f"{bid}-in.png")
            outp.save(OUT / f"{bid}-out.png")
        print(bid)


if __name__ == "__main__":
    main()
