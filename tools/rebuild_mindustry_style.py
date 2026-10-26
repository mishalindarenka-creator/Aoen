"""Rebuild ALL unit bodies + weapons in vanilla Mindustry silhouette style.

Weapons are drawn as proper top-down mounts (barrel points +Y / up), not body crops.
Uses Anuken vanilla templates + hard 3-band tint (fits next to dagger/atrax/toxopid).
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

SHELL = ((36, 34, 40, 255), (68, 64, 72, 255), (160, 150, 130, 255))
SHELL2 = ((40, 36, 44, 255), (90, 78, 70, 255), (220, 190, 120, 255))
DAIMYO = ((48, 12, 14, 255), (110, 28, 32, 255), (210, 70, 70, 255))
STEEL = ((40, 46, 56, 255), (78, 90, 104, 255), (170, 190, 210, 255))
STORM = ((36, 32, 72, 255), (78, 68, 140, 255), (170, 160, 240, 255))
T6 = ((16, 14, 20, 255), (70, 55, 40, 255), (255, 200, 90, 255))
T7 = ((12, 8, 18, 255), (90, 28, 40, 255), (255, 90, 70, 255))
SNAKE = ((40, 34, 58, 255), (100, 88, 140, 255), (190, 175, 230, 255))
SLAG = ((52, 28, 16, 255), (140, 70, 30, 255), (230, 140, 55, 255))
AEGIS = ((28, 52, 42, 255), (48, 110, 82, 255), (90, 210, 150, 255))
GOLD = ((28, 22, 14, 255), (120, 95, 35, 255), (245, 205, 90, 255))
VOID = ((18, 14, 22, 255), (55, 42, 70, 255), (160, 130, 210, 255))
NAVAL = ((28, 44, 58, 255), (52, 88, 112, 255), (130, 195, 215, 255))
ABYSS = ((14, 10, 28, 255), (70, 40, 120, 255), (200, 160, 255, 255))

REFS = [
    "alpha-cell.png", "arkyid.png", "atrax.png", "atrax-leg.png",
    "dagger.png", "dagger-leg.png", "mace.png", "fortress.png", "scepter.png", "reign.png",
    "risso.png", "minke.png", "bryde.png", "sei.png", "omura.png",
    "toxopid.png", "spiroct.png",
]


def ensure_refs() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    for name in REFS:
        dest = TMP / name
        if dest.exists() and dest.stat().st_size > 80:
            continue
        try:
            urllib.request.urlretrieve(f"{BASE}/{name}", dest)
        except Exception as e:
            print("skip", name, e)


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


def tint_hard(src: Image.Image, dark, mid, hi) -> Image.Image:
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
            op[x, y] = c
    return out


def scale_nn(src: Image.Image, scale: float) -> Image.Image:
    w = max(8, int(round(src.width * scale)))
    h = max(8, int(round(src.height * scale)))
    return src.resize((w, h), Image.Resampling.NEAREST)


def load(name: str) -> Image.Image:
    return Image.open(TMP / name).convert("RGBA")


def body_save(unit_id: str, body: Image.Image, leg: Image.Image | None = None) -> None:
    body = harden(trim(body, 4))
    body.save(SPR / f"{unit_id}.png")
    prev = body.copy()
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR / f"{unit_id}-preview.png")
    if leg is not None:
        harden(trim(leg, 2)).save(SPR / f"{unit_id}-leg.png")
    cell = tint_hard(load("alpha-cell.png"), body.getpixel((body.width // 2, body.height // 2))[:3] + (255,), (120, 100, 80, 255), (255, 220, 160, 255))
    # simpler cell
    c = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.ellipse([4, 4, 19, 19], fill=(255, 211, 127, 255))
    harden(c).save(SPR / f"{unit_id}-cell.png")


def build_unit(stem: str, van: str, scale: float, pal, kind: str, leg_van: str | None = None) -> None:
    dark, mid, hi = pal
    body = tint_hard(scale_nn(load(f"{van}.png"), scale), dark, mid, hi)
    # center panel accent like vanilla readability
    d = ImageDraw.Draw(body)
    cx, cy = body.width // 2, body.height // 2
    d.rectangle([cx - 3, cy - 2, cx + 3, cy + 4], outline=hi)
    leg = None
    if kind in ("legs", "mech"):
        lv = leg_van or ("atrax-leg.png" if kind == "legs" else "dagger-leg.png")
        leg = tint_hard(scale_nn(load(lv), max(scale * 0.95, 1.0)), dark, mid, hi)
    body_save(stem, body, leg)


def weapon_gun(name: str, pal, style: str = "gun", scale: float = 1.0, parts: bool = True) -> None:
    """Top-down weapon: breech at bottom, barrel toward +Y (Mindustry shoot forward)."""
    dark, mid, hi = pal
    w = max(14, int(18 * scale))
    h = max(18, int(24 * scale))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # breech (rear / bottom)
    d.rectangle([2, h // 2, w - 3, h - 2], fill=dark, outline=hi)
    d.rectangle([3, h // 2 + 1, w - 4, h - 3], outline=mid)
    bw = max(4, w // 3)
    if style in ("gun", "flak"):
        d.rectangle([w // 2 - bw // 2, 1, w // 2 + bw // 2, h // 2 + 2], fill=mid, outline=hi)
        d.rectangle([w // 2 - 1, 0, w // 2 + 1, 4], fill=hi)
    elif style == "laser":
        d.rectangle([w // 2 - bw // 2, 2, w // 2 + bw // 2, h // 2 + 2], fill=mid, outline=hi)
        d.rectangle([w // 2 - 1, 1, w // 2 + 1, h // 2], fill=hi)
        d.ellipse([w // 2 - 3, h // 2 - 2, w // 2 + 3, h // 2 + 4], outline=hi)
    elif style == "art":
        d.ellipse([w // 2 - bw, h // 2 - 2, w // 2 + bw, h - 2], fill=dark, outline=hi)
        d.rectangle([w // 2 - bw // 2, 1, w // 2 + bw // 2, h // 2 + 4], fill=mid, outline=hi)
        d.ellipse([w // 2 - 4, 0, w // 2 + 4, 8], fill=hi)
    elif style == "missile":
        d.rectangle([w // 2 - bw // 2, 6, w // 2 + bw // 2, h - 2], fill=mid, outline=hi)
        d.ellipse([w // 2 - 3, 0, w // 2 + 3, 8], fill=hi)
    elif style == "rail":
        d.rectangle([w // 2 - bw // 2, 0, w // 2 + bw // 2, h - 2], fill=mid, outline=hi)
        for y in range(4, h - 4, 4):
            d.line([(2, y), (w - 3, y)], fill=hi)
    elif style == "fang":
        d.polygon([(2, h - 2), (w // 2, 1), (w - 3, h - 2)], fill=hi, outline=dark)
    harden(trim(im, 2)).save(SPR / f"{name}.png")
    if not parts:
        return
    # breech / barrels / muzzle relative to same palette (consistent with mount)
    breech = Image.new("RGBA", (max(w - 2, 10), max(h // 2, 8)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(breech)
    bd.rectangle([0, 0, breech.width - 1, breech.height - 1], fill=dark, outline=hi)
    harden(trim(breech, 1)).save(SPR / f"{name}-breech.png")
    for bi in range(2):
        bw2, bh2 = max(5, w // 4), max(14, h - 4)
        barrel = Image.new("RGBA", (bw2, bh2), (0, 0, 0, 0))
        bld = ImageDraw.Draw(barrel)
        bld.rectangle([1, 0, bw2 - 2, bh2 - 1], fill=mid, outline=hi)
        bld.rectangle([bw2 // 2 - 1, 0, bw2 // 2 + 1, 3], fill=hi)
        harden(trim(barrel, 1)).save(SPR / f"{name}-barrel{bi}.png")
    muzzle = Image.new("RGBA", (max(8, w // 2), 8), (0, 0, 0, 0))
    md = ImageDraw.Draw(muzzle)
    md.polygon([(0, 4), (muzzle.width // 2, 0), (muzzle.width - 1, 4), (muzzle.width // 2, 7)], fill=hi)
    harden(trim(muzzle, 1)).save(SPR / f"{name}-muzzle.png")
    for extra in ("-mag", "-coil"):
        ex = Image.new("RGBA", (max(10, w // 2), max(8, h // 2)), (0, 0, 0, 0))
        ed = ImageDraw.Draw(ex)
        ed.rectangle([0, 0, ex.width - 1, ex.height - 1], fill=mid, outline=hi)
        harden(trim(ex, 1)).save(SPR / f"{name}{extra}.png")


def claw_weapon(prefix: str, pal, n: int = 3, scale: float = 1.0) -> None:
    """Segmented claw: mount + seg1..n pointing +Y tip."""
    dark, mid, hi = pal
    s = max(12, int(14 * scale))
    mount = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(mount)
    d.rectangle([1, 1, s - 2, s - 2], fill=mid, outline=hi)
    d.rectangle([s // 2 - 2, s // 2 - 2, s // 2 + 2, s // 2 + 2], fill=hi)
    harden(trim(mount, 2)).save(SPR / f"{prefix}.png")
    specs = [(10, 14), (12, 12), (14, 10), (15, 9), (16, 9)][:n]
    for i, (bw, bh) in enumerate(specs, 1):
        w, h = max(int(bw * scale), 8), max(int(bh * scale), 7)
        seg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(seg)
        col = hi if i == n else mid if i > 1 else dark
        # tip toward top
        sd.rectangle([1, 2, w - 2, h - 1], fill=col, outline=dark)
        if i == n:
            sd.polygon([(2, 4), (w // 2, 0), (w - 3, 4)], fill=hi)
        harden(trim(seg, 2)).save(SPR / f"{prefix}-seg{i}.png")


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    ensure_refs()
    for p in list(SPR.glob("aoen-*.png")):
        p.unlink()

    # --- bodies (vanilla silhouettes) ---
    build_unit("crab", "atrax", 1.25, SHELL, "legs")
    build_unit("crab-t2", "spiroct", 1.45, SHELL2, "legs")
    build_unit("ceramtyr-daimyo", "arkyid", 1.7, DAIMYO, "legs")
    build_unit("quake-bulwark", "arkyid", 1.85, STEEL, "legs")
    build_unit("storm-sovereign", "toxopid", 2.1, STORM, "legs")
    build_unit("eclipse-tyrant", "toxopid", 4.2, T6, "legs")
    build_unit("crabzilla", "toxopid", 5.2, T7, "legs")

    build_unit("boomeranger", "dagger", 1.35, GOLD, "mech")
    build_unit("boomeranger-t2", "mace", 1.55, GOLD, "mech")
    build_unit("foundry-orbiter", "fortress", 1.75, STEEL, "mech")
    build_unit("aegis-walker", "scepter", 1.95, AEGIS, "mech")
    build_unit("nexus-prime", "reign", 2.2, GOLD, "mech")
    build_unit("apotheosis-core", "reign", 4.4, T6, "mech")

    build_unit("naval", "risso", 1.35, NAVAL, "ship")
    build_unit("naval-t2", "minke", 1.55, NAVAL, "ship")
    build_unit("iron-reef", "bryde", 1.75, STEEL, "ship")
    build_unit("needle-skiff", "sei", 1.95, NAVAL, "ship")
    build_unit("leviathan-crown", "omura", 2.05, (DAIMYO[0], NAVAL[1], STORM[2]), "ship")
    build_unit("mare-imperator", "omura", 4.5, T6, "ship")

    # serpents / bahamut heads+segments (keep palette; weapons rebuilt below)
    from build_snake_sprites import main as build_snakes
    from build_bahamut_sprites import main as build_bahamut

    build_snakes()
    build_bahamut()
    # NOTE: do NOT call build_naval — bodies already rebuilt from vanilla risso→omura

    # --- weapons (correct +Y barrel orientation + matching parts) ---
    claw_weapon("crab-claw", SHELL, 3, 1.1)
    weapon_gun("crab-spit", SHELL, "gun", 0.9)
    claw_weapon("crab-t2-claw", SHELL2, 3, 1.25)
    weapon_gun("crab-t2-spit", SHELL2, "gun", 1.0)
    weapon_gun("crab-t2-flak", SHELL2, "flak", 0.95)
    claw_weapon("ceramtyr-daimyo-claw", DAIMYO, 4, 1.6)
    weapon_gun("ceramtyr-daimyo-gun", DAIMYO, "gun", 1.2)
    weapon_gun("ceramtyr-daimyo-mortar", DAIMYO, "art", 1.3)
    weapon_gun("ceramtyr-daimyo-fang", DAIMYO, "fang", 1.1)

    for n, st, sc in [
        ("quake-bulwark-mortar", "art", 1.3), ("quake-bulwark-gun", "gun", 1.1),
        ("quake-bulwark-flak", "flak", 1.0), ("quake-bulwark-missile", "missile", 1.1),
        ("quake-bulwark-rail", "rail", 1.15),
    ]:
        weapon_gun(n, STEEL, st, sc)
    for n, st, sc in [
        ("storm-sovereign-beam", "laser", 1.3), ("storm-sovereign-rail", "rail", 1.2),
        ("storm-sovereign-emp", "art", 1.1), ("storm-sovereign-missile", "missile", 1.1),
    ]:
        weapon_gun(n, STORM, st, sc)
    claw_weapon("eclipse-tyrant-claw", T6, 4, 3.0)
    for n, st, sc in [
        ("eclipse-tyrant-mortar", "art", 1.6), ("eclipse-tyrant-beam", "laser", 1.5),
        ("eclipse-tyrant-missile", "missile", 1.4), ("eclipse-tyrant-rail", "rail", 1.4),
    ]:
        weapon_gun(n, T6, st, sc)
    claw_weapon("crabzilla-claw", T7, 5, 4.2)
    for n, st, sc in [
        ("crabzilla-mortar", "art", 2.0), ("crabzilla-beam", "laser", 1.9),
        ("crabzilla-rail", "rail", 1.8), ("crabzilla-missile", "missile", 1.7),
        ("crabzilla-flak", "flak", 1.5), ("crabzilla-nova", "laser", 2.0),
    ]:
        weapon_gun(n, T7, st, sc)

    weapon_gun("snake-fang", SNAKE, "fang", 1.0, parts=True)
    weapon_gun("snake-spit", SNAKE, "gun", 0.95)
    weapon_gun("snake-t2-fang", SNAKE, "fang", 1.1)
    weapon_gun("snake-t2-spit", SNAKE, "gun", 1.0)
    weapon_gun("snake-t2-sap", SNAKE, "laser", 1.0)
    weapon_gun("cinder-millipede-spit", SLAG, "gun", 1.1)
    weapon_gun("cinder-millipede-slag", SLAG, "art", 1.1)
    weapon_gun("cinder-millipede-fang", SLAG, "fang", 1.05)
    for n, st in [
        ("payload-serpent-hook", "gun"), ("payload-serpent-spit-l", "gun"),
        ("payload-serpent-spit-r", "gun"), ("payload-serpent-rear", "art"),
        ("payload-serpent-sap", "laser"),
    ]:
        weapon_gun(n, AEGIS, st, 1.1)
    weapon_gun("singularity-eel-rift", VOID, "laser", 1.2)
    weapon_gun("singularity-eel-bolt", VOID, "laser", 1.1)
    weapon_gun("singularity-eel-spores", VOID, "gun", 1.0)
    weapon_gun("singularity-eel-missile", VOID, "missile", 1.1)
    weapon_gun("ouroboros-prime-maw", ABYSS, "laser", 1.5)
    weapon_gun("ouroboros-prime-bolt", ABYSS, "laser", 1.4)
    weapon_gun("ouroboros-prime-missile", ABYSS, "missile", 1.4)
    weapon_gun("ouroboros-prime-emp", ABYSS, "art", 1.3)

    for lab in "abc":
        weapon_gun(f"boomeranger-orb-{lab}", GOLD, "art", 0.75, parts=False)
    for lab in "abcde":
        weapon_gun(f"boomeranger-t2-orb-{lab}", GOLD, "art", 0.8, parts=False)
    weapon_gun("foundry-orbiter-laser", STEEL, "laser", 1.2)
    weapon_gun("foundry-orbiter-shotgun", STEEL, "gun", 1.15)
    weapon_gun("foundry-orbiter-missile", STEEL, "missile", 1.1)
    weapon_gun("foundry-orbiter-flak", STEEL, "flak", 1.05)
    for n, st in [
        ("aegis-walker-gun", "gun"), ("aegis-walker-shotgun", "gun"),
        ("aegis-walker-missile", "missile"), ("aegis-walker-emp", "art"),
    ]:
        weapon_gun(n, AEGIS, st, 1.2)
    for n, st in [
        ("nexus-prime-core", "art"), ("nexus-prime-laser", "laser"),
        ("nexus-prime-point", "laser"), ("nexus-prime-missile", "missile"),
        ("nexus-prime-flak", "flak"),
    ]:
        weapon_gun(n, GOLD, st, 1.3)
    for n, st in [
        ("apotheosis-core-nova", "laser"), ("apotheosis-core-batteries", "gun"),
        ("apotheosis-core-rail", "rail"), ("apotheosis-core-missile", "missile"),
        ("apotheosis-core-emp", "art"),
    ]:
        weapon_gun(n, T6, st, 1.5)

    for n, st, sc, pal in [
        ("naval-cannon", "gun", 1.0, NAVAL), ("naval-torpedo", "missile", 1.0, NAVAL),
        ("naval-flak", "flak", 0.95, NAVAL),
        ("naval-t2-cannon", "gun", 1.1, NAVAL), ("naval-t2-shell", "art", 1.1, NAVAL),
        ("naval-t2-laser", "laser", 1.1, NAVAL),
        ("iron-reef-battery", "art", 1.2, STEEL), ("iron-reef-flak", "flak", 1.1, STEEL),
        ("iron-reef-missile", "missile", 1.15, STEEL),
        ("needle-skiff-rack", "gun", 1.2, NAVAL), ("needle-skiff-rack-l", "gun", 1.2, NAVAL),
        ("needle-skiff-rack-r", "gun", 1.2, NAVAL), ("needle-skiff-ciws", "flak", 1.0, NAVAL),
        ("needle-skiff-beam", "laser", 1.15, NAVAL),
        ("leviathan-crown-main", "art", 1.4, NAVAL), ("leviathan-crown-flak", "flak", 1.2, NAVAL),
        ("leviathan-crown-beam", "laser", 1.3, NAVAL), ("leviathan-crown-torpedo", "missile", 1.2, NAVAL),
        ("leviathan-crown-rail", "rail", 1.25, NAVAL),
        ("mare-imperator-main", "art", 1.7, T6), ("mare-imperator-ciws", "flak", 1.4, T6),
        ("mare-imperator-beam", "laser", 1.6, T6), ("mare-imperator-missile", "missile", 1.5, T6),
        ("mare-imperator-rail", "rail", 1.55, T6),
        ("bahamut-catastrophe", "art", 2.2, DAIMYO), ("bahamut-skyfall", "missile", 1.8, DAIMYO),
        ("bahamut-breath", "laser", 2.0, DAIMYO), ("bahamut-claw", "fang", 1.8, DAIMYO),
        ("bahamut-orb", "art", 1.4, GOLD), ("bahamut-wing-missile", "missile", 1.5, DAIMYO),
        ("bahamut-emp", "art", 1.4, STORM),
    ]:
        weapon_gun(n, pal, st, sc)

    print("rebuild mindustry-style OK", len(list(SPR.glob("*.png"))))


if __name__ == "__main__":
    main()
