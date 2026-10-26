"""Calamity-style serpent sprites: distinct head body + trail segments (head/body/tail).

Used with JS worm trail (not Mindustry crawl).
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

SPR = Path(__file__).resolve().parents[1] / "sprites" / "units"


def harden(im: Image.Image) -> Image.Image:
    out = im.convert("RGBA")
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 128 else (0, 0, 0, 0)
    return out


def trim(im: Image.Image, pad: int = 2) -> Image.Image:
    im = harden(im)
    bbox = im.getbbox()
    if not bbox:
        return im
    c = im.crop(bbox)
    out = Image.new("RGBA", (c.width + pad * 2, c.height + pad * 2), (0, 0, 0, 0))
    out.paste(c, (pad, pad), c)
    return harden(out)


def seg(w: int, h: int, dark, mid, hi, kind: str, motif: str = "scales") -> Image.Image:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, w - 2, h - 2], fill=mid, outline=hi)
    d.ellipse([3, 3, w - 4, h - 4], outline=dark)
    if motif == "sand":
        for y in range(4, h - 4, 4):
            d.line([(3, y), (w - 4, y)], fill=hi)
    elif motif == "aqua":
        d.arc([2, 2, w - 3, h - 3], 20, 160, fill=hi)
        d.arc([2, 2, w - 3, h - 3], 200, 340, fill=dark)
    elif motif == "brim":
        d.polygon([(w // 2, 2), (w - 3, h // 2), (w // 2, h - 3), (2, h // 2)], outline=hi)
        d.point((w // 2, h // 2), fill=hi)
    elif motif == "mech":
        d.rectangle([4, 4, w - 5, h - 5], outline=hi)
        d.rectangle([w // 2 - 2, 3, w // 2 + 2, h - 4], fill=dark)
    elif motif == "storm":
        d.line([(w // 2, 2), (w // 2 - 3, h // 2), (w // 2, h - 3)], fill=hi)
        d.line([(w // 2, 2), (w // 2 + 3, h // 2), (w // 2, h - 3)], fill=hi)
    else:  # void
        d.ellipse([w // 2 - 3, h // 2 - 3, w // 2 + 3, h // 2 + 3], fill=hi, outline=dark)

    if kind == "head":
        d.polygon([(2, h // 2), (w // 2, h - 1), (w - 3, h // 2)], fill=hi)
        d.rectangle([w // 2 - 3, h // 3, w // 2 - 1, h // 3 + 2], fill=(255, 255, 255, 255))
        d.rectangle([w // 2 + 1, h // 3, w // 2 + 3, h // 3 + 2], fill=(255, 255, 255, 255))
        d.rectangle([w // 2 - 1, h // 3 + 3, w // 2 + 1, h // 3 + 4], fill=dark)
    elif kind == "tail":
        d.polygon([(w // 2, 1), (w - 2, h // 2), (w // 2, h - 2), (2, h // 2)], fill=mid, outline=hi)
    return trim(im, 2)


def build_serpent(unit_id: str, n: int, dark, mid, hi, motif: str, base_w: int, base_h: int) -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    # head = main unit body (what Mindustry draws)
    head = seg(base_w + 6, base_h + 8, dark, mid, hi, "head", motif)
    head.save(SPR / f"{unit_id}.png")
    for i in range(n):
        t = i / max(n - 1, 1)
        if i == n - 1:
            kind, w, h = "tail", max(base_w - 4, 8), max(int(base_h * 0.75), 14)
        else:
            kind, w, h = "body", max(int(base_w - t * 2), 9), max(int(base_h - t * 3), 16)
        s = seg(w, h, dark, mid, hi, kind, motif)
        s.save(SPR / f"{unit_id}-segment{i}.png")
        # outline stubs (unused by trail, kept for atlas safety)
        ol = Image.new("RGBA", (s.width + 2, s.height + 2), (0, 0, 0, 0))
        od = ImageDraw.Draw(ol)
        od.rectangle([0, 0, s.width + 1, s.height + 1], outline=dark)
        ol.paste(s, (1, 1), s)
        harden(ol).save(SPR / f"{unit_id}-segment-outline{i}.png")

    prev = head.copy()
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR / f"{unit_id}-preview.png")

    # tiny leg/cell stubs for legs/mech types
    leg = Image.new("RGBA", (8, 10), (0, 0, 0, 0))
    ld = ImageDraw.Draw(leg)
    ld.rectangle([2, 0, 5, 9], fill=mid, outline=hi)
    harden(trim(leg)).save(SPR / f"{unit_id}-leg.png")
    cell = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cell)
    cd.ellipse([1, 1, 10, 10], fill=hi, outline=dark)
    harden(cell).save(SPR / f"{unit_id}-cell.png")
    print("serpent", unit_id, n, motif)


def main() -> None:
    # Desert Scourge
    build_serpent("snake", 8, (72, 52, 28, 255), (180, 140, 70, 255), (240, 210, 120, 255), "sand", 14, 24)
    # Aquatic Scourge
    build_serpent("snake-t2", 10, (20, 48, 58, 255), (40, 120, 130, 255), (120, 230, 220, 255), "aqua", 15, 26)
    # Brimstone
    build_serpent("cinder-millipede", 10, (60, 18, 12, 255), (160, 50, 28, 255), (255, 140, 40, 255), "brim", 16, 28)
    # Plague/mech
    build_serpent("payload-serpent", 11, (28, 52, 42, 255), (48, 110, 82, 255), (90, 210, 150, 255), "mech", 16, 28)
    # Storm Weaver (flying)
    build_serpent("singularity-eel", 12, (24, 28, 70, 255), (70, 80, 180, 255), (180, 200, 255, 255), "storm", 17, 30)
    # Devourer-like
    build_serpent("ouroboros-prime", 16, (14, 8, 28, 255), (80, 30, 120, 255), (220, 140, 255, 255), "void", 24, 42)


if __name__ == "__main__":
    main()
