"""Fix drill oh-no: Drill needs -rotator / -top (and optional -rim) sprites."""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

from PIL import Image

MOD = Path(__file__).resolve().parents[1]
SPR = MOD / "sprites" / "blocks"
TMP = Path(os.environ.get("TEMP", ".")) / "mindustry-sprites"
BASE = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/drills"

DRILLS = {
    "dark-drill": ("pneumatic-drill", ((28, 28, 36), (70, 70, 88), (200, 190, 140))),
    "void-drill": ("laser-drill", ((18, 12, 28), (70, 50, 110), (180, 140, 255))),
    "mythril-drill": ("blast-drill", ((40, 44, 52), (140, 150, 170), (230, 235, 245))),
}


def fetch(name: str) -> Image.Image | None:
    TMP.mkdir(parents=True, exist_ok=True)
    dest = TMP / f"{name}.png"
    if not dest.exists() or dest.stat().st_size < 40:
        try:
            urllib.request.urlretrieve(f"{BASE}/{name}.png", dest)
        except Exception as e:
            print("skip", name, e)
            return None
    try:
        return Image.open(dest).convert("RGBA")
    except Exception:
        return None


def tint(im: Image.Image, dark, mid, hi) -> Image.Image:
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    px, op = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            lum = (r * 299 + g * 587 + b * 114) / 1000
            c = hi if lum > 170 else mid if lum > 85 else dark
            op[x, y] = (*c, 255)
    return out


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    for stem, (van, pal) in DRILLS.items():
        dark, mid, hi = pal
        size = 64 if stem == "dark-drill" else 96
        for suf in ("", "-rotator", "-top", "-rim"):
            src = fetch(f"{van}{suf}" if suf else van)
            if src is None and suf == "-rim":
                continue
            if src is None:
                # solid fallback
                im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                from PIL import ImageDraw
                d = ImageDraw.Draw(im)
                m = 4
                d.rectangle([m, m, size - m - 1, size - m - 1], fill=mid, outline=hi)
                if suf == "-rotator":
                    d.ellipse([size // 4, size // 4, 3 * size // 4, 3 * size // 4], outline=hi)
                    d.line([(size // 2, size // 4), (size // 2, 3 * size // 4)], fill=hi, width=3)
                im.save(SPR / f"{stem}{suf}.png")
                print("fallback", stem + suf)
                continue
            if src.width != size or src.height != size:
                src = src.resize((size, size), Image.Resampling.NEAREST)
            tint(src, dark, mid, hi).save(SPR / f"{stem}{suf}.png")
            print("ok", stem + suf)


if __name__ == "__main__":
    main()
