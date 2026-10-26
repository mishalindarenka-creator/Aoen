"""Naval units — Monster Hunter aquatic silhouettes + hard Aoen palette.

Top-down sea beasts: fins, shells, horns, biolum strips (not flat tinted ships).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

SPR = Path(__file__).resolve().parents[1] / "sprites" / "units"

NAVAL = ((28, 44, 58, 255), (52, 88, 112, 255), (130, 195, 215, 255))
STEEL = ((40, 46, 56, 255), (78, 90, 104, 255), (170, 190, 210, 255))
DAIMYO = ((48, 12, 14, 255), (110, 28, 32, 255), (210, 70, 70, 255))
STORM = ((36, 32, 72, 255), (78, 68, 140, 255), (170, 160, 240, 255))
T6 = ((16, 14, 20, 255), (40, 70, 90, 255), (120, 220, 240, 255))
FOAM = (220, 240, 255, 255)


def harden(im: Image.Image) -> Image.Image:
    out = im.convert("RGBA")
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 128 else (0, 0, 0, 0)
    return out


def trim(im: Image.Image, pad: int = 3) -> Image.Image:
    im = harden(im)
    bbox = im.getbbox()
    if not bbox:
        return im
    c = im.crop(bbox)
    out = Image.new("RGBA", (c.width + pad * 2, c.height + pad * 2), (0, 0, 0, 0))
    out.paste(c, (pad, pad), c)
    return harden(out)


def save_unit(uid: str, im: Image.Image) -> None:
    body = harden(trim(im))
    body.save(SPR / f"{uid}.png")
    prev = body.copy()
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR / f"{uid}-preview.png")


def hull(w: int, h: int, dark, mid, hi, style: str) -> Image.Image:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # main body oval (nose toward +Y)
    d.ellipse([cx - w // 5, 4, cx + w // 5, h - 4], fill=mid, outline=hi)
    d.ellipse([cx - w // 6, 10, cx + w // 6, h - 10], outline=dark)

    if style == "pup":  # small reef hunter
        d.polygon([(cx - 8, cy), (cx, 2), (cx + 8, cy)], fill=hi)
        d.polygon([(2, cy + 4), (cx - w // 5, cy), (4, h - 6)], fill=dark, outline=hi)
        d.polygon([(w - 3, cy + 4), (cx + w // 5, cy), (w - 5, h - 6)], fill=dark, outline=hi)
        d.rectangle([cx - 2, cy - 2, cx + 2, cy + 6], fill=FOAM)
    elif style == "plesio":  # armored mid
        d.rectangle([cx - 10, 12, cx + 10, h - 12], fill=dark, outline=hi)
        d.ellipse([cx - 6, 6, cx + 6, 18], fill=hi, outline=dark)
        for side in (-1, 1):
            d.polygon([(cx + side * 10, cy - 8), (cx + side * (w // 2 - 2), cy), (cx + side * 10, cy + 10)], fill=mid, outline=hi)
        d.line([(cx, 14), (cx, h - 14)], fill=FOAM)
    elif style == "hermit":  # iron-reef fortress shell
        d.ellipse([6, 8, w - 7, h - 6], fill=dark, outline=hi)
        d.ellipse([12, 14, w - 13, h - 12], outline=mid)
        d.polygon([(cx - 6, 4), (cx, 0), (cx + 6, 4), (cx + 4, 14), (cx - 4, 14)], fill=STEEL[1], outline=hi)
        for a in range(8, w - 8, 8):
            d.rectangle([a, cy - 2, a + 3, cy + 4], fill=hi)
    elif style == "mizu":  # sleek bubble fox / lagiacrus
        d.polygon([(cx, 1), (cx + 12, cy), (cx + 6, h - 3), (cx - 6, h - 3), (cx - 12, cy)], fill=mid, outline=hi)
        d.polygon([(cx - 14, cy - 4), (2, cy + 2), (cx - 10, cy + 10)], fill=STORM[1], outline=FOAM)
        d.polygon([(cx + 14, cy - 4), (w - 3, cy + 2), (cx + 10, cy + 10)], fill=STORM[1], outline=FOAM)
        for y in range(16, h - 10, 6):
            d.ellipse([cx - 3, y, cx + 3, y + 4], outline=FOAM)
        d.ellipse([cx - 2, 8, cx + 2, 14], fill=FOAM)
    elif style == "ceadeus":  # leviathan crown
        d.ellipse([cx - 16, 10, cx + 16, h - 6], fill=dark, outline=hi)
        d.ellipse([cx - 12, 16, cx + 12, h - 12], fill=mid, outline=STEEL[2])
        # horns / crown
        d.polygon([(cx - 18, 18), (cx - 22, 2), (cx - 8, 12)], fill=DAIMYO[2], outline=hi)
        d.polygon([(cx + 18, 18), (cx + 22, 2), (cx + 8, 12)], fill=DAIMYO[2], outline=hi)
        d.polygon([(cx, 4), (cx - 4, 16), (cx + 4, 16)], fill=FOAM)
        d.rectangle([cx - 3, cy - 4, cx + 3, cy + 10], fill=STORM[2])
        for side in (-1, 1):
            d.polygon([(cx + side * 16, cy), (cx + side * (w // 2 - 1), cy + 6), (cx + side * 14, cy + 16)], fill=mid, outline=hi)
    else:  # amatsu / mare emperor
        d.ellipse([cx - 22, 8, cx + 22, h - 4], fill=dark, outline=hi)
        d.ellipse([cx - 16, 16, cx + 16, h - 12], fill=T6[1], outline=FOAM)
        # storm mantle fins
        d.polygon([(2, cy - 10), (cx - 20, 20), (cx - 18, cy + 20), (6, h - 8)], fill=STORM[1], outline=FOAM)
        d.polygon([(w - 3, cy - 10), (cx + 20, 20), (cx + 18, cy + 20), (w - 7, h - 8)], fill=STORM[1], outline=FOAM)
        d.polygon([(cx, 2), (cx + 10, 20), (cx - 10, 20)], fill=FOAM, outline=hi)
        d.rectangle([cx - 4, cy - 6, cx + 4, cy + 16], fill=T6[2], outline=hi)
        for i, ox in enumerate((-12, -4, 4, 12)):
            d.ellipse([cx + ox - 2, h - 18, cx + ox + 2, h - 12], fill=FOAM if i % 2 == 0 else hi)

    # wake strip
    d.line([(cx, h // 3), (cx, h - 6)], fill=FOAM)
    return im


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    specs = [
        ("naval", 40, 56, NAVAL, "pup"),
        ("naval-t2", 48, 64, NAVAL, "plesio"),
        ("iron-reef", 56, 64, STEEL, "hermit"),
        ("needle-skiff", 52, 72, STORM, "mizu"),
        ("leviathan-crown", 64, 84, (DAIMYO[0], NAVAL[1], STORM[2]), "ceadeus"),
        ("mare-imperator", 96, 120, T6, "amatsu"),
    ]
    for uid, w, h, pal, style in specs:
        save_unit(uid, hull(w, h, pal[0], pal[1], pal[2], style))
        print("naval", uid, style)
    print("naval sprites done", len(specs))


if __name__ == "__main__":
    main()
