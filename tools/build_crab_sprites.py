"""Procedural crab-line sprites — real carapace silhouette (not atrax tint).

Top-down Mindustry style: hard alpha, 3–4 color bands, readable claws/eyes.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

MOD = Path(__file__).resolve().parents[1]
SPR = MOD / "sprites" / "units"

SHELL = ((36, 34, 40, 255), (68, 64, 72, 255), (160, 150, 130, 255), (230, 210, 160, 255))
SHELL2 = ((40, 36, 44, 255), (90, 78, 70, 255), (200, 170, 110, 255), (255, 230, 170, 255))
DAIMYO = ((48, 12, 14, 255), (110, 28, 32, 255), (210, 70, 70, 255), (255, 160, 120, 255))
STEEL = ((40, 46, 56, 255), (78, 90, 104, 255), (170, 190, 210, 255), (230, 245, 255, 255))
STORM = ((36, 32, 72, 255), (78, 68, 140, 255), (170, 160, 240, 255), (220, 210, 255, 255))
T6 = ((16, 14, 20, 255), (70, 55, 40, 255), (255, 200, 90, 255), (255, 240, 180, 255))
T7 = ((12, 8, 18, 255), (90, 28, 40, 255), (255, 90, 70, 255), (255, 210, 140, 255))


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
    return out


def save_body(stem: str, body: Image.Image, leg: Image.Image | None = None) -> None:
    body = harden(trim(body, 4))
    body.save(SPR / f"{stem}.png")
    prev = body.copy()
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR / f"{stem}-preview.png")
    if leg is not None:
        harden(trim(leg, 2)).save(SPR / f"{stem}-leg.png")
    # cell glow
    cell = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    d.ellipse([4, 4, 19, 19], fill=(255, 211, 127, 255), outline=(255, 240, 200, 255))
    harden(cell).save(SPR / f"{stem}-cell.png")


def draw_leg(pal, scale: float = 1.0) -> Image.Image:
    dark, mid, hi, _ = pal
    w, h = max(10, int(12 * scale)), max(22, int(28 * scale))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # jointed leg: thick base → taper tip
    d.polygon(
        [(w // 2 - 3, 1), (w // 2 + 3, 1), (w - 2, h // 3), (w // 2 + 2, h - 2), (w // 2 - 2, h - 2), (2, h // 3)],
        fill=mid,
        outline=hi,
    )
    d.ellipse([w // 2 - 3, h // 3 - 3, w // 2 + 3, h // 3 + 3], fill=dark, outline=hi)
    d.rectangle([w // 2 - 1, h - 6, w // 2 + 1, h - 1], fill=hi)
    return im


def draw_crab_body(size: int, pal, tier: int = 1) -> Image.Image:
    """Top-down crab: wide carapace, forward eyes, rear abdomen, side armor."""
    dark, mid, hi, glow = pal
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = size // 2, size // 2 + size // 16

    # rear abdomen
    aw, ah = size // 3, size // 5
    d.ellipse([cx - aw // 2, cy + size // 8, cx + aw // 2, cy + size // 8 + ah], fill=dark, outline=mid)

    # main carapace (wide oval)
    bw, bh = int(size * 0.72), int(size * 0.48)
    d.ellipse([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2], fill=mid, outline=hi)
    # inner plate
    d.ellipse(
        [cx - bw // 2 + 4, cy - bh // 2 + 3, cx + bw // 2 - 4, cy + bh // 2 - 3],
        outline=dark,
    )
    # center ridge
    d.line([(cx, cy - bh // 2 + 4), (cx, cy + bh // 2 - 4)], fill=hi, width=max(1, size // 48))
    # side armor lobes
    for sx in (-1, 1):
        d.ellipse(
            [cx + sx * bw // 3 - size // 10, cy - size // 12, cx + sx * bw // 3 + size // 10, cy + size // 8],
            fill=dark,
            outline=hi,
        )

    # forward eyes / sensors
    eye_y = cy - bh // 2 + size // 14
    for sx in (-1, 1):
        ex = cx + sx * size // 8
        d.ellipse([ex - 3, eye_y - 3, ex + 3, eye_y + 3], fill=dark, outline=glow)
        d.point((ex, eye_y), fill=glow)

    # mouth / front notch
    d.polygon(
        [(cx - size // 12, cy - bh // 2 + 2), (cx, cy - bh // 2 - size // 20), (cx + size // 12, cy - bh // 2 + 2)],
        fill=dark,
        outline=hi,
    )

    # tier badges
    if tier >= 3:
        d.rectangle([cx - 4, cy - 2, cx + 4, cy + 4], outline=glow)
    if tier >= 5:
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=glow)
        d.point((cx, cy), fill=glow)
    if tier >= 6:
        # crown spikes
        for i, ox in enumerate((-size // 6, 0, size // 6)):
            d.polygon(
                [(cx + ox - 3, cy - bh // 2 + 6), (cx + ox, cy - bh // 2 - size // 16), (cx + ox + 3, cy - bh // 2 + 6)],
                fill=glow,
                outline=hi,
            )
    if tier >= 7:
        # massive shell plates + glow core
        d.ellipse([cx - size // 5, cy - size // 8, cx + size // 5, cy + size // 8], outline=glow)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=glow, outline=hi)
        # dual horn
        for sx in (-1, 1):
            d.polygon(
                [
                    (cx + sx * size // 5, cy - bh // 3),
                    (cx + sx * size // 4, cy - bh // 2 - size // 10),
                    (cx + sx * size // 7, cy - bh // 3 + 4),
                ],
                fill=hi,
                outline=glow,
            )

    return im


def claw_set(prefix: str, scale: float, pal, n: int = 3, red: bool = False) -> None:
    dark, mid, hi, glow = pal
    if red:
        dark, mid, hi, glow = (120, 20, 28, 255), (190, 45, 50, 255), (255, 120, 90, 255), (255, 200, 140, 255)
    s = max(14, int(16 * scale))
    mount = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(mount)
    # pincer base
    d.ellipse([1, 1, s - 2, s - 2], fill=mid, outline=hi)
    d.ellipse([s // 2 - 3, s // 2 - 3, s // 2 + 3, s // 2 + 3], fill=dark, outline=glow)
    harden(trim(mount, 2)).save(SPR / f"{prefix}.png")

    specs = [(11, 16), (13, 13), (15, 11), (17, 10), (18, 10)][:n]
    for i, (bw, bh) in enumerate(specs, 1):
        w, h = max(int(bw * scale), 9), max(int(bh * scale), 8)
        seg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(seg)
        col = glow if i == n else mid if i > 1 else dark
        # claw segment shape
        sd.polygon([(1, h // 2), (3, 1), (w - 2, 2), (w - 1, h // 2), (w - 2, h - 2), (3, h - 1)], fill=col, outline=dark)
        if i == n:
            # tip
            sd.polygon([(w - 6, 2), (w - 1, h // 2), (w - 6, h - 2)], fill=glow)
        harden(trim(seg, 2)).save(SPR / f"{prefix}-seg{i}.png")


def weapon_box(name: str, w: int, h: int, pal, style: str = "gun") -> None:
    dark, mid, hi, glow = pal
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 2, w - 2, h - 2], radius=2, fill=dark, outline=hi)
    d.rectangle([3, 4, w - 4, h - 4], outline=mid)
    if style == "gun":
        d.rectangle([w // 2 - 2, 0, w // 2 + 2, h // 2], fill=hi)
        d.rectangle([w // 2 - 1, 0, w // 2 + 1, 3], fill=glow)
    elif style == "laser":
        d.rectangle([2, h // 2 - 1, w - 3, h // 2 + 1], fill=glow)
        d.ellipse([w // 2 - 4, h // 2 - 4, w // 2 + 4, h // 2 + 4], outline=hi)
    elif style == "art":
        d.ellipse([w // 2 - 5, 1, w // 2 + 5, 11], fill=mid, outline=hi)
        d.rectangle([w // 2 - 3, 8, w // 2 + 3, h - 3], fill=hi)
    elif style == "missile":
        d.ellipse([w // 2 - 3, 0, w // 2 + 3, 8], fill=glow)
        d.rectangle([w // 2 - 2, 6, w // 2 + 2, h - 2], fill=mid, outline=hi)
    elif style == "rail":
        d.rectangle([w // 2 - 3, 0, w // 2 + 3, h - 2], fill=mid, outline=hi)
        for y in range(4, h - 4, 4):
            d.line([(2, y), (w - 3, y)], fill=glow)
    harden(trim(im, 2)).save(SPR / f"{name}.png")
    # jababarium parts
    breech = Image.new("RGBA", (max(w - 2, 10), max(h - 2, 8)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(breech)
    bd.rectangle([0, 1, breech.width - 1, breech.height - 2], fill=dark, outline=hi)
    harden(trim(breech, 1)).save(SPR / f"{name}-breech.png")
    for bi in range(2):
        bw, bh = max(6, w // 4), max(12, h)
        barrel = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        bld = ImageDraw.Draw(barrel)
        bld.rectangle([1, 0, bw - 2, bh - 1], fill=mid, outline=hi)
        bld.rectangle([bw // 2 - 1, 0, bw // 2 + 1, 3], fill=glow)
        harden(trim(barrel, 1)).save(SPR / f"{name}-barrel{bi}.png")
    muzzle = Image.new("RGBA", (max(w // 2, 8), 8), (0, 0, 0, 0))
    md = ImageDraw.Draw(muzzle)
    md.polygon([(0, 4), (muzzle.width // 2, 0), (muzzle.width - 1, 4), (muzzle.width // 2, 7)], fill=glow)
    harden(trim(muzzle, 1)).save(SPR / f"{name}-muzzle.png")
    for extra in ("-mag", "-coil"):
        ex = Image.new("RGBA", (max(10, w // 2), max(8, h // 2)), (0, 0, 0, 0))
        ed = ImageDraw.Draw(ex)
        ed.rectangle([0, 0, ex.width - 1, ex.height - 1], fill=mid, outline=glow)
        harden(trim(ex, 1)).save(SPR / f"{name}{extra}.png")


def build_unit(stem: str, size: int, pal, tier: int, claws: list[tuple[str, float, int, bool]], weapons=None) -> None:
    body = draw_crab_body(size, pal, tier)
    leg = draw_leg(pal, max(0.9, size / 48))
    save_body(stem, body, leg)
    for prefix, sc, n, red in claws:
        claw_set(prefix, sc, pal, n=n, red=red)
    for wname, style, ww, wh in weapons or []:
        weapon_box(wname, ww, wh, pal, style)


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)

    build_unit("crab", 40, SHELL, 1, [("crab-claw", 1.15, 3, False)])
    build_unit("crab-t2", 52, SHELL2, 2, [("crab-t2-claw", 1.35, 3, False)])
    build_unit(
        "ceramtyr-daimyo",
        72,
        DAIMYO,
        3,
        [("ceramtyr-daimyo-claw", 1.7, 4, True)],
        [("ceramtyr-daimyo-gun", "gun", 22, 14)],
    )
    build_unit(
        "quake-bulwark",
        88,
        STEEL,
        4,
        [],
        [
            ("quake-bulwark-mortar", "art", 26, 16),
            ("quake-bulwark-gun", "gun", 22, 14),
            ("quake-bulwark-flak", "gun", 20, 12),
            ("quake-bulwark-missile", "missile", 22, 14),
        ],
    )
    build_unit(
        "storm-sovereign",
        104,
        STORM,
        5,
        [],
        [
            ("storm-sovereign-beam", "laser", 28, 16),
            ("storm-sovereign-rail", "rail", 26, 14),
            ("storm-sovereign-emp", "art", 24, 14),
            ("storm-sovereign-missile", "missile", 24, 14),
        ],
    )
    build_unit(
        "eclipse-tyrant",
        160,
        T6,
        6,
        [("eclipse-tyrant-claw", 3.4, 4, True)],
        [
            ("eclipse-tyrant-mortar", "art", 32, 18),
            ("eclipse-tyrant-beam", "laser", 30, 16),
            ("eclipse-tyrant-missile", "missile", 28, 16),
            ("eclipse-tyrant-rail", "rail", 28, 16),
        ],
    )
    # T7 Crabzilla — kaiju carapace
    build_unit(
        "crabzilla",
        220,
        T7,
        7,
        [("crabzilla-claw", 4.6, 5, True)],
        [
            ("crabzilla-mortar", "art", 40, 22),
            ("crabzilla-beam", "laser", 36, 18),
            ("crabzilla-rail", "rail", 34, 18),
            ("crabzilla-missile", "missile", 32, 18),
            ("crabzilla-flak", "gun", 28, 16),
            ("crabzilla-nova", "laser", 38, 20),
        ],
    )
    print("crab sprites OK", len(list(SPR.glob("crab*.png"))) + len(list(SPR.glob("eclipse*.png"))) + len(list(SPR.glob("*sovereign*.png"))))


if __name__ == "__main__":
    main()
