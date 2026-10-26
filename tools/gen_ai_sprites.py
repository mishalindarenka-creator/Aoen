"""Generate unique Mindustry sprites via free Pollinations image API (no key).

Safe public endpoint: https://image.pollinations.ai
Each content stem gets a distinct prompt so textures don't look copy-pasted.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

MOD = Path(__file__).resolve().parents[1]
SPR_U = MOD / "sprites" / "units"
SPR_B = MOD / "sprites" / "blocks"
SPR_I = MOD / "sprites" / "items"
CACHE = Path(__file__).resolve().parent / "_ai_cache"
CACHE.mkdir(parents=True, exist_ok=True)

UA = "AoenModSpriteGen/1.0 (Mindustry mod local asset bake)"


def harden(im: Image.Image, thresh: int = 28) -> Image.Image:
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


def knock_bg(im: Image.Image) -> Image.Image:
    """Remove near-black / near-white / flat studio backgrounds."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    # sample corners to detect bg
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    br = sum(c[0] for c in corners) / 4
    bg = sum(c[1] for c in corners) / 4
    bb = sum(c[2] for c in corners) / 4
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            # distance to corner bg
            dist = abs(r - br) + abs(g - bg) + abs(b - bb)
            lum = (r + g + b) / 3
            # chroma
            sat = max(r, g, b) - min(r, g, b)
            if dist < 55 and sat < 35:
                px[x, y] = (0, 0, 0, 0)
            elif lum < 14 and sat < 20:
                px[x, y] = (0, 0, 0, 0)
            elif lum > 245 and sat < 18:
                px[x, y] = (0, 0, 0, 0)
    # flood from edges for leftover bg
    from collections import deque

    visited = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        q.append((x, 0))
        q.append((x, h - 1))
    for y in range(h):
        q.append((0, y))
        q.append((w - 1, y))
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or visited[y][x]:
            continue
        visited[y][x] = True
        r, g, b, a = px[x, y]
        if a == 0:
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                q.append((nx, ny))
            continue
        lum = (r + g + b) / 3
        sat = max(r, g, b) - min(r, g, b)
        dist = abs(r - br) + abs(g - bg) + abs(b - bb)
        if (dist < 70 and sat < 40) or (lum < 18 and sat < 25):
            px[x, y] = (0, 0, 0, 0)
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                q.append((nx, ny))
    return im


def fetch_image(prompt: str, width: int = 256, height: int = 256, retries: int = 4) -> Image.Image:
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16) % 999999
    q = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{q}"
        f"?width={width}&height={height}&seed={seed}&nologo=true&enhance=true&model=flux"
    )
    cache_key = hashlib.sha1(f"{prompt}|{width}x{height}|{seed}".encode()).hexdigest()
    cache_path = CACHE / f"{cache_key}.png"
    if cache_path.exists() and cache_path.stat().st_size > 800:
        return Image.open(cache_path).convert("RGBA")

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
            if len(data) < 500:
                raise RuntimeError("tiny response")
            cache_path.write_bytes(data)
            return Image.open(cache_path).convert("RGBA")
        except Exception as e:
            last_err = e
            time.sleep(1.5 + attempt)
    raise RuntimeError(f"fetch failed: {last_err}")


def fit_square(im: Image.Image, size: int) -> Image.Image:
    im = trim(knock_bg(im), 4)
    # keep aspect inside square
    im.thumbnail((size - 4, size - 4), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
    return harden(canvas, 24)


def save_unit_body(stem: str, im: Image.Image, size: int) -> None:
    body = fit_square(im, size)
    body.save(SPR_U / f"{stem}.png")
    prev = body.copy()
    prev.thumbnail((64, 64), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    harden(canvas, 20).save(SPR_U / f"{stem}-preview.png")
    # leg stub from bottom crop
    leg = body.crop((body.width // 3, body.height // 2, 2 * body.width // 3, body.height))
    leg = harden(trim(leg, 2))
    if leg.getbbox():
        leg.save(SPR_U / f"{stem}-leg.png")
    else:
        leg = Image.new("RGBA", (16, 28), (0, 0, 0, 0))
        d = ImageDraw.Draw(leg)
        d.ellipse([2, 2, 13, 26], fill=(120, 110, 100, 255))
        leg.save(SPR_U / f"{stem}-leg.png")
    cell = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    d.ellipse([3, 3, 20, 20], fill=(255, 210, 120, 255), outline=(255, 240, 200, 255))
    cell.save(SPR_U / f"{stem}-cell.png")


def save_block(stem: str, im: Image.Image, tiles: int) -> None:
    px = 32 * tiles
    out = fit_square(im, px)
    out.save(SPR_B / f"{stem}.png")
    if any(k in stem for k in ("turret", "bolt", "pulse", "howitzer", "beam", "rail", "flak", "missile", "lance", "fortress", "battery", "scatter")):
        heat = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(heat)
        d.ellipse([px // 2 - px // 6, px // 2 - px // 6, px // 2 + px // 6, px // 2 + px // 6], fill=(255, 90, 40, 180))
        heat.save(SPR_B / f"{stem}-heat.png")


def save_item(stem: str, im: Image.Image) -> None:
    fit_square(im, 32).save(SPR_I / f"{stem}.png")


# --- prompt builders ---
# CRITICAL rules for the image model (also used when finishing parts of a unit):
STYLE_GUIDE = (
    "STRICT Mindustry vanilla sprite rules: flat orthographic TOP-DOWN unit icon like "
    "Anuken dagger/atrax/toxopid/omura — NOT a photo, NOT isometric 3/4, NOT painted concept art. "
    "Hard 2–3 color bands + black outline silhouette, low-res crisp pixels, transparent or pure black void bg. "
    "Study Mindustry + popular mods (Exo, Progressive, NH) silhouette language: readable limbs, centered torso, "
    "no perspective foreshortening. When generating a PART (leg, claw seg, barrel, breech, muzzle, wing, segment), "
    "MATCH the already-finished body of THIS unit: same palette, same outline thickness, same pixel scale, "
    "same lighting direction; do not invent a new style. Barrel/muzzle always point toward +Y (up) on the sheet. "
    "Weapons are separate mount sprites, never a random crop of the body."
)


def unit_prompt(flavor: str) -> str:
    return f"{STYLE_GUIDE} Subject: {flavor}."


UNIT_PROMPTS: dict[str, tuple[str, int]] = {
    "crab": (unit_prompt("small atrax-like crab walker, beige shell, twin side claws"), 64),
    "crab-t2": (unit_prompt("spiroct-like sand crab, gold trim, heavier claws"), 80),
    "ceramtyr-daimyo": (unit_prompt("arkyid-like crimson warlord crab, red lacquer, ornate claws"), 112),
    "quake-bulwark": (unit_prompt("steel siege crab fortress, gray plating, mortar hump"), 128),
    "storm-sovereign": (unit_prompt("toxopid-like violet storm arachnid, purple arcs"), 144),
    "eclipse-tyrant": (unit_prompt("colossal toxopid eclipse crab, dark gold core, huge claws"), 192),
    "crabzilla": (unit_prompt("kaiju toxopid crabzilla, volcanic red glow, massive carapace"), 224),
    "snake": (unit_prompt("desert serpent HEAD only + matching body-segment style, ochre"), 64),
    "snake-t2": (unit_prompt("aquatic toxic serpent head, teal bioluminescence"), 80),
    "cinder-millipede": (unit_prompt("brimstone millipede head, lava cracks, ember glow"), 96),
    "payload-serpent": (unit_prompt("green cargo serpent head, modular plates"), 112),
    "singularity-eel": (unit_prompt("void eel head, dark purple rift energy"), 128),
    "ouroboros-prime": (unit_prompt("cosmic ouroboros head, abyssal violet"), 160),
    "boomeranger": (unit_prompt("golden dagger-like mech, orbiting orb mounts"), 64),
    "boomeranger-t2": (unit_prompt("ornate gold mace-like mech lancer"), 80),
    "foundry-orbiter": (unit_prompt("foundry fortress-like mech, molten vents, steel/slag"), 96),
    "aegis-walker": (unit_prompt("emerald scepter-like aegis guardian, shield plates"), 112),
    "nexus-prime": (unit_prompt("nexus reign-like command mech, golden core"), 128),
    "apotheosis-core": (unit_prompt("apotheosis colossus reign-like, radiant gold nova"), 192),
    "naval": (unit_prompt("small risso-like teal patrol skiff"), 64),
    "naval-t2": (unit_prompt("minke-like armored teal gunboat"), 80),
    "iron-reef": (unit_prompt("bryde-like ironclad reef battleship, rust steel"), 96),
    "needle-skiff": (unit_prompt("sei-like needle missile skiff, cyan hull"), 112),
    "leviathan-crown": (unit_prompt("omura-like crowned leviathan, crimson+teal"), 128),
    "mare-imperator": (unit_prompt("omura-scale imperial sea titan, dark gold decks"), 192),
    "bahamut": (unit_prompt("Proto Bahamut dragon boss, silver armor, red wings, chains — Mindustry boss silhouette"), 200),
}

ITEM_PROMPTS = {
    "void-shard": "pixel art crystal item icon void purple shard, Mindustry item, black background",
    "ceramite": "pixel art ceramic brick item orange-brown, Mindustry item icon, black background",
    "aether-dust": "pixel art glowing cyan aether dust pile item, Mindustry icon, black background",
    "nocturne-ore": "pixel art dark violet ore chunk item, Mindustry icon, black background",
    "abyssal-quartz": "pixel art blue abyssal quartz crystal item, Mindustry icon, black background",
    "tide-coral": "pixel art teal tide coral fragment item, Mindustry icon, black background",
    "ember-slag": "pixel art molten ember slag chunk item, Mindustry icon, black background",
    "pale-mythril": "pixel art pale silver mythril bar item, Mindustry icon, black background",
    "nocturne-plate": "pixel art refined nocturne metal plate item, Mindustry icon, black background",
    "abyssal-alloy": "pixel art blue-silver alloy ingot item, Mindustry icon, black background",
    "tide-composite": "pixel art layered tide composite tile item, Mindustry icon, black background",
}

BLOCK_META: dict[str, tuple[str, int]] = {
    # tiles, prompt fragment
    "shard-turret": (1, "small dual-barrel void turret"),
    "wave-scatter": (2, "scatter flak turret cyan"),
    "eclipse-beam": (2, "golden laser lancer turret"),
    "tyrant-rail": (3, "heavy railgun turret crimson"),
    "void-flak": (2, "void flak AA turret purple"),
    "aether-missile": (3, "triple missile battery cyan"),
    "ceramite-howitzer": (3, "ceramite artillery howitzer"),
    "singularity-lance": (4, "huge singularity beam lance turret"),
    "abyss-fortress": (4, "abyss fortress siege turret"),
    "storm-battery": (3, "storm scatter battery"),
    "nocturne-bolt": (2, "nocturne twin bolt turret violet"),
    "tide-pulse": (3, "tide pulse scatter turret teal"),
    "crab-howitzer": (4, "kaiju crab howitzer siege turret red"),
    "void-smelter": (2, "void smelter factory building"),
    "ceramite-forge": (3, "ceramite forge factory"),
    "aether-refinery": (3, "aether refinery building"),
    "nocturne-smelter": (2, "nocturne smelter building"),
    "abyssal-foundry": (3, "abyssal foundry building"),
    "tide-kiln": (3, "tide kiln factory"),
    "pale-foundry": (3, "pale mythril foundry"),
    "void-compressor": (2, "void compressor machine"),
    "ceramite-crucible": (2, "ceramite crucible"),
    "dark-drill": (2, "dark pneumatic drill"),
    "void-drill": (3, "void laser drill"),
    "mythril-drill": (3, "mythril heavy drill"),
    "dark-generator": (1, "small combustion generator"),
    "ember-generator": (2, "ember slag generator"),
    "aether-reactor": (3, "aether power reactor"),
    "mythril-reactor": (4, "mythril impact reactor"),
    "dark-battery": (1, "small power battery"),
    "nocturne-battery": (2, "nocturne power battery"),
    "tide-mender": (2, "tide mend projector"),
    "abyss-radar": (2, "abyss radar dish"),
    "tide-conduit": (1, "tide liquid conduit tile"),
    "void-unloader": (1, "void item unloader"),
    "ceramite-wall": (1, "ceramite wall tile"),
    "ceramite-wall-large": (2, "large ceramite wall"),
    "nocturne-wall": (1, "nocturne wall tile"),
    "nocturne-wall-large": (2, "large nocturne wall"),
    "abyssal-wall": (1, "abyssal wall tile"),
    "abyssal-wall-large": (2, "large abyssal wall"),
    "tide-wall": (1, "tide wall tile"),
    "tide-wall-large": (2, "large tide wall"),
    "mythril-wall": (1, "mythril wall tile"),
    "mythril-wall-large": (2, "large mythril wall"),
    "ember-wall": (1, "ember slag wall tile"),
    "ember-wall-large": (2, "large ember wall"),
    "dark-conveyor": (1, "dark item conveyor belt"),
    "dark-conveyor-armored": (1, "armored dark conveyor"),
    "dark-junction": (1, "dark conveyor junction"),
    "dark-router": (1, "dark item router"),
    "dark-bridge": (1, "dark bridge conveyor"),
    "dark-overflow": (1, "dark overflow gate"),
    "dark-sorter": (1, "dark item sorter"),
    "ground-fabricator": (3, "ground unit fabricator factory"),
    "naval-fabricator": (3, "naval unit fabricator factory"),
    "ground-reconstructor": (3, "additive reconstructor"),
    "ground-reconstructor-t3": (3, "tier3 reconstructor"),
    "ground-reconstructor-t4": (5, "multiplicative reconstructor"),
    "ground-reconstructor-t5": (7, "exponential reconstructor"),
    "ground-reconstructor-t6": (9, "colossal reconstructor"),
    "ground-reconstructor-t7": (11, "kaiju reconstructor cathedral"),
    "naval-reconstructor": (3, "naval additive reconstructor"),
    "naval-reconstructor-t3": (3, "naval t3 reconstructor"),
    "naval-reconstructor-t4": (5, "naval t4 reconstructor"),
    "naval-reconstructor-t5": (7, "naval t5 reconstructor"),
    "naval-reconstructor-t6": (9, "naval t6 reconstructor"),
}


def block_prompt(stem: str, desc: str) -> str:
    accents = ["violet", "teal", "crimson", "amber", "cyan", "obsidian", "pearl", "rust"]
    accent = accents[int(hashlib.md5(stem.encode()).hexdigest(), 16) % len(accents)]
    return (
        f"{STYLE_GUIDE} Mindustry BLOCK (like duo/hail/ripple/pneumatic-drill): "
        f"{desc}, {accent} accents, square footprint, riveted panels, unique for {stem}."
    )


def weapon_prompt(unit_stem: str, weapon: str, style: str, body_hint: str) -> str:
    """Tell the model: look at finished unit parts + Mindustry mounts; barrel +Y."""
    return (
        f"{STYLE_GUIDE} WEAPON MOUNT sprite for unit '{unit_stem}', name '{weapon}', style '{style}'. "
        f"Reuse palette/outline from finished body: {body_hint}. "
        f"Breech at BOTTOM of sheet, barrel/muzzle toward TOP (+Y). "
        f"Separate small mount — not a body crop. Match Mindustry weapon sheet conventions "
        f"(duo barrel, hail breech, toxopid claw segments stacked toward tip)."
    )


def gen_weapon_from_body(stem: str, weapon: str, style: str = "gun") -> None:
    """Build a proper +Y mount tinted from the finished body (never a random body crop as the gun)."""
    body_p = SPR_U / f"{stem}.png"
    if not body_p.exists():
        return
    body = Image.open(body_p).convert("RGBA")
    # sample palette from finished body
    px = body.load()
    samples = []
    for y in range(0, body.height, max(1, body.height // 8)):
        for x in range(0, body.width, max(1, body.width // 8)):
            r, g, b, a = px[x, y]
            if a > 200:
                samples.append((r, g, b))
    samples.sort(key=lambda c: c[0] + c[1] + c[2])
    dark = samples[len(samples) // 6] if samples else (40, 40, 40)
    mid = samples[len(samples) // 2] if samples else (100, 100, 100)
    hi = samples[-len(samples) // 6] if samples else (200, 200, 200)
    # procedural Mindustry-like gun (palette locked to body)
    w, h = 18, 24
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([2, h // 2, w - 3, h - 2], fill=dark + (255,), outline=hi + (255,))
    bw = max(4, w // 3)
    d.rectangle([w // 2 - bw // 2, 1, w // 2 + bw // 2, h // 2 + 2], fill=mid + (255,), outline=hi + (255,))
    d.rectangle([w // 2 - 1, 0, w // 2 + 1, 4], fill=hi + (255,))
    harden(trim(im, 2)).save(SPR_U / f"{weapon}.png")
    for suf, yw, yh, yfill in (
        ("-breech", w - 2, h // 2, dark),
        ("-barrel0", max(5, w // 4), h - 4, mid),
        ("-barrel1", max(5, w // 4), h - 4, mid),
        ("-muzzle", max(8, w // 2), 8, hi),
        ("-mag", max(10, w // 2), max(8, h // 2), mid),
        ("-coil", max(10, w // 2), max(8, h // 2), mid),
    ):
        part = Image.new("RGBA", (yw, yh), (0, 0, 0, 0))
        pd = ImageDraw.Draw(part)
        pd.rectangle([0, 0, yw - 1, yh - 1], fill=yfill + (255,), outline=hi + (255,))
        harden(trim(part, 1)).save(SPR_U / f"{weapon}{suf}.png")
    # keep prompt string available for external AI pipelines
    _ = weapon_prompt(stem, weapon, style, f"colors dark={dark} mid={mid} hi={hi}")


def main(limit: int | None = None) -> None:
    SPR_U.mkdir(parents=True, exist_ok=True)
    SPR_B.mkdir(parents=True, exist_ok=True)
    SPR_I.mkdir(parents=True, exist_ok=True)

    jobs: list[tuple[str, str, callable]] = []

    for stem, (prompt, size) in UNIT_PROMPTS.items():
        jobs.append(("unit", stem, lambda s=stem, p=prompt, z=size: save_unit_body(s, fetch_image(p, 384, 384), z)))

    for stem, prompt in ITEM_PROMPTS.items():
        jobs.append(("item", stem, lambda s=stem, p=prompt: save_item(s, fetch_image(p, 128, 128))))

    for stem, (tiles, desc) in BLOCK_META.items():
        prompt = block_prompt(stem, desc)
        jobs.append(("block", stem, lambda s=stem, p=prompt, t=tiles: save_block(s, fetch_image(p, 256, 256), t)))

    # ores
    for ore, desc in [
        ("ore-void-shard", "void purple ore patches on stone"),
        ("ore-ceramite", "ceramite orange ore patches"),
        ("ore-nocturne", "nocturne violet ore patches"),
        ("ore-abyssal-quartz", "abyssal blue quartz ore"),
        ("ore-tide-coral", "tide coral ore patches"),
        ("ore-ember-slag", "ember slag ore patches"),
        ("ore-pale-mythril", "pale mythril ore patches"),
    ]:
        for i in range(1, 4):
            stem = f"{ore}{i}"
            prompt = f"top-down pixel art Mindustry ore tile variant {i}, {desc}, sparse crystals, black background, unique layout"
            jobs.append(("ore", stem, lambda s=stem, p=prompt: fit_square(fetch_image(p, 128, 128), 32).save(SPR_B / f"{s}.png")))

    if limit:
        jobs = jobs[:limit]

    ok = fail = 0
    for kind, stem, fn in jobs:
        try:
            print(f"[{kind}] {stem} ...", flush=True)
            fn()
            ok += 1
            time.sleep(0.35)  # be polite to free API
        except Exception as e:
            fail += 1
            print(f"  FAIL {stem}: {e}", flush=True)

    # conveyor frames from base
    for stem in ("dark-conveyor", "dark-conveyor-armored"):
        base = SPR_B / f"{stem}.png"
        if base.exists():
            im = Image.open(base).convert("RGBA")
            for a in range(5):
                for b in range(4):
                    frame = ImageEnhance.Brightness(im).enhance(0.85 + 0.03 * a)
                    frame = ImageOps.mirror(frame) if b % 2 else frame
                    frame.save(SPR_B / f"{stem}-{a}-{b}.png")

    # reconstructor in/out/top from body
    for p in SPR_B.glob("*-reconstructor*.png"):
        if any(p.name.endswith(s) for s in ("-in.png", "-out.png", "-top.png", "-heat.png")):
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
        if any(k in p.stem for k in ("smelter", "forge", "foundry", "kiln", "refinery", "crucible", "compressor")):
            if p.stem.endswith("-top"):
                continue
            top = Image.new("RGBA", Image.open(p).size, (0, 0, 0, 0))
            d = ImageDraw.Draw(top)
            cx, cy = top.width // 2, top.height // 2
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 200, 120, 200))
            top.save(p.with_name(p.stem + "-top.png"))

    print(json.dumps({"ok": ok, "fail": fail, "cache": str(CACHE)}))


if __name__ == "__main__":
    import sys

    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(lim)
