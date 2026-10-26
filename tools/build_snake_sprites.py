"""Snake/crawl sprite system — elongated segments that read as a serpent, not a blob.

Crawl draws ALL segments at the unit position with sine offset + interpolated rotation.
Each segment sprite must be long on the forward axis (Y-up) and narrow on X.
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


def segment(w: int, h: int, dark, mid, hi, kind: str = "body") -> Image.Image:
    """Y-long capsule. kind: head | body | tail."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # outer plate
    d.rectangle([1, 1, w - 2, h - 2], fill=mid, outline=hi)
    # inner darker ridge (scales)
    d.rectangle([3, 3, w - 4, h - 4], outline=dark)
    # center line
    d.line([(w // 2, 2), (w // 2, h - 3)], fill=hi)
    if kind == "head":
        # snout toward +Y (engine draws rot-90 so forward is up in sprite)
        d.polygon([(2, h - 4), (w // 2, h - 1), (w - 3, h - 4)], fill=hi)
        d.rectangle([w // 2 - 2, h // 3, w // 2, h // 3 + 2], fill=(255, 255, 255, 255))
        d.rectangle([w // 2 + 1, h // 3, w // 2 + 2, h // 3 + 2], fill=(255, 255, 255, 255))
        d.rectangle([w // 2 - 1, h // 3 + 1, w // 2 + 1, h // 3 + 1], fill=dark)
    elif kind == "tail":
        d.polygon([(w // 2, 1), (w - 2, h // 2), (w // 2, h - 2), (2, h // 2)], fill=mid, outline=hi)
        d.rectangle([w // 2 - 1, h // 2 - 2, w // 2 + 1, h - 3], fill=hi)
    else:
        # armor plates
        for y in range(4, h - 4, max(4, h // 5)):
            d.line([(2, y), (w - 3, y)], fill=dark)
    return trim(im, 2)


def outline_of(im: Image.Image, dark) -> Image.Image:
    w, h = im.size
    out = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, w + 1, h + 1], outline=dark)
    out.paste(im, (1, 1), im)
    return harden(out)


def build_snake(unit_id: str, n: int, dark, mid, hi, base_w: int = 14, base_h: int = 28) -> None:
    """n segments: 0=head (longest), last=tail, middle taper."""
    SPR.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        t = i / max(n - 1, 1)
        if i == 0:
            kind, w, h = "head", base_w + 4, base_h + 6
        elif i == n - 1:
            kind, w, h = "tail", max(base_w - 4, 8), max(int(base_h * 0.7), 16)
        else:
            kind = "body"
            w = max(int(base_w - t * 3), 9)
            h = max(int(base_h - t * 4), 18)
        seg = segment(w, h, dark, mid, hi, kind)
        seg.save(SPR / f"{unit_id}-segment{i}.png")
        outline_of(seg, dark).save(SPR / f"{unit_id}-segment-outline{i}.png")
    # UI body = head
    head = Image.open(SPR / f"{unit_id}-segment0.png").convert("RGBA")
    head.save(SPR / f"{unit_id}.png")
    prev = head.copy()
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR / f"{unit_id}-preview.png")
    print("snake", unit_id, n, "segs")


def main() -> None:
    SNAKE = ((40, 34, 58, 255), (100, 88, 140, 255), (190, 175, 230, 255))
    SLAG = ((52, 28, 16, 255), (140, 70, 30, 255), (230, 140, 55, 255))
    AEGIS = ((28, 52, 42, 255), (48, 110, 82, 255), (90, 210, 150, 255))
    VOID = ((18, 14, 22, 255), (55, 42, 70, 255), (160, 130, 210, 255))
    ABYSS = ((14, 10, 28, 255), (70, 40, 120, 255), (200, 160, 255, 255))
    build_snake("snake", 6, *SNAKE, 12, 26)
    build_snake("snake-t2", 8, *SNAKE, 13, 28)
    build_snake("cinder-millipede", 8, *SLAG, 14, 30)
    build_snake("payload-serpent", 9, *AEGIS, 15, 32)
    build_snake("singularity-eel", 10, *VOID, 16, 34)
    build_snake("ouroboros-prime", 14, *ABYSS, 22, 48)
    # Bahamut body also uses elongated dark segments if used as crawl alt — flying uses separate


if __name__ == "__main__":
    main()
