"""Aoen unit sprites — unified clean style (leviathan-crown reference).

Rules:
- vanilla top-down base + hard 3-color tint
- alpha only 0 or 255 (no soft smear)
- no multi-layer composites / masks / spike scribbles
- shared accent language: center panel + small hard highlights
"""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

MOD = Path(__file__).resolve().parents[1]
SPR = MOD / "sprites" / "units"
TMP = Path(os.environ.get("TEMP", ".")) / "mindustry-sprites"
BASE = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/units"

# Shared Aoen palettes (dark / mid / hi) — muted metal like leviathan
SHELL = ((36, 34, 40, 255), (68, 64, 72, 255), (160, 150, 130, 255))
DAIMYO = ((48, 12, 14, 255), (110, 28, 32, 255), (210, 70, 70, 255))
STEEL = ((40, 46, 56, 255), (78, 90, 104, 255), (170, 190, 210, 255))
STORM = ((36, 32, 72, 255), (78, 68, 140, 255), (170, 160, 240, 255))
SNAKE = ((40, 34, 58, 255), (100, 88, 140, 255), (190, 175, 230, 255))
SLAG = ((52, 28, 16, 255), (140, 70, 30, 255), (230, 140, 55, 255))
AEGIS = ((28, 52, 42, 255), (48, 110, 82, 255), (90, 210, 150, 255))
GOLD = ((28, 22, 14, 255), (120, 95, 35, 255), (245, 205, 90, 255))
VOID = ((18, 14, 22, 255), (55, 42, 70, 255), (160, 130, 210, 255))
NAVAL = ((28, 44, 58, 255), (52, 88, 112, 255), (130, 195, 215, 255))
T6 = ((16, 14, 20, 255), (70, 55, 40, 255), (255, 200, 90, 255))
ABYSS = ((14, 10, 28, 255), (70, 40, 120, 255), (200, 160, 255, 255))

REFS = (
    "alpha-cell.png", "arkyid.png", "atrax.png", "atrax-leg.png",
    "dagger.png", "dagger-leg.png", "mace.png", "fortress.png", "scepter.png", "reign.png",
    "risso.png", "minke.png", "bryde.png", "sei.png", "omura.png",
    "toxopid.png", "spiroct.png",
)


def load(name: str) -> Image.Image:
    return Image.open(TMP / name).convert("RGBA")


def ensure_refs() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    for name in REFS:
        dest = TMP / name
        if dest.exists() and dest.stat().st_size > 100:
            continue
        try:
            urllib.request.urlretrieve(f"{BASE}/{name}", dest)
        except Exception as exc:
            print("skip", name, exc)


def harden(im: Image.Image) -> Image.Image:
    """Force binary alpha — kills smear / fringe pixels."""
    out = im.convert("RGBA")
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 128 else (0, 0, 0, 0)
    return out


def trim(im: Image.Image, pad: int = 4) -> Image.Image:
    im = harden(im)
    bbox = im.getbbox()
    if not bbox:
        return im
    cropped = im.crop(bbox)
    out = Image.new("RGBA", (cropped.width + pad * 2, cropped.height + pad * 2), (0, 0, 0, 0))
    out.paste(cropped, (pad, pad), cropped)
    return out


def tint_hard(src: Image.Image, dark, mid, hi) -> Image.Image:
    """3-band hard tint preserving vanilla silhouette."""
    src = harden(src)
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    px, op = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            lum = (r * 299 + g * 587 + b * 114) / 1000
            c = hi if lum > 170 else mid if lum > 85 else dark
            op[x, y] = (c[0], c[1], c[2], 255)
    return out


def scale_nn(src: Image.Image, scale: float) -> Image.Image:
    w = max(8, int(round(src.width * scale)))
    h = max(8, int(round(src.height * scale)))
    return src.resize((w, h), Image.Resampling.NEAREST)


def accent_panel(im: Image.Image, hi, kind: str = "ship") -> Image.Image:
    """Minimal hard accent like leviathan center line / mech cockpit."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    cx, cy = im.width // 2, im.height // 2
    if kind == "ship":
        d.line([(cx, 3), (cx, im.height - 4)], fill=hi, width=1)
        # small hard deck block
        d.rectangle([cx - 3, cy - 4, cx + 3, cy + 6], outline=hi)
    elif kind == "mech":
        d.rectangle([cx - 4, cy - 3, cx + 4, cy + 5], outline=hi)
        d.point((cx, cy), fill=hi)
    elif kind == "legs":
        d.rectangle([cx - 3, cy - 2, cx + 3, cy + 4], outline=hi)
    return im


def body_save(unit_id: str, body: Image.Image, leg: Image.Image | None = None, cell: Image.Image | None = None) -> None:
    body = harden(trim(body, 4))
    body.save(SPR / f"{unit_id}.png")
    preview = body.copy()
    preview.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(preview, ((64 - preview.width) // 2, (64 - preview.height) // 2), preview)
    canvas.save(SPR / f"{unit_id}-preview.png")
    if leg is not None:
        harden(trim(leg, 2)).save(SPR / f"{unit_id}-leg.png")
    if cell is not None:
        c = harden(cell.copy())
        c.thumbnail((32, 32), Image.Resampling.NEAREST)
        harden(c).save(SPR / f"{unit_id}-cell.png")


def weapon_mount(name: str, w: int, h: int, dark, mid, hi, style: str = "gun", parts: bool = False) -> None:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 2, w - 2, h - 2], fill=dark, outline=hi)
    d.rectangle([2, 3, w - 3, h - 3], outline=mid)
    if style == "gun":
        d.rectangle([w // 2 - 2, 0, w // 2 + 2, h // 2], fill=hi)
    elif style == "laser":
        d.rectangle([2, h // 2 - 1, w - 3, h // 2 + 1], fill=hi)
    elif style == "art":
        d.rectangle([w // 2 - 3, 1, w // 2 + 3, 7], fill=hi)
    elif style == "missile":
        d.ellipse([w // 2 - 3, 0, w // 2 + 3, 8], fill=hi)
        d.rectangle([w // 2 - 2, 6, w // 2 + 2, h - 3], fill=mid)
    elif style == "fang":
        d.polygon([(2, h - 2), (w // 2, 1), (w - 3, h - 2)], fill=hi, outline=dark)
    harden(trim(im, 2)).save(SPR / f"{name}.png")
    if parts:
        # jababarium-style breech / barrel / muzzle stack
        breech = Image.new("RGBA", (max(w - 4, 10), max(h - 4, 8)), (0, 0, 0, 0))
        bd = ImageDraw.Draw(breech)
        bd.rectangle([0, 1, breech.width - 1, breech.height - 2], fill=dark, outline=hi)
        harden(trim(breech, 1)).save(SPR / f"{name}-breech.png")
        for bi in range(2):
            bw, bh = max(6, w // 4), max(12, h)
            barrel = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
            bld = ImageDraw.Draw(barrel)
            bld.rectangle([1, 0, bw - 2, bh - 1], fill=mid, outline=hi)
            bld.rectangle([bw // 2 - 1, 0, bw // 2 + 1, 3], fill=hi)
            harden(trim(barrel, 1)).save(SPR / f"{name}-barrel{bi}.png")
        muzzle = Image.new("RGBA", (max(w // 2, 8), 8), (0, 0, 0, 0))
        md = ImageDraw.Draw(muzzle)
        md.polygon([(0, 4), (muzzle.width // 2, 0), (muzzle.width - 1, 4), (muzzle.width // 2, 7)], fill=hi)
        harden(trim(muzzle, 1)).save(SPR / f"{name}-muzzle.png")


def build_from_vanilla(unit_id: str, van: str, scale: float, palette, kind: str, weapons=None, leg_van: str | None = None) -> None:
    dark, mid, hi = palette
    body = accent_panel(tint_hard(scale_nn(load(f"{van}.png"), scale), dark, mid, hi), hi, kind)
    leg = None
    cell = None
    if kind in ("mech", "legs"):
        lv = leg_van or ("atrax-leg.png" if kind == "legs" else "dagger-leg.png")
        leg = tint_hard(scale_nn(load(lv), max(scale * 0.95, 1.0)), dark, mid, hi)
        cell = tint_hard(load("alpha-cell.png"), dark, mid, hi)
    body_save(unit_id, body, leg, cell)
    for wname, style in weapons or []:
        weapon_mount(wname, max(18, int(22 * min(scale, 2.2))), max(12, int(14 * min(scale, 2.2))), dark, mid, hi, style)


def claw_clean(prefix: str, scale: float, red: bool = False, n: int = 3) -> None:
    """Hard-edge claw mounts/segments — no rotated soft fringes."""
    dark = (150, 30, 34, 255) if red else (100, 85, 75, 255)
    mid = (190, 50, 48, 255) if red else (160, 135, 105, 255)
    hi = (240, 90, 70, 255) if red else (230, 200, 140, 255)
    # mount
    s = max(12, int(14 * scale))
    mount = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(mount)
    d.rectangle([1, 1, s - 2, s - 2], fill=mid, outline=hi)
    d.rectangle([s // 2 - 2, s // 2 - 2, s // 2 + 2, s // 2 + 2], fill=hi)
    harden(trim(mount, 2)).save(SPR / f"{prefix}.png")
    specs = [(10, 14), (12, 11), (14, 9), (15, 9)][:n]
    for i, (bw, bh) in enumerate(specs, 1):
        w, h = max(int(bw * scale), 8), max(int(bh * scale), 7)
        seg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(seg)
        col = hi if i == n else mid if i > 1 else dark
        sd.rectangle([0, 1, w - 1, h - 2], fill=col, outline=dark)
        if i == n:
            sd.polygon([(w - 5, 1), (w - 1, h // 2), (w - 5, h - 2)], fill=hi)
        harden(trim(seg, 2)).save(SPR / f"{prefix}-seg{i}.png")


def build_snake(unit_id: str, segments: int, palette, scale: float = 1.4) -> None:
    dark, mid, hi = palette
    bw, bh = max(int(36 * scale), 28), max(int(12 * scale), 10)
    head = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(head)
    d.rectangle([0, 1, bw - 1, bh - 2], fill=mid, outline=hi)
    d.rectangle([2, 3, bw // 3, bh - 4], fill=dark)
    d.rectangle([bw // 4, bh // 3, bw // 4 + 2, bh // 3 + 2], fill=hi)
    harden(trim(head, 3)).save(SPR / f"{unit_id}.png")
    for i in range(segments):
        w = max(bw - i * 2, int(20 * scale))
        h = max(bh - i // 3, int(9 * scale))
        seg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(seg)
        c = mid if i % 2 == 0 else dark
        sd.rectangle([0, 1, w - 1, h - 2], fill=c, outline=hi if i == 0 else dark)
        harden(trim(seg, 2)).save(SPR / f"{unit_id}-segment{i}.png")
        # outline: solid dark ring, still hard alpha
        ol = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
        od = ImageDraw.Draw(ol)
        od.rectangle([0, 0, w + 1, h + 1], outline=dark)
        od.rectangle([1, 1, w, h], fill=c)
        harden(trim(ol, 1)).save(SPR / f"{unit_id}-segment-outline{i}.png")
    prev = harden(trim(head, 3))
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR / f"{unit_id}-preview.png")


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    ensure_refs()
    for p in list(SPR.glob("aoen-*.png")):
        p.unlink()

    # --- Crab line: clean legs silhouette + hard claws ---
    build_from_vanilla("crab", "atrax", 1.25, SHELL, "legs", [("crab-claw", "gun")])
    claw_clean("crab-claw", 1.1, n=3)
    build_from_vanilla("crab-t2", "spiroct", 1.45, (SHELL[0], SHELL[1], (220, 190, 120, 255)), "legs", [("crab-t2-claw", "gun")])
    claw_clean("crab-t2-claw", 1.25, n=3)
    build_from_vanilla("ceramtyr-daimyo", "arkyid", 1.7, DAIMYO, "legs", [("ceramtyr-daimyo-claw", "gun")])
    claw_clean("ceramtyr-daimyo-claw", 1.6, red=True, n=4)
    build_from_vanilla(
        "quake-bulwark", "arkyid", 1.85, STEEL, "legs",
        [("quake-bulwark-mortar", "art"), ("quake-bulwark-gun", "gun"), ("quake-bulwark-flak", "gun"), ("quake-bulwark-missile", "gun")],
    )
    build_from_vanilla(
        "storm-sovereign", "toxopid", 2.1, STORM, "legs",
        [("storm-sovereign-beam", "laser"), ("storm-sovereign-rail", "laser"), ("storm-sovereign-emp", "art")],
    )
    for wn, st in (("storm-sovereign-beam", "laser"), ("storm-sovereign-rail", "laser"), ("storm-sovereign-emp", "art")):
        weapon_mount(wn, 26, 16, STORM[0], STORM[1], STORM[2], st, parts=True)
    build_from_vanilla("eclipse-tyrant", "toxopid", 4.4, T6, "legs", [("eclipse-tyrant-mortar", "art"), ("eclipse-tyrant-beam", "laser")])
    claw_clean("eclipse-tyrant-claw", 3.2, red=True, n=4)

    # --- Crawl: elongated Y-forward segments (dedicated snake system) ---
    from build_snake_sprites import main as build_snakes

    build_snakes()
    for n, pal, st in [
        ("snake-fang", SNAKE, "fang"),
        ("snake-t2-fang", SNAKE, "fang"),
        ("snake-t2-spit", SNAKE, "gun"),
        ("cinder-millipede-spit", SLAG, "gun"),
        ("cinder-millipede-slag", SLAG, "art"),
        ("payload-serpent-hook", AEGIS, "gun"),
        ("payload-serpent-spit-l", AEGIS, "gun"),
        ("payload-serpent-spit-r", AEGIS, "gun"),
        ("payload-serpent-rear", AEGIS, "art"),
        ("singularity-eel-rift", VOID, "laser"),
        ("singularity-eel-bolt", VOID, "laser"),
        ("singularity-eel-spores", VOID, "gun"),
        ("ouroboros-prime-maw", ABYSS, "laser"),
        ("ouroboros-prime-bolt", ABYSS, "laser"),
    ]:
        weapon_mount(n, 22, 14, pal[0], pal[1], pal[2], st, parts=(st in ("gun", "laser", "art")))

    # --- Proto Bahamut (GBF) ---
    from build_bahamut_sprites import main as build_bahamut

    build_bahamut()

    # --- Jababarium-style multi-part weapons ---
    from build_weapon_sprites import main as build_weapons

    build_weapons()

    # --- Mech ---
    build_from_vanilla("boomeranger", "dagger", 1.35, GOLD, "mech")
    for lab in "abc":
        weapon_mount(f"boomeranger-orb-{lab}", 14, 14, GOLD[0], GOLD[1], GOLD[2], "art")
    build_from_vanilla("boomeranger-t2", "mace", 1.55, GOLD, "mech")
    for lab in "abcde":
        weapon_mount(f"boomeranger-t2-orb-{lab}", 15, 15, GOLD[0], GOLD[1], GOLD[2], "art")
    build_from_vanilla("foundry-orbiter", "fortress", 1.75, STEEL, "mech", [("foundry-orbiter-laser", "laser")])
    for lab in "abcde":
        weapon_mount(f"foundry-orbiter-orb-{lab}", 14, 14, STEEL[0], GOLD[1], SLAG[2], "art")
    build_from_vanilla(
        "aegis-walker", "scepter", 1.95, AEGIS, "mech",
        [("aegis-walker-gun", "gun"), ("aegis-walker-shotgun", "gun"), ("aegis-walker-missile", "missile")],
    )
    for wn, st in (("aegis-walker-gun", "gun"), ("aegis-walker-shotgun", "gun"), ("aegis-walker-missile", "missile")):
        weapon_mount(wn, 24, 14, AEGIS[0], AEGIS[1], AEGIS[2], st, parts=True)
    build_from_vanilla(
        "nexus-prime", "reign", 2.2, GOLD, "mech",
        [("nexus-prime-core", "art"), ("nexus-prime-laser", "laser"), ("nexus-prime-point", "laser")],
    )
    build_from_vanilla(
        "apotheosis-core", "reign", 4.5, T6, "mech",
        [("apotheosis-core-nova", "laser"), ("apotheosis-core-batteries", "gun"), ("apotheosis-core-rail", "laser")],
    )

    # --- Naval (leviathan reference style) ---
    build_from_vanilla("naval", "risso", 1.35, NAVAL, "ship", [("naval-cannon", "gun"), ("naval-torpedo", "gun")])
    build_from_vanilla("naval-t2", "minke", 1.55, NAVAL, "ship", [("naval-t2-cannon", "gun"), ("naval-t2-shell", "art")])
    build_from_vanilla("iron-reef", "bryde", 1.75, STEEL, "ship", [("iron-reef-battery", "art")])
    build_from_vanilla(
        "needle-skiff", "sei", 1.95, NAVAL, "ship",
        [("needle-skiff-rack", "gun"), ("needle-skiff-rack-l", "gun"), ("needle-skiff-rack-r", "gun"), ("needle-skiff-ciws", "gun")],
    )
    build_from_vanilla(
        "leviathan-crown", "omura", 2.05, (DAIMYO[0], NAVAL[1], STORM[2]), "ship",
        [("leviathan-crown-main", "art"), ("leviathan-crown-flak", "gun"), ("leviathan-crown-beam", "laser"), ("leviathan-crown-torpedo", "gun")],
    )
    build_from_vanilla(
        "mare-imperator", "omura", 4.6, T6, "ship",
        [("mare-imperator-main", "art"), ("mare-imperator-ciws", "gun"), ("mare-imperator-beam", "laser"), ("mare-imperator-missile", "gun")],
    )

    print("sprites:", len(list(SPR.glob("*.png"))))
    from ensure_unit_sprites import main as ensure

    ensure()


if __name__ == "__main__":
    main()
