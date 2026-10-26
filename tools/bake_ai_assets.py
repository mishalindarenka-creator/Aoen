"""Bake Cursor GenerateImage assets into Mindustry stem sprites (unique, non-repeating)."""
from __future__ import annotations

import colorsys
import hashlib
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

MOD = Path(__file__).resolve().parents[1]
ASSETS = Path(r"C:\Users\misha\.cursor\projects\c-Users-misha-OneDrive-Desktop-Aoen\assets")
SPR_U = MOD / "sprites" / "units"
SPR_B = MOD / "sprites" / "blocks"
SPR_I = MOD / "sprites" / "items"

UNIT_SIZE = {
    "crab": 64, "crab-t2": 80, "ceramtyr-daimyo": 112, "quake-bulwark": 128,
    "storm-sovereign": 144, "eclipse-tyrant": 192, "crabzilla": 224,
    "snake": 64, "snake-t2": 80, "cinder-millipede": 96, "payload-serpent": 112,
    "singularity-eel": 128, "ouroboros-prime": 160,
    "boomeranger": 64, "boomeranger-t2": 80, "foundry-orbiter": 96,
    "aegis-walker": 112, "nexus-prime": 128, "apotheosis-core": 192,
    "naval": 64, "naval-t2": 80, "iron-reef": 96, "needle-skiff": 112,
    "leviathan-crown": 128, "mare-imperator": 192, "bahamut": 200,
}

BLOCK_TILES = {
    "shard-turret": 1, "wave-scatter": 2, "eclipse-beam": 2, "tyrant-rail": 3,
    "void-flak": 2, "aether-missile": 3, "ceramite-howitzer": 3, "singularity-lance": 4,
    "abyss-fortress": 4, "storm-battery": 3, "nocturne-bolt": 2, "tide-pulse": 3,
    "crab-howitzer": 4, "void-smelter": 2, "ceramite-forge": 3, "aether-refinery": 3,
    "nocturne-smelter": 2, "abyssal-foundry": 3, "tide-kiln": 3, "pale-foundry": 3,
    "void-compressor": 2, "ceramite-crucible": 2, "dark-drill": 2, "void-drill": 3,
    "mythril-drill": 3, "dark-generator": 1, "ember-generator": 2, "aether-reactor": 3,
    "mythril-reactor": 4, "dark-battery": 1, "nocturne-battery": 2, "tide-mender": 2,
    "abyss-radar": 2, "tide-conduit": 1, "void-unloader": 1,
    "ceramite-wall": 1, "ceramite-wall-large": 2, "nocturne-wall": 1, "nocturne-wall-large": 2,
    "abyssal-wall": 1, "abyssal-wall-large": 2, "tide-wall": 1, "tide-wall-large": 2,
    "mythril-wall": 1, "mythril-wall-large": 2, "ember-wall": 1, "ember-wall-large": 2,
    "dark-conveyor": 1, "dark-conveyor-armored": 1, "dark-junction": 1, "dark-router": 1,
    "dark-bridge": 1, "dark-overflow": 1, "dark-sorter": 1,
    "ground-fabricator": 3, "naval-fabricator": 3,
    "ground-reconstructor": 3, "ground-reconstructor-t3": 3, "ground-reconstructor-t4": 5,
    "ground-reconstructor-t5": 7, "ground-reconstructor-t6": 9, "ground-reconstructor-t7": 11,
    "naval-reconstructor": 3, "naval-reconstructor-t3": 3, "naval-reconstructor-t4": 5,
    "naval-reconstructor-t5": 7, "naval-reconstructor-t6": 9,
}


def harden(im: Image.Image, thresh: int = 30) -> Image.Image:
    out = im.convert("RGBA")
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= thresh else (0, 0, 0, 0)
    return out


def knock_bg(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    corners = [px[1, 1], px[w - 2, 1], px[1, h - 2], px[w - 2, h - 2]]
    br = sum(c[0] for c in corners) / 4
    bg = sum(c[1] for c in corners) / 4
    bb = sum(c[2] for c in corners) / 4
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            dist = abs(r - br) + abs(g - bg) + abs(b - bb)
            lum = (r + g + b) / 3
            sat = max(r, g, b) - min(r, g, b)
            if dist < 60 and sat < 40:
                px[x, y] = (0, 0, 0, 0)
            elif lum < 12 and sat < 22:
                px[x, y] = (0, 0, 0, 0)
            elif lum > 248 and sat < 15:
                px[x, y] = (0, 0, 0, 0)
    # edge flood
    from collections import deque
    vis = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        q.extend(((x, 0), (x, h - 1)))
    for y in range(h):
        q.extend(((0, y), (w - 1, y)))
    while q:
        x, y = q.popleft()
        if not (0 <= x < w and 0 <= y < h) or vis[y][x]:
            continue
        vis[y][x] = True
        r, g, b, a = px[x, y]
        if a == 0:
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            continue
        dist = abs(r - br) + abs(g - bg) + abs(b - bb)
        sat = max(r, g, b) - min(r, g, b)
        lum = (r + g + b) / 3
        if (dist < 75 and sat < 45) or (lum < 16 and sat < 25):
            px[x, y] = (0, 0, 0, 0)
            q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


def trim(im: Image.Image, pad: int = 2) -> Image.Image:
    im = harden(im)
    bbox = im.getbbox()
    if not bbox:
        return im
    c = im.crop(bbox)
    out = Image.new("RGBA", (c.width + pad * 2, c.height + pad * 2), (0, 0, 0, 0))
    out.paste(c, (pad, pad), c)
    return out


def fit(im: Image.Image, size: int) -> Image.Image:
    im = trim(knock_bg(im), 3)
    # slight sharpen for pixel readability
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
    im.thumbnail((size - 2, size - 2), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
    return harden(canvas, 28)


def hue_shift(im: Image.Image, amount: float) -> Image.Image:
    """Shift hue of non-transparent pixels; amount in [-0.5, 0.5]."""
    out = im.convert("RGBA")
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a < 28:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            h = (h + amount) % 1.0
            rr, gg, bb = colorsys.hsv_to_rgb(h, min(1.0, s * 1.05), v)
            px[x, y] = (int(rr * 255), int(gg * 255), int(bb * 255), a)
    return out


def uniqueify(im: Image.Image, key: str) -> Image.Image:
    """Make a derivative unique via deterministic hue/contrast/flip from key."""
    h = int(hashlib.md5(key.encode()).hexdigest()[:6], 16)
    amount = ((h % 200) - 100) / 220.0
    out = hue_shift(im, amount)
    if h & 1:
        out = ImageOps.mirror(out)
    if h & 2:
        out = ImageEnhance.Contrast(out).enhance(1.08 + (h % 10) * 0.01)
    if h & 4:
        out = ImageEnhance.Color(out).enhance(1.05 + (h % 8) * 0.015)
    return out


def find_asset(prefix: str, stem: str) -> Path | None:
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = ASSETS / f"{prefix}-{stem}{ext}"
        if p.exists():
            return p
    # fuzzy
    for p in ASSETS.glob(f"{prefix}-*{stem}*.*"):
        return p
    return None


def save_unit(stem: str, src: Image.Image) -> None:
    size = UNIT_SIZE.get(stem, 96)
    body = fit(src, size)
    body.save(SPR_U / f"{stem}.png")
    prev = body.copy()
    prev.thumbnail((64, 64), Image.Resampling.LANCZOS)
    c = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    c.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    harden(c, 20).save(SPR_U / f"{stem}-preview.png")
    # leg from lower third
    leg = body.crop((body.width // 4, body.height // 2, 3 * body.width // 4, body.height))
    leg = harden(trim(leg, 2))
    if not leg.getbbox():
        leg = Image.new("RGBA", (14, 26), (0, 0, 0, 0))
        d = ImageDraw.Draw(leg)
        d.polygon([(7, 1), (12, 10), (9, 25), (5, 25), (2, 10)], fill=(100, 90, 80, 255))
    leg.save(SPR_U / f"{stem}-leg.png")
    cell = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    d.ellipse([3, 3, 20, 20], fill=(255, 210, 130, 255), outline=(255, 240, 200, 255))
    cell.save(SPR_U / f"{stem}-cell.png")


def weapon_parts(unit_stem: str, weapon: str) -> None:
    body_p = SPR_U / f"{unit_stem}.png"
    if not body_p.exists():
        return
    body = Image.open(body_p).convert("RGBA")
    w = max(22, body.width // 3)
    h = max(16, body.height // 4)
    crop = body.crop((body.width // 3, body.height // 5, 2 * body.width // 3, body.height // 2))
    mount = uniqueify(fit(crop, max(w, h)), weapon)
    mount.save(SPR_U / f"{weapon}.png")
    for i, suf in enumerate(("-breech", "-barrel0", "-barrel1", "-muzzle", "-mag", "-coil", "-seg1", "-seg2", "-seg3", "-seg4", "-seg5")):
        part = uniqueify(mount, weapon + suf)
        part.thumbnail((max(10, w // 2 + i), max(10, h - i)), Image.Resampling.LANCZOS)
        harden(trim(part, 1)).save(SPR_U / f"{weapon}{suf}.png")


def save_block(stem: str, src: Image.Image) -> None:
    tiles = BLOCK_TILES.get(stem, 2)
    px = 32 * tiles
    out = fit(src, px)
    out.save(SPR_B / f"{stem}.png")
    if any(k in stem for k in ("turret", "bolt", "pulse", "howitzer", "beam", "rail", "flak", "missile", "lance", "fortress", "scatter", "battery")) and "storm-battery" in stem or any(
        k in stem for k in ("turret", "bolt", "pulse", "howitzer", "beam", "rail", "flak", "missile", "lance", "fortress", "scatter")
    ):
        heat = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(heat)
        d.ellipse([px // 2 - px // 6, px // 2 - px // 6, px // 2 + px // 6, px // 2 + px // 6], fill=(255, 90, 40, 180))
        heat.save(SPR_B / f"{stem}-heat.png")


def main() -> None:
    SPR_U.mkdir(parents=True, exist_ok=True)
    SPR_B.mkdir(parents=True, exist_ok=True)
    SPR_I.mkdir(parents=True, exist_ok=True)

    baked_u = baked_i = baked_b = 0

    # units
    for stem in UNIT_SIZE:
        p = find_asset("aoen-unit", stem)
        if not p:
            print("missing unit asset", stem)
            continue
        save_unit(stem, Image.open(p))
        baked_u += 1
        print("unit", stem)

    # items
    for stem in [
        "void-shard", "ceramite", "aether-dust", "nocturne-ore", "abyssal-quartz",
        "tide-coral", "ember-slag", "pale-mythril", "nocturne-plate", "abyssal-alloy", "tide-composite",
    ]:
        p = find_asset("aoen-item", stem)
        if not p:
            print("missing item", stem)
            continue
        fit(Image.open(p), 32).save(SPR_I / f"{stem}.png")
        baked_i += 1
        print("item", stem)

    # direct block assets
    direct_blocks = []
    for p in ASSETS.glob("aoen-block-*.*"):
        stem = p.stem.removeprefix("aoen-block-")
        direct_blocks.append(stem)
        save_block(stem, Image.open(p))
        baked_b += 1
        print("block", stem)

    # derive remaining blocks from nearest AI parents (unique hue each)
    parents = {
        "wave-scatter": "tide-pulse",
        "void-flak": "shard-turret",
        "aether-missile": "tide-pulse",
        "ceramite-howitzer": "crab-howitzer",
        "storm-battery": "tide-pulse",
        "ceramite-forge": "void-smelter",
        "aether-refinery": "tide-kiln",
        "abyssal-foundry": "nocturne-smelter",
        "pale-foundry": "mythril-reactor",
        "void-compressor": "void-smelter",
        "ceramite-crucible": "void-smelter",
        "dark-drill": "ground-fabricator",
        "void-drill": "mythril-reactor",
        "mythril-drill": "mythril-reactor",
        "dark-generator": "mythril-reactor",
        "ember-generator": "ember-wall",
        "aether-reactor": "mythril-reactor",
        "dark-battery": "nocturne-wall",
        "nocturne-battery": "nocturne-wall",
        "abyss-radar": "tide-mender",
        "tide-conduit": "dark-conveyor",
        "void-unloader": "dark-conveyor",
        "ceramite-wall": "ember-wall",
        "ceramite-wall-large": "ember-wall",
        "nocturne-wall-large": "nocturne-wall",
        "abyssal-wall": "nocturne-wall",
        "abyssal-wall-large": "nocturne-wall",
        "tide-wall": "tide-mender",
        "tide-wall-large": "tide-mender",
        "mythril-wall-large": "mythril-wall",
        "ember-wall-large": "ember-wall",
        "dark-conveyor-armored": "dark-conveyor",
        "dark-junction": "dark-conveyor",
        "dark-router": "dark-conveyor",
        "dark-bridge": "dark-conveyor",
        "dark-overflow": "dark-conveyor",
        "dark-sorter": "dark-conveyor",
        "naval-fabricator": "ground-fabricator",
        "ground-reconstructor": "ground-fabricator",
        "ground-reconstructor-t3": "ground-fabricator",
        "ground-reconstructor-t4": "ground-reconstructor-t7",
        "ground-reconstructor-t5": "ground-reconstructor-t7",
        "ground-reconstructor-t6": "ground-reconstructor-t7",
        "naval-reconstructor": "ground-fabricator",
        "naval-reconstructor-t3": "ground-fabricator",
        "naval-reconstructor-t4": "ground-reconstructor-t7",
        "naval-reconstructor-t5": "ground-reconstructor-t7",
        "naval-reconstructor-t6": "ground-reconstructor-t7",
    }
    for stem, parent in parents.items():
        if (SPR_B / f"{stem}.png").exists() and stem in direct_blocks:
            continue
        src_p = SPR_B / f"{parent}.png"
        if not src_p.exists():
            ap = find_asset("aoen-block", parent)
            if ap:
                save_block(parent, Image.open(ap))
                src_p = SPR_B / f"{parent}.png"
        if not src_p.exists():
            print("skip derive", stem)
            continue
        src = Image.open(src_p).convert("RGBA")
        der = uniqueify(src, stem)
        save_block(stem, der)
        baked_b += 1
        print("derived", stem, "←", parent)

    # conveyor frames
    for stem in ("dark-conveyor", "dark-conveyor-armored"):
        base = SPR_B / f"{stem}.png"
        if not base.exists():
            continue
        im = Image.open(base).convert("RGBA")
        for a in range(5):
            for b in range(4):
                fr = uniqueify(im, f"{stem}-{a}-{b}")
                fr = ImageEnhance.Brightness(fr).enhance(0.9 + 0.02 * a)
                fr.save(SPR_B / f"{stem}-{a}-{b}.png")

    # reconstructor layers
    for p in list(SPR_B.glob("*reconstructor*.png")):
        if p.stem.endswith(("-in", "-out", "-top", "-heat")):
            continue
        im = Image.open(p).convert("RGBA")
        im.save(p.with_name(p.stem + "-top.png"))
        w, h = im.size
        inp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        outp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        inp.alpha_composite(im.crop((0, 0, w // 2, h)))
        outp.alpha_composite(im.crop((w // 2, 0, w, h)), (w // 2, 0))
        inp.save(p.with_name(p.stem + "-in.png"))
        outp.save(p.with_name(p.stem + "-out.png"))

    # crafter tops
    for p in SPR_B.glob("*.png"):
        if p.stem.endswith("-top"):
            continue
        if any(k in p.stem for k in ("smelter", "forge", "foundry", "kiln", "refinery", "crucible", "compressor")):
            top = Image.new("RGBA", Image.open(p).size, (0, 0, 0, 0))
            d = ImageDraw.Draw(top)
            cx, cy = top.width // 2, top.height // 2
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 200, 120, 200))
            top.save(p.with_name(p.stem + "-top.png"))

    # ores from item crystals
    ore_map = {
        "ore-void-shard": "void-shard",
        "ore-ceramite": "ceramite",
        "ore-nocturne": "nocturne-ore",
        "ore-abyssal-quartz": "abyssal-quartz",
        "ore-tide-coral": "tide-coral",
        "ore-ember-slag": "ember-slag",
        "ore-pale-mythril": "pale-mythril",
    }
    for ore, item in ore_map.items():
        ip = SPR_I / f"{item}.png"
        if not ip.exists():
            continue
        base = Image.open(ip).convert("RGBA")
        for i in range(1, 4):
            tile = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
            chip = uniqueify(fit(base, 14), f"{ore}{i}")
            for _ in range(3 + i):
                import random
                random.seed(hash(f"{ore}{i}{_}") & 0xFFFF)
                x, y = random.randint(2, 18), random.randint(2, 18)
                tile.alpha_composite(chip, (x, y))
            harden(tile).save(SPR_B / f"{ore}{i}.png")

    # weapons from unit bodies (jababarium multi-part)
    weapon_map = [
        ("crab", "crab-claw"), ("crab-t2", "crab-t2-claw"), ("ceramtyr-daimyo", "ceramtyr-daimyo-claw"),
        ("ceramtyr-daimyo", "ceramtyr-daimyo-gun"), ("ceramtyr-daimyo", "ceramtyr-daimyo-mortar"),
        ("quake-bulwark", "quake-bulwark-mortar"), ("quake-bulwark", "quake-bulwark-gun"),
        ("quake-bulwark", "quake-bulwark-flak"), ("quake-bulwark", "quake-bulwark-missile"),
        ("storm-sovereign", "storm-sovereign-beam"), ("storm-sovereign", "storm-sovereign-rail"),
        ("storm-sovereign", "storm-sovereign-emp"), ("storm-sovereign", "storm-sovereign-missile"),
        ("eclipse-tyrant", "eclipse-tyrant-claw"), ("eclipse-tyrant", "eclipse-tyrant-mortar"),
        ("eclipse-tyrant", "eclipse-tyrant-beam"), ("eclipse-tyrant", "eclipse-tyrant-missile"),
        ("eclipse-tyrant", "eclipse-tyrant-rail"),
        ("crabzilla", "crabzilla-claw"), ("crabzilla", "crabzilla-mortar"), ("crabzilla", "crabzilla-beam"),
        ("crabzilla", "crabzilla-rail"), ("crabzilla", "crabzilla-missile"), ("crabzilla", "crabzilla-flak"),
        ("crabzilla", "crabzilla-nova"),
        ("snake", "snake-fang"), ("snake-t2", "snake-t2-fang"), ("snake-t2", "snake-t2-spit"),
        ("cinder-millipede", "cinder-millipede-spit"), ("cinder-millipede", "cinder-millipede-slag"),
        ("payload-serpent", "payload-serpent-hook"), ("payload-serpent", "payload-serpent-spit-l"),
        ("payload-serpent", "payload-serpent-spit-r"), ("payload-serpent", "payload-serpent-rear"),
        ("singularity-eel", "singularity-eel-rift"), ("singularity-eel", "singularity-eel-bolt"),
        ("singularity-eel", "singularity-eel-spores"),
        ("ouroboros-prime", "ouroboros-prime-maw"), ("ouroboros-prime", "ouroboros-prime-bolt"),
        ("aegis-walker", "aegis-walker-gun"), ("aegis-walker", "aegis-walker-shotgun"),
        ("aegis-walker", "aegis-walker-missile"),
        ("nexus-prime", "nexus-prime-core"), ("nexus-prime", "nexus-prime-laser"), ("nexus-prime", "nexus-prime-point"),
        ("apotheosis-core", "apotheosis-core-nova"), ("apotheosis-core", "apotheosis-core-batteries"),
        ("apotheosis-core", "apotheosis-core-rail"),
        ("foundry-orbiter", "foundry-orbiter-laser"),
        ("naval", "naval-cannon"), ("naval", "naval-torpedo"),
        ("naval-t2", "naval-t2-cannon"), ("naval-t2", "naval-t2-shell"),
        ("iron-reef", "iron-reef-battery"),
        ("needle-skiff", "needle-skiff-rack"), ("needle-skiff", "needle-skiff-rack-l"),
        ("needle-skiff", "needle-skiff-rack-r"), ("needle-skiff", "needle-skiff-ciws"),
        ("leviathan-crown", "leviathan-crown-main"), ("leviathan-crown", "leviathan-crown-flak"),
        ("leviathan-crown", "leviathan-crown-beam"), ("leviathan-crown", "leviathan-crown-torpedo"),
        ("mare-imperator", "mare-imperator-main"), ("mare-imperator", "mare-imperator-ciws"),
        ("mare-imperator", "mare-imperator-beam"), ("mare-imperator", "mare-imperator-missile"),
    ]
    for u, w in weapon_map:
        weapon_parts(u, w)
    for lab in "abc":
        weapon_parts("boomeranger", f"boomeranger-orb-{lab}")
    for lab in "abcde":
        weapon_parts("boomeranger-t2", f"boomeranger-t2-orb-{lab}")
        weapon_parts("foundry-orbiter", f"foundry-orbiter-orb-{lab}")

    # serpent segments from snake bodies
    try:
        from build_snake_sprites import main as build_snakes
        build_snakes()
    except Exception as e:
        print("snake segments", e)
    try:
        from build_bahamut_sprites import main as build_bahamut
        build_bahamut()
    except Exception as e:
        print("bahamut parts", e)

    # nuke double-prefix
    for folder in (SPR_U, SPR_B, SPR_I):
        for p in list(folder.glob("aoen-*.png")):
            p.unlink()

    print(f"baked units={baked_u} items={baked_i} blocks={baked_b}")


if __name__ == "__main__":
    main()
