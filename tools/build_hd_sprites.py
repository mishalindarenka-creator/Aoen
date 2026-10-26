"""Rebuild Aoen sprites in NH / Exogenesis / Jababarium style.

Approach: take high-detail reference silhouettes from those mods, hard-remap
into Aoen palettes (multi-band metal + glow core), keep layered readability.
"""
from __future__ import annotations

import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

MOD = Path(__file__).resolve().parents[1]
SPR_U = MOD / "sprites" / "units"
SPR_B = MOD / "sprites" / "blocks"
SPR_I = MOD / "sprites" / "items"
REF = Path(os.environ.get("TEMP", ".")) / "aoen-mod-refs"

JABA = REF / "jababarium" / "sprites"
EXO = REF / "exogenesis" / "AureusStratus-ExoGenesis-8806f35" / "sprites"
NH = REF / "nh" / "sprites"

# Aoen palettes: dark, shadow, mid, hi, glow
SHELL = ((18, 16, 22), (40, 38, 48), (78, 72, 84), (168, 158, 140), (255, 210, 140))
SHELL2 = ((20, 18, 24), (48, 42, 40), (96, 82, 70), (210, 180, 120), (255, 230, 170))
DAIMYO = ((28, 8, 10), (70, 16, 20), (140, 36, 42), (220, 90, 80), (255, 180, 120))
STEEL = ((16, 20, 28), (40, 50, 62), (78, 96, 112), (170, 200, 220), (120, 230, 255))
STORM = ((16, 12, 36), (40, 32, 80), (90, 70, 150), (180, 170, 240), (220, 200, 255))
T6 = ((10, 8, 14), (36, 28, 24), (90, 60, 40), (255, 190, 80), (255, 240, 180))
T7 = ((8, 4, 12), (50, 14, 22), (130, 36, 48), (255, 100, 80), (255, 210, 150))
SNAKE = ((16, 12, 28), (48, 40, 70), (110, 90, 150), (200, 180, 230), (160, 255, 220))
SLAG = ((28, 12, 8), (80, 36, 16), (160, 80, 30), (240, 150, 60), (255, 220, 120))
AEGIS = ((10, 28, 22), (28, 70, 55), (50, 130, 100), (100, 230, 170), (180, 255, 220))
GOLD = ((16, 12, 8), (50, 40, 18), (130, 100, 40), (245, 210, 100), (255, 240, 180))
VOID = ((8, 6, 14), (32, 22, 48), (70, 50, 100), (170, 140, 220), (210, 180, 255))
NAVAL = ((10, 20, 28), (28, 55, 70), (55, 110, 130), (130, 210, 230), (180, 255, 255))
ABYSS = ((8, 4, 18), (40, 20, 70), (90, 50, 140), (200, 160, 255), (255, 200, 255))
NOCT = ((14, 10, 24), (40, 30, 70), (90, 70, 130), (180, 150, 230), (200, 170, 255))
TIDE = ((8, 24, 22), (28, 80, 70), (45, 150, 130), (100, 240, 210), (180, 255, 240))
EMBR = ((28, 10, 6), (90, 36, 14), (180, 80, 30), (255, 160, 70), (255, 220, 140))
MYTH = ((18, 20, 26), (60, 68, 80), (140, 150, 170), (230, 235, 245), (255, 255, 255))
CER = ((24, 10, 8), (80, 35, 28), (150, 70, 45), (230, 160, 90), (255, 200, 140))
AETH = ((8, 22, 28), (28, 80, 95), (50, 150, 170), (130, 240, 250), (200, 255, 255))
DARK = ((14, 14, 20), (40, 40, 52), (80, 80, 98), (200, 190, 150), (255, 230, 160))


def harden(im: Image.Image, thresh: int = 40) -> Image.Image:
    out = im.convert("RGBA")
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= thresh else (0, 0, 0, 0)
    return out


def trim(im: Image.Image, pad: int = 2) -> Image.Image:
    im = harden(im)
    bbox = im.getbbox()
    if not bbox:
        return im
    c = im.crop(bbox)
    out = Image.new("RGBA", (c.width + pad * 2, c.height + pad * 2), (0, 0, 0, 0))
    out.paste(c, (pad, pad), c)
    return out


def remap(src: Image.Image, pal, glow_sat: float = 1.0) -> Image.Image:
    """Map reference sprite into 5-band palette; bright chroma → glow."""
    src = src.convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    px, op = src.load(), out.load()
    d, sh, m, h, g = pal
    for y in range(src.height):
        for x in range(src.width):
            r, gc, b, a = px[x, y]
            if a < 40:
                continue
            lum = (r * 299 + gc * 587 + b * 114) / 1000
            mx = max(r, gc, b)
            mn = min(r, gc, b)
            sat = (mx - mn) / (mx + 1e-6)
            # glowing accents (saturated + bright)
            if sat > 0.35 and lum > 90 and glow_sat > 0:
                c = g
            elif lum > 200:
                c = h
            elif lum > 140:
                c = m if sat < 0.25 else h
            elif lum > 85:
                c = m
            elif lum > 45:
                c = sh
            else:
                c = d
            op[x, y] = (c[0], c[1], c[2], 255)
    return out


def load_ref(*candidates: str) -> Image.Image | None:
    for rel in candidates:
        p = REF / rel if not Path(rel).is_absolute() else Path(rel)
        # also try under known roots
        tries = [p, JABA / rel, EXO / rel, NH / rel, Path(rel)]
        for t in tries:
            if t.exists() and t.suffix.lower() == ".png":
                try:
                    return Image.open(t).convert("RGBA")
                except Exception:
                    pass
    return None


def find_first(root: Path, *name_parts: str) -> Image.Image | None:
    if not root.exists():
        return None
    for p in root.rglob("*.png"):
        n = p.name.lower()
        if all(part.lower() in n for part in name_parts):
            # skip heat/outline/cell if looking for body
            if any(x in n for x in ("-heat", "-outline", "-cell", "-leg", "-full")) and "body" not in name_parts:
                if "-full" in name_parts or name_parts == ("full",):
                    pass
                elif any(x in name_parts for x in ("heat", "cell", "leg")):
                    pass
                else:
                    continue
            try:
                return Image.open(p).convert("RGBA")
            except Exception:
                continue
    return None


def save_unit(stem: str, body: Image.Image, leg: Image.Image | None = None, cell_pal=None) -> None:
    body = harden(trim(body, 3))
    body.save(SPR_U / f"{stem}.png")
    prev = body.copy()
    prev.thumbnail((64, 64), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    harden(canvas, 20).save(SPR_U / f"{stem}-preview.png")
    if leg is not None:
        harden(trim(leg, 2)).save(SPR_U / f"{stem}-leg.png")
    pal = cell_pal or SHELL
    cell = Image.new("RGBA", (28, 28), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    d.ellipse([4, 4, 23, 23], fill=(*pal[3], 255), outline=(*pal[4], 255))
    d.ellipse([10, 10, 17, 17], fill=(*pal[4], 255))
    harden(cell).save(SPR_U / f"{stem}-cell.png")


def scale_to(im: Image.Image, target: int) -> Image.Image:
    w, h = im.size
    s = target / max(w, h)
    nw, nh = max(8, int(w * s)), max(8, int(h * s))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def weapon_hd(name: str, pal, style: str = "gun", scale: float = 1.0) -> None:
    """Jababarium-like multi-part weapon mounts."""
    dark, sh, mid, hi, glow = pal
    w = max(18, int(28 * scale))
    h = max(14, int(20 * scale))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # breech block
    d.rounded_rectangle([1, h // 3, w // 2, h - 2], radius=2, fill=sh, outline=hi)
    d.rectangle([3, h // 3 + 2, w // 2 - 2, h - 4], outline=mid)
    # barrel
    bw = max(4, w // 6)
    d.rectangle([w // 2 - 1, 2, w // 2 + bw, h - 3], fill=mid, outline=hi)
    d.rectangle([w // 2, 3, w // 2 + bw - 1, 6], fill=glow)
    if style == "laser":
        d.rectangle([2, h // 2 - 1, w - 3, h // 2 + 1], fill=glow)
        d.ellipse([w // 2 - 4, h // 2 - 4, w // 2 + 4, h // 2 + 4], outline=glow)
    elif style == "art":
        d.ellipse([w // 2 - 5, 1, w // 2 + 6, 12], fill=mid, outline=glow)
    elif style == "missile":
        d.ellipse([w // 2 - 3, 0, w // 2 + 3, 8], fill=glow, outline=hi)
    elif style == "rail":
        for y in range(4, h - 4, 3):
            d.line([(w // 2 - 4, y), (w // 2 + bw + 2, y)], fill=glow)
    elif style == "fang":
        d.polygon([(2, h - 2), (w // 2, 1), (w - 2, h - 2)], fill=hi, outline=glow)
    harden(trim(im, 1)).save(SPR_U / f"{name}.png")
    # parts
    for suf, size, drawer in (
        ("-breech", (max(10, w // 2), max(8, h - 4)), "box"),
        ("-barrel0", (max(6, w // 4), max(12, h)), "bar"),
        ("-barrel1", (max(6, w // 4), max(12, h)), "bar"),
        ("-muzzle", (max(8, w // 3), 8), "muzzle"),
        ("-mag", (max(10, w // 2), max(8, h // 2)), "box"),
        ("-coil", (max(10, w // 2), max(8, h // 2)), "coil"),
    ):
        ww, hh = size
        part = Image.new("RGBA", (ww, hh), (0, 0, 0, 0))
        pd = ImageDraw.Draw(part)
        if drawer == "box":
            pd.rectangle([0, 0, ww - 1, hh - 1], fill=sh, outline=hi)
            pd.rectangle([2, 2, ww - 3, hh - 3], outline=mid)
        elif drawer == "bar":
            pd.rectangle([1, 0, ww - 2, hh - 1], fill=mid, outline=hi)
            pd.rectangle([ww // 2 - 1, 0, ww // 2 + 1, 3], fill=glow)
        elif drawer == "muzzle":
            pd.polygon([(0, 4), (ww // 2, 0), (ww - 1, 4), (ww // 2, 7)], fill=glow, outline=hi)
        else:
            pd.ellipse([0, 0, ww - 1, hh - 1], outline=glow)
            pd.ellipse([2, 2, ww - 3, hh - 3], fill=mid, outline=hi)
        harden(trim(part, 1)).save(SPR_U / f"{name}{suf}.png")


def claw_hd(prefix: str, pal, n: int = 3, scale: float = 1.0) -> None:
    dark, sh, mid, hi, glow = pal
    s = max(16, int(18 * scale))
    mount = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(mount)
    d.ellipse([1, 1, s - 2, s - 2], fill=mid, outline=hi)
    d.ellipse([s // 2 - 4, s // 2 - 4, s // 2 + 4, s // 2 + 4], fill=sh, outline=glow)
    d.point((s // 2, s // 2), fill=glow)
    harden(trim(mount, 2)).save(SPR_U / f"{prefix}.png")
    specs = [(12, 16), (14, 14), (16, 12), (18, 11), (20, 10)][:n]
    for i, (bw, bh) in enumerate(specs, 1):
        w, h = max(int(bw * scale), 10), max(int(bh * scale), 9)
        seg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(seg)
        col = glow if i == n else hi if i > 2 else mid if i > 1 else sh
        sd.polygon([(1, h // 2), (3, 1), (w - 3, 2), (w - 1, h // 2), (w - 3, h - 2), (3, h - 1)], fill=col, outline=dark)
        if i == n:
            sd.polygon([(w - 7, 2), (w - 1, h // 2), (w - 7, h - 2)], fill=glow)
        # panel line
        sd.line([(4, 2), (4, h - 3)], fill=hi)
        harden(trim(seg, 2)).save(SPR_U / f"{prefix}-seg{i}.png")


def unit_from_refs(stem: str, pal, size: int, refs: list[str], leg_refs: list[str] | None = None) -> bool:
    src = None
    for r in refs:
        # path relative to REF roots
        for root in (JABA, EXO, NH):
            p = root / r if not r.startswith("sprites") else REF / r.split("sprites/", 1)[-1]
            # try direct
            cand = list(root.rglob(r)) if "/" not in r else [root / r]
            for c in cand:
                if c.exists():
                    src = Image.open(c).convert("RGBA")
                    break
            if src:
                break
        if src is None:
            # fuzzy
            parts = Path(r).stem.replace("-", " ").split()
            src = find_first(JABA, *parts) or find_first(EXO, *parts) or find_first(NH, *parts)
        if src:
            break
    if src is None:
        return False
    body = remap(scale_to(src, size), pal)
    leg = None
    if leg_refs:
        for r in leg_refs:
            lg = find_first(JABA, *Path(r).stem.replace("-", " ").split()) or find_first(NH, "leg")
            if lg:
                leg = remap(scale_to(lg, max(16, size // 3)), pal)
                break
    if leg is None:
        # procedural jointed leg
        lw, lh = max(12, size // 5), max(24, size // 2)
        leg = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        d = ImageDraw.Draw(leg)
        d.polygon([(lw // 2 - 3, 1), (lw // 2 + 3, 1), (lw - 2, lh // 3), (lw // 2 + 2, lh - 2), (lw // 2 - 2, lh - 2), (2, lh // 3)], fill=pal[2], outline=pal[3])
        d.ellipse([lw // 2 - 3, lh // 3 - 3, lw // 2 + 3, lh // 3 + 3], fill=pal[1], outline=pal[4])
    save_unit(stem, body, leg, pal)
    return True


def paint_block(size: int, pal, kind: str = "machine") -> Image.Image:
    """Dense panelled block like Jababarium/NH factories."""
    dark, sh, mid, hi, glow = pal
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = max(2, size // 18)
    d.rounded_rectangle([m, m, size - 1 - m, size - 1 - m], radius=max(2, size // 14), fill=dark, outline=hi)
    d.rounded_rectangle([m + 2, m + 2, size - 3 - m, size - 3 - m], radius=2, fill=sh, outline=mid)
    # panel grid
    step = max(6, size // 6)
    for x in range(m + 4, size - m - 4, step):
        d.line([(x, m + 4), (x, size - m - 5)], fill=dark)
    for y in range(m + 4, size - m - 4, step):
        d.line([(m + 4, y), (size - m - 5, y)], fill=dark)
    # rivets
    for x, y in ((m + 5, m + 5), (size - m - 7, m + 5), (m + 5, size - m - 7), (size - m - 7, size - m - 7)):
        d.rectangle([x, y, x + 2, y + 2], fill=hi)
    cx, cy = size // 2, size // 2
    if kind == "turret":
        # Jababarium-like layered turret: base ring, breech, multi-shade barrels, glow tips
        d.ellipse([m + 2, m + 2, size - m - 3, size - m - 3], fill=dark, outline=hi)
        d.ellipse([m + 5, m + 5, size - m - 6, size - m - 6], fill=sh, outline=mid)
        # side armor plates
        for sx in (-1, 1):
            d.polygon(
                [
                    (cx + sx * size // 5, cy - size // 8),
                    (cx + sx * size // 3, cy),
                    (cx + sx * size // 5, cy + size // 5),
                    (cx + sx * size // 8, cy + size // 10),
                ],
                fill=mid,
                outline=hi,
            )
        # breech core
        d.ellipse([cx - size // 6, cy - size // 10, cx + size // 6, cy + size // 4], fill=sh, outline=hi)
        d.ellipse([cx - 5, cy, cx + 5, cy + 10], fill=glow, outline=hi)
        # twin barrels
        bw = max(5, size // 10)
        for ox in (-size // 10, size // 10) if size >= 64 else (0,):
            d.rounded_rectangle([cx + ox - bw // 2, m + 2, cx + ox + bw // 2, cy + 4], radius=2, fill=mid, outline=hi)
            d.rectangle([cx + ox - bw // 2 + 1, m + 2, cx + ox + bw // 2 - 1, m + 8], fill=glow)
            d.rectangle([cx + ox - 1, m + 2, cx + ox + 1, cy], fill=hi)
        # greeble vents
        for i, vy in enumerate(range(cy - size // 8, cy + size // 6, max(4, size // 16))):
            d.rectangle([cx - size // 5, vy, cx - size // 5 + 3, vy + 1], fill=glow if i % 2 == 0 else hi)
    elif kind == "mend":
        d.ellipse([cx - size // 4, cy - size // 4, cx + size // 4, cy + size // 4], outline=glow)
        d.rectangle([cx - 2, cy - size // 8, cx + 2, cy + size // 8], fill=glow)
        d.rectangle([cx - size // 8, cy - 2, cx + size // 8, cy + 2], fill=glow)
    elif kind == "radar":
        d.ellipse([cx - size // 3, cy - size // 3, cx + size // 3, cy + size // 3], outline=hi)
        d.pieslice([cx - size // 3, cy - size // 3, cx + size // 3, cy + size // 3], -30, 40, fill=(*glow, 160))
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=glow)
    elif kind == "reactor":
        d.ellipse([m + 6, m + 6, size - m - 7, size - m - 7], fill=mid, outline=hi)
        d.ellipse([cx - size // 6, cy - size // 6, cx + size // 6, cy + size // 6], fill=glow, outline=hi)
        for i in range(0, 360, 45):
            import math
            rad = math.radians(i)
            d.line([(cx, cy), (cx + int(math.cos(rad) * size // 3), cy + int(math.sin(rad) * size // 3))], fill=hi, width=2)
    elif kind == "battery":
        d.rectangle([m + 8, m + 6, size - m - 9, size - m - 7], fill=mid, outline=hi)
        for i in range(3):
            y = m + 12 + i * (size // 5)
            d.rectangle([m + 12, y, size - m - 13, y + size // 10], fill=glow)
    elif kind == "conduit":
        d.rectangle([m + 4, cy - 6, size - m - 5, cy + 6], fill=mid, outline=hi)
        d.rectangle([m + 6, cy - 2, size - m - 7, cy + 2], fill=glow)
    elif kind == "wall":
        d.rectangle([m + 4, m + 4, size - m - 5, size - m - 5], fill=mid, outline=hi)
        d.line([(m + 4, cy), (size - m - 5, cy)], fill=hi)
        d.line([(cx, m + 4), (cx, size - m - 5)], fill=sh)
    else:  # machine
        d.ellipse([cx - size // 5, cy - size // 5, cx + size // 5, cy + size // 5], fill=mid, outline=hi)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=glow)
        d.rectangle([cx - 2, m + 8, cx + 2, cy - size // 5], fill=hi)
    return harden(im)


def _colorful(im: Image.Image, min_colors: int = 8) -> bool:
    visible = {px[:3] for px in im.getdata() if px[3] > 40}
    return len(visible) >= min_colors


def turret_from_ref(name: str, size_tiles: int, pal, hints: list[str]) -> None:
    px = 32 * size_tiles
    src = None
    for h in hints:
        # Prefer exact turret folder match (apex/apex.png) over huge full sprites
        folder = JABA / "blocks" / "turrets" / h
        if folder.is_dir():
            cand = folder / f"{h}.png"
            if cand.exists() and cand.stat().st_size < 40000:
                src = Image.open(cand).convert("RGBA")
                break
        src = find_first(JABA / "blocks" / "turrets", h)
        if src and src.width <= 256 and src.height <= 256:
            break
        src = None
    canvas = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    if src is not None:
        im = remap(scale_to(src, px - 6), pal)
        if _colorful(im, 6):
            canvas.alpha_composite(im, ((px - im.width) // 2, (px - im.height) // 2))
        else:
            canvas = paint_block(px, pal, "turret")
    else:
        canvas = paint_block(px, pal, "turret")
    harden(canvas).save(SPR_B / f"{name}.png")
    heat = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(heat)
    d.ellipse([px // 2 - px // 6, px // 2 - px // 6, px // 2 + px // 6, px // 2 + px // 6], fill=(255, 90, 40, 200))
    heat.save(SPR_B / f"{name}-heat.png")


def item_hd(name: str, pal) -> None:
    # try NH/jaba item then paint gem
    src = find_first(NH / "items", name.split("-")[-1]) or find_first(JABA / "items", name.split("-")[-1])
    if src:
        remap(scale_to(src, 32), pal).save(SPR_I / f"{name}.png")
        return
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dark, sh, mid, hi, glow = pal
    d.polygon([(16, 2), (28, 10), (28, 22), (16, 30), (4, 22), (4, 10)], fill=mid, outline=hi)
    d.polygon([(16, 6), (24, 12), (16, 18), (8, 12)], fill=glow)
    harden(im).save(SPR_I / f"{name}.png")


def main() -> None:
    SPR_U.mkdir(parents=True, exist_ok=True)
    SPR_B.mkdir(parents=True, exist_ok=True)
    SPR_I.mkdir(parents=True, exist_ok=True)
    random.seed(7)

    # --- units from refs ---
    units = [
        ("crab", SHELL, 48, ["brinneclaw.png", "ariel.png"], ["ariel-leg.png"]),
        ("crab-t2", SHELL2, 64, ["brinneclaw.png", "broodmother.png"], ["broodmother-leg"]),
        ("ceramtyr-daimyo", DAIMYO, 96, ["broodmother.png", "brinneclaw.png"], ["broodmother-leg"]),
        ("quake-bulwark", STEEL, 112, ["blip.png", "broodmother.png"], ["ariel-leg.png"]),
        ("storm-sovereign", STORM, 128, ["dusk.png", "apollo", "dk.png"], ["leg"]),
        ("eclipse-tyrant", T6, 180, ["dusk.png", "brinneclaw.png"], ["broodmother-leg"]),
        ("crabzilla", T7, 240, ["brinneclaw.png", "dusk.png", "broodmother.png"], ["broodmother-leg"]),
        ("boomeranger", GOLD, 48, ["asgard.png", "candlelight.png"], None),
        ("boomeranger-t2", GOLD, 64, ["asgard.png", "apollo"], None),
        ("foundry-orbiter", STEEL, 80, ["asgard.png", "dk.png"], None),
        ("aegis-walker", AEGIS, 96, ["asgard.png", "dk.png"], None),
        ("nexus-prime", GOLD, 120, ["asgard.png", "dusk.png"], None),
        ("apotheosis-core", T6, 180, ["dusk.png", "asgard.png"], None),
        ("naval", NAVAL, 48, ["aquarail.png"], None),
        ("naval-t2", NAVAL, 64, ["aquarail.png"], None),
        ("iron-reef", STEEL, 80, ["aquarail.png", "brinneclaw.png"], None),
        ("needle-skiff", NAVAL, 96, ["aquarail.png"], None),
        ("leviathan-crown", (DAIMYO[0], NAVAL[1], NAVAL[2], STORM[3], STORM[4]), 120, ["aquarail.png", "dusk.png"], None),
        ("mare-imperator", T6, 180, ["dusk.png", "aquarail.png"], None),
        ("bahamut", DAIMYO, 200, ["dusk.png", "asgard.png"], None),
    ]
    ok = 0
    for stem, pal, size, refs, legs in units:
        if unit_from_refs(stem, pal, size, refs, legs):
            ok += 1
            print("unit", stem)
        else:
            # procedural fallback HD carapace
            from build_crab_sprites import draw_crab_body, draw_leg, save_body
            save_body(stem, draw_crab_body(size, (*[(*c, 255) for c in pal[:4]],), min(7, 1 + size // 40)), draw_leg((*( (*c, 255) for c in pal[:4]),), size / 48))
            print("fallback", stem)

    # claws / weapons
    claw_hd("crab-claw", SHELL, 3, 1.2)
    claw_hd("crab-t2-claw", SHELL2, 3, 1.4)
    claw_hd("ceramtyr-daimyo-claw", DAIMYO, 4, 1.8)
    claw_hd("eclipse-tyrant-claw", T6, 4, 3.2)
    claw_hd("crabzilla-claw", T7, 5, 4.5)

    weapons = [
        ("quake-bulwark-mortar", STEEL, "art", 1.2),
        ("quake-bulwark-gun", STEEL, "gun", 1.0),
        ("quake-bulwark-flak", STEEL, "gun", 0.9),
        ("quake-bulwark-missile", STEEL, "missile", 1.0),
        ("storm-sovereign-beam", STORM, "laser", 1.3),
        ("storm-sovereign-rail", STORM, "rail", 1.2),
        ("storm-sovereign-emp", STORM, "art", 1.1),
        ("storm-sovereign-missile", STORM, "missile", 1.1),
        ("eclipse-tyrant-mortar", T6, "art", 1.6),
        ("eclipse-tyrant-beam", T6, "laser", 1.5),
        ("eclipse-tyrant-missile", T6, "missile", 1.4),
        ("eclipse-tyrant-rail", T6, "rail", 1.4),
        ("crabzilla-mortar", T7, "art", 2.0),
        ("crabzilla-beam", T7, "laser", 1.9),
        ("crabzilla-rail", T7, "rail", 1.8),
        ("crabzilla-missile", T7, "missile", 1.7),
        ("crabzilla-flak", T7, "gun", 1.5),
        ("crabzilla-nova", T7, "laser", 2.0),
        ("ceramtyr-daimyo-gun", DAIMYO, "gun", 1.2),
        ("ceramtyr-daimyo-mortar", DAIMYO, "art", 1.3),
        ("snake-fang", SNAKE, "fang", 1.0),
        ("snake-t2-fang", SNAKE, "fang", 1.1),
        ("snake-t2-spit", SNAKE, "gun", 1.0),
        ("cinder-millipede-spit", SLAG, "gun", 1.1),
        ("cinder-millipede-slag", SLAG, "art", 1.1),
        ("payload-serpent-hook", AEGIS, "gun", 1.1),
        ("payload-serpent-spit-l", AEGIS, "gun", 1.0),
        ("payload-serpent-spit-r", AEGIS, "gun", 1.0),
        ("payload-serpent-rear", AEGIS, "art", 1.1),
        ("singularity-eel-rift", VOID, "laser", 1.2),
        ("singularity-eel-bolt", VOID, "laser", 1.1),
        ("singularity-eel-spores", VOID, "gun", 1.0),
        ("ouroboros-prime-maw", ABYSS, "laser", 1.5),
        ("ouroboros-prime-bolt", ABYSS, "laser", 1.4),
        ("aegis-walker-gun", AEGIS, "gun", 1.2),
        ("aegis-walker-shotgun", AEGIS, "gun", 1.2),
        ("aegis-walker-missile", AEGIS, "missile", 1.2),
        ("nexus-prime-core", GOLD, "art", 1.3),
        ("nexus-prime-laser", GOLD, "laser", 1.3),
        ("nexus-prime-point", GOLD, "laser", 1.2),
        ("apotheosis-core-nova", T6, "laser", 1.6),
        ("apotheosis-core-batteries", T6, "gun", 1.5),
        ("apotheosis-core-rail", T6, "rail", 1.5),
        ("naval-cannon", NAVAL, "gun", 1.0),
        ("naval-torpedo", NAVAL, "missile", 1.0),
        ("naval-t2-cannon", NAVAL, "gun", 1.1),
        ("naval-t2-shell", NAVAL, "art", 1.1),
        ("iron-reef-battery", STEEL, "art", 1.2),
        ("needle-skiff-rack", NAVAL, "gun", 1.2),
        ("needle-skiff-rack-l", NAVAL, "gun", 1.2),
        ("needle-skiff-rack-r", NAVAL, "gun", 1.2),
        ("needle-skiff-ciws", NAVAL, "gun", 1.0),
        ("leviathan-crown-main", STORM, "art", 1.4),
        ("leviathan-crown-flak", NAVAL, "gun", 1.2),
        ("leviathan-crown-beam", STORM, "laser", 1.3),
        ("leviathan-crown-torpedo", NAVAL, "missile", 1.2),
        ("mare-imperator-main", T6, "art", 1.7),
        ("mare-imperator-ciws", T6, "gun", 1.4),
        ("mare-imperator-beam", T6, "laser", 1.6),
        ("mare-imperator-missile", T6, "missile", 1.5),
        ("foundry-orbiter-laser", STEEL, "laser", 1.2),
    ]
    for wn, pal, st, sc in weapons:
        weapon_hd(wn, pal, st, sc)

    # orbs
    for lab in "abc":
        weapon_hd(f"boomeranger-orb-{lab}", GOLD, "art", 0.7)
    for lab in "abcde":
        weapon_hd(f"boomeranger-t2-orb-{lab}", GOLD, "art", 0.75)
        weapon_hd(f"foundry-orbiter-orb-{lab}", STEEL, "art", 0.7)

    # serpents via existing builder then we're done for snakes
    try:
        from build_snake_sprites import main as build_snakes
        build_snakes()
    except Exception as e:
        print("snake skip", e)
    try:
        from build_bahamut_sprites import main as build_bahamut
        build_bahamut()
    except Exception as e:
        print("bahamut skip", e)

    # --- items ---
    for name, pal in [
        ("void-shard", VOID), ("ceramite", CER), ("aether-dust", AETH),
        ("nocturne-ore", NOCT), ("abyssal-quartz", (NOCT[0], STEEL[1], AETH[2], AETH[3], AETH[4])),
        ("tide-coral", TIDE), ("ember-slag", EMBR), ("pale-mythril", MYTH),
        ("nocturne-plate", NOCT), ("abyssal-alloy", AETH), ("tide-composite", TIDE),
    ]:
        item_hd(name, pal)

    # --- blocks ---
    turrets = [
        ("shard-turret", 1, VOID, ["avangard", "apex"]),
        ("wave-scatter", 2, AETH, ["cascade", "avangard"]),
        ("eclipse-beam", 2, GOLD, ["chronos", "apex"]),
        ("tyrant-rail", 3, CER, ["entropy", "apex"]),
        ("void-flak", 2, VOID, ["avangard"]),
        ("aether-missile", 3, AETH, ["cascade"]),
        ("ceramite-howitzer", 3, CER, ["entropy", "abbys"]),
        ("singularity-lance", 4, GOLD, ["abbys", "apex"]),
        ("abyss-fortress", 4, DAIMYO, ["abbys"]),
        ("storm-battery", 3, STEEL, ["cascade"]),
        ("nocturne-bolt", 2, NOCT, ["avangard", "apex"]),
        ("tide-pulse", 3, TIDE, ["cascade"]),
        ("crab-howitzer", 4, T7, ["abbys", "entropy"]),
    ]
    for name, sz, pal, hints in turrets:
        turret_from_ref(name, sz, pal, hints)

    def save_b(name, size, pal, kind="machine"):
        paint_block(size, pal, kind).save(SPR_B / f"{name}.png")

    for name, sz, pal, kind in [
        ("void-smelter", 64, VOID, "machine"),
        ("ceramite-forge", 96, CER, "machine"),
        ("aether-refinery", 96, AETH, "machine"),
        ("nocturne-smelter", 64, NOCT, "machine"),
        ("abyssal-foundry", 96, AETH, "machine"),
        ("tide-kiln", 96, TIDE, "machine"),
        ("pale-foundry", 96, MYTH, "machine"),
        ("void-compressor", 64, VOID, "machine"),
        ("ceramite-crucible", 64, CER, "machine"),
        ("dark-drill", 64, DARK, "machine"),
        ("void-drill", 96, VOID, "machine"),
        ("mythril-drill", 96, MYTH, "machine"),
        ("dark-generator", 32, GOLD, "reactor"),
        ("ember-generator", 64, EMBR, "reactor"),
        ("aether-reactor", 96, AETH, "reactor"),
        ("mythril-reactor", 128, MYTH, "reactor"),
        ("dark-battery", 32, AETH, "battery"),
        ("nocturne-battery", 64, NOCT, "battery"),
        ("tide-mender", 64, TIDE, "mend"),
        ("abyss-radar", 64, AETH, "radar"),
        ("tide-conduit", 32, TIDE, "conduit"),
        ("void-unloader", 32, VOID, "machine"),
        ("ceramite-wall", 32, CER, "wall"),
        ("ceramite-wall-large", 64, CER, "wall"),
        ("nocturne-wall", 32, NOCT, "wall"),
        ("nocturne-wall-large", 64, NOCT, "wall"),
        ("abyssal-wall", 32, AETH, "wall"),
        ("abyssal-wall-large", 64, AETH, "wall"),
        ("tide-wall", 32, TIDE, "wall"),
        ("tide-wall-large", 64, TIDE, "wall"),
        ("mythril-wall", 32, MYTH, "wall"),
        ("mythril-wall-large", 64, MYTH, "wall"),
        ("ember-wall", 32, EMBR, "wall"),
        ("ember-wall-large", 64, EMBR, "wall"),
        ("dark-junction", 32, DARK, "machine"),
        ("dark-router", 32, DARK, "machine"),
        ("dark-bridge", 32, DARK, "machine"),
        ("dark-overflow", 32, DARK, "machine"),
        ("dark-sorter", 32, DARK, "machine"),
    ]:
        save_b(name, sz, pal, kind)
        if kind == "machine" and name.endswith(("smelter", "forge", "foundry", "kiln", "refinery", "crucible", "compressor")):
            top = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
            td = ImageDraw.Draw(top)
            td.ellipse([sz // 2 - 8, sz // 2 - 8, sz // 2 + 8, sz // 2 + 8], fill=(*pal[4], 200))
            top.save(SPR_B / f"{name}-top.png")

    # conveyors — detailed frames
    for stem, pal in (("dark-conveyor", DARK), ("dark-conveyor-armored", CER)):
        for a in range(5):
            for b in range(4):
                im = paint_block(32, pal, "conduit")
                d = ImageDraw.Draw(im)
                d.polygon([(10, 10), (22, 16), (10, 22)], fill=pal[4])
                im.save(SPR_B / f"{stem}-{a}-{b}.png")
        paint_block(32, pal, "conduit").save(SPR_B / f"{stem}.png")

    # ores
    for stem, pal in [
        ("ore-void-shard", VOID), ("ore-ceramite", CER), ("ore-nocturne", NOCT),
        ("ore-abyssal-quartz", AETH), ("ore-tide-coral", TIDE), ("ore-ember-slag", EMBR),
        ("ore-pale-mythril", MYTH),
    ]:
        for i in range(1, 4):
            im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            for _ in range(10):
                x, y = random.randint(2, 24), random.randint(2, 24)
                d.ellipse([x, y, x + 6, y + 5], fill=pal[2], outline=pal[4])
            harden(im).save(SPR_B / f"{stem}{i}.png")

    # unit factories — remap NH/jaba constructors if present
    from build_block_sprites import main as build_blocks
    build_blocks()

    # nuke double prefix
    for folder in (SPR_U, SPR_B, SPR_I):
        for p in list(folder.glob("aoen-*.png")):
            p.unlink()

    print("HD sprites done; units ok", ok, "unit pngs", len(list(SPR_U.glob("*.png"))), "blocks", len(list(SPR_B.glob("*.png"))))


if __name__ == "__main__":
    main()
