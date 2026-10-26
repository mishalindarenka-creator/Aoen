"""Rebuild Aoen sprites inspired by Jababarium silhouette/detail language.

Uses local Steam jababadevjababarium.zip as REFERENCE only:
hard 3-band recolor into Aoen palettes (not a verbatim asset copy).
Also emits -leg / -leg-base / -foot / -joint for legs units.
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

MOD = Path(__file__).resolve().parents[1]
SPR_U = MOD / "sprites" / "units"
SPR_B = MOD / "sprites" / "blocks"
SPR_I = MOD / "sprites" / "items"
JABA_ZIP = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Mindustry\saves\mods\jababadevjababarium.zip")
JABA_TMP = Path(os.environ.get("TEMP", ".")) / "jababarium-ref"
JABA_U = JABA_TMP / "sprites" / "units"
JABA_B = JABA_TMP / "sprites" / "blocks"
JABA_I = JABA_TMP / "sprites" / "items"

SHELL = ((36, 34, 40), (90, 82, 70), (210, 195, 150))
SHELL2 = ((40, 36, 44), (110, 90, 70), (230, 200, 130))
DAIMYO = ((48, 12, 14), (130, 32, 36), (220, 80, 70))
STEEL = ((40, 46, 56), (90, 105, 120), (180, 200, 220))
STORM = ((36, 32, 72), (90, 75, 150), (180, 170, 245))
T6 = ((16, 14, 20), (80, 60, 40), (255, 200, 90))
T7 = ((12, 8, 18), (100, 30, 40), (255, 95, 70))
SNAKE = ((40, 34, 58), (110, 95, 150), (200, 185, 235))
SLAG = ((52, 28, 16), (150, 75, 35), (240, 150, 60))
AEGIS = ((28, 52, 42), (55, 120, 90), (100, 220, 160))
GOLD = ((28, 22, 14), (130, 100, 40), (250, 210, 100))
VOID = ((18, 14, 22), (60, 45, 80), (170, 140, 220))
NAVAL = ((28, 44, 58), (55, 95, 120), (140, 205, 225))
ABYSS = ((14, 10, 28), (80, 45, 130), (210, 170, 255))


def ensure_jaba() -> None:
    if JABA_U.exists() and any(JABA_U.rglob("*.png")):
        return
    JABA_TMP.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(JABA_ZIP, "r") as zf:
        zf.extractall(JABA_TMP)


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


def tint_hard(src: Image.Image, dark, mid, hi) -> Image.Image:
    src = harden(src)
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    px, op = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            lum = (r * 299 + g * 587 + b * 114) / 1000
            c = hi if lum > 170 else mid if lum > 85 else dark
            op[x, y] = (*c, 255)
    return out


def fit(im: Image.Image, size: int) -> Image.Image:
    im = trim(im, 3)
    im.thumbnail((size - 4, size - 4), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(im, ((size - im.width) // 2, (size - im.height) // 2), im)
    return harden(canvas)


def scale_nn(im: Image.Image, scale: float) -> Image.Image:
    w = max(8, int(round(im.width * scale)))
    h = max(8, int(round(im.height * scale)))
    return im.resize((w, h), Image.Resampling.NEAREST)


def jaba_unit(name: str, suffix: str = "") -> Image.Image | None:
    """Load jababa unit part: units/<name>/<name><suffix>.png"""
    folder = JABA_U / name
    cands = [
        folder / f"{name}{suffix}.png",
        folder / f"{suffix.lstrip('-')}.png" if suffix else folder / f"{name}.png",
        JABA_U / f"{name}{suffix}.png",
    ]
    for c in cands:
        if c.exists():
            return Image.open(c).convert("RGBA")
    return None


def jaba_block(*parts: str) -> Image.Image | None:
    p = JABA_B.joinpath(*parts)
    if p.exists():
        return Image.open(p).convert("RGBA")
    # recursive search by filename
    target = parts[-1]
    for f in JABA_B.rglob(target):
        return Image.open(f).convert("RGBA")
    return None


def save_preview(stem: str, body: Image.Image) -> None:
    prev = body.copy()
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR_U / f"{stem}-preview.png")
    cell = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    d.ellipse([4, 4, 19, 19], fill=(255, 211, 127, 255))
    cell.save(SPR_U / f"{stem}-cell.png")


def save_legs_parts(stem: str, pal, leg_src: str, scale: float) -> None:
    dark, mid, hi = pal
    mapping = {
        "-leg": "",
        "-leg-base": "-leg-base",
        "-foot": "-foot",
        "-joint": "-joint",
        "-joint-base": "-joint-base",
    }
    # fallbacks: tiny/ariel for small, widow, theridion, empress, oraxia
    for out_suf, in_suf in mapping.items():
        src = jaba_unit(leg_src, in_suf if in_suf else "")
        if src is None and out_suf == "-leg":
            src = jaba_unit(leg_src, "-leg")
        if src is None:
            # synthesize simple part from palette
            if out_suf == "-foot":
                im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
                d = ImageDraw.Draw(im)
                d.ellipse([2, 2, 21, 21], fill=mid + (255,), outline=hi + (255,))
                harden(im).save(SPR_U / f"{stem}{out_suf}.png")
            elif out_suf in ("-joint", "-joint-base"):
                im = Image.new("RGBA", (14, 14), (0, 0, 0, 0))
                d = ImageDraw.Draw(im)
                d.ellipse([1, 1, 12, 12], fill=dark + (255,), outline=hi + (255,))
                harden(im).save(SPR_U / f"{stem}{out_suf}.png")
            continue
        if out_suf == "-leg" and in_suf == "":
            # body mistaken — prefer -leg
            alt = jaba_unit(leg_src, "-leg")
            if alt is not None:
                src = alt
        part = tint_hard(scale_nn(src, scale), dark, mid, hi)
        harden(trim(part, 2)).save(SPR_U / f"{stem}{out_suf}.png")


def build_legs_unit(stem: str, jab: str, size: int, pal, leg_jab: str | None = None, leg_scale: float = 0.35) -> None:
    dark, mid, hi = pal
    src = jaba_unit(jab)
    if src is None:
        print("missing unit", jab)
        return
    body = fit(tint_hard(src, dark, mid, hi), size)
    body.save(SPR_U / f"{stem}.png")
    save_preview(stem, body)
    save_legs_parts(stem, pal, leg_jab or jab, leg_scale)
    print("legs", stem, "<-", jab)


def build_body(stem: str, jab: str, size: int, pal) -> None:
    dark, mid, hi = pal
    src = jaba_unit(jab)
    if src is None:
        print("missing", jab)
        return
    body = fit(tint_hard(src, dark, mid, hi), size)
    body.save(SPR_U / f"{stem}.png")
    save_preview(stem, body)
    # mech stub leg
    leg = Image.new("RGBA", (16, 28), (0, 0, 0, 0))
    d = ImageDraw.Draw(leg)
    d.rectangle([4, 2, 11, 26], fill=mid + (255,), outline=hi + (255,))
    leg.save(SPR_U / f"{stem}-leg.png")
    print("body", stem, "<-", jab)


def weapon_from_jab(name: str, jab_unit: str, jab_part: str, pal, size: int = 48) -> None:
    dark, mid, hi = pal
    src = jaba_unit(jab_unit, jab_part)
    if src is None:
        # procedural fallback matching jababa cannon proportions
        w, h = max(14, size // 2), max(18, size)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle([2, h // 2, w - 3, h - 2], fill=dark + (255,), outline=hi + (255,))
        bw = max(4, w // 3)
        d.rectangle([w // 2 - bw // 2, 1, w // 2 + bw // 2, h // 2 + 2], fill=mid + (255,), outline=hi + (255,))
        d.rectangle([w // 2 - 1, 0, w // 2 + 1, 4], fill=hi + (255,))
        harden(trim(im, 2)).save(SPR_U / f"{name}.png")
    else:
        fit(tint_hard(src, dark, mid, hi), size).save(SPR_U / f"{name}.png")
    # parts stacked +Y
    for suf, yw, yh, col in (
        ("-breech", max(10, size // 3), max(8, size // 4), dark),
        ("-barrel0", max(5, size // 8), max(14, size // 2), mid),
        ("-barrel1", max(5, size // 8), max(14, size // 2), mid),
        ("-muzzle", max(8, size // 4), 8, hi),
        ("-mag", max(10, size // 3), max(8, size // 4), mid),
        ("-coil", max(10, size // 3), max(8, size // 4), mid),
    ):
        part = Image.new("RGBA", (yw, yh), (0, 0, 0, 0))
        d = ImageDraw.Draw(part)
        d.rectangle([0, 0, yw - 1, yh - 1], fill=col + (255,), outline=hi + (255,))
        harden(trim(part, 1)).save(SPR_U / f"{name}{suf}.png")


def claw_from_jab(prefix: str, jab_unit: str, pal, n: int = 3, scale: float = 0.4) -> None:
    dark, mid, hi = pal
    fang = jaba_unit(jab_unit, "-fang") or jaba_unit(jab_unit, "-gun") or jaba_unit(jab_unit, "-cannon")
    s = max(12, int(16 * scale * 2))
    mount = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(mount)
    d.rectangle([1, 1, s - 2, s - 2], fill=mid + (255,), outline=hi + (255,))
    harden(trim(mount, 2)).save(SPR_U / f"{prefix}.png")
    for i in range(1, n + 1):
        if fang is not None:
            seg = tint_hard(scale_nn(fang, scale * (0.55 + i * 0.08)), dark, mid, hi)
            # tip toward +Y: rotate so long axis is vertical if needed
            if seg.width > seg.height:
                seg = seg.rotate(90, expand=True, fillcolor=(0, 0, 0, 0))
            harden(trim(seg, 2)).save(SPR_U / f"{prefix}-seg{i}.png")
        else:
            w, h = 8 + i, 10 + i * 2
            seg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            sd = ImageDraw.Draw(seg)
            sd.rectangle([1, 2, w - 2, h - 1], fill=(hi if i == n else mid) + (255,), outline=dark + (255,))
            if i == n:
                sd.polygon([(2, 4), (w // 2, 0), (w - 3, 4)], fill=hi + (255,))
            harden(trim(seg, 2)).save(SPR_U / f"{prefix}-seg{i}.png")


def tint_save_block(stem: str, src: Image.Image | None, tiles: int, pal) -> None:
    dark, mid, hi = pal
    px = 32 * tiles
    if src is None:
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle([2, 2, px - 3, px - 3], fill=mid + (255,), outline=hi + (255,))
        im.save(SPR_B / f"{stem}.png")
        return
    fit(tint_hard(src, dark, mid, hi), px).save(SPR_B / f"{stem}.png")


def main() -> None:
    ensure_jaba()
    SPR_U.mkdir(parents=True, exist_ok=True)
    SPR_B.mkdir(parents=True, exist_ok=True)
    SPR_I.mkdir(parents=True, exist_ok=True)

    # --- crab / spider line (Jababarium widow→broodmother language) ---
    build_legs_unit("crab", "widow", 64, SHELL, "widow", 0.45)
    build_legs_unit("crab-t2", "theridion", 80, SHELL2, "theridion", 0.35)
    build_legs_unit("ceramtyr-daimyo", "empress", 112, DAIMYO, "empress", 0.28)
    build_legs_unit("quake-bulwark", "octoclasm", 128, STEEL, "octoclasm", 0.22)
    build_legs_unit("storm-sovereign", "oraxia", 144, STORM, "oraxia", 0.18)
    build_legs_unit("eclipse-tyrant", "broodmother", 192, T6, "broodmother", 0.12)
    build_legs_unit("crabzilla", "broodmother", 224, T7, "broodmother", 0.14)

    # --- mech line ---
    build_body("boomeranger", "fray", 64, GOLD)
    build_body("boomeranger-t2", "ripjaw", 80, GOLD)
    build_body("foundry-orbiter", "geran", 96, STEEL)
    build_body("aegis-walker", "destroyer", 112, AEGIS)
    build_body("nexus-prime", "inferno", 128, GOLD)
    build_body("apotheosis-core", "decimator", 192, T6)

    # --- naval ---
    build_body("naval", "pelagis", 64, NAVAL)
    build_body("naval-t2", "aquarail", 80, NAVAL)
    build_body("iron-reef", "brinneclaw", 96, STEEL)
    build_body("needle-skiff", "glacial", 112, NAVAL)
    build_body("leviathan-crown", "leviathan", 128, NAVAL)
    build_body("mare-imperator", "ocelexis", 192, T6)

    # serpents: keep head-like from jababa phantom/rift accents via body builders already present
    from build_snake_sprites import main as build_snakes
    from build_bahamut_sprites import main as build_bahamut

    build_snakes()
    build_bahamut()

    # --- weapons ---
    claw_from_jab("crab-claw", "empress", SHELL, 3, 0.35)
    weapon_from_jab("crab-spit", "fray", "-gun", SHELL, 32)
    claw_from_jab("crab-t2-claw", "theridion", SHELL2, 3, 0.4)
    weapon_from_jab("crab-t2-spit", "theridion", "-cannon", SHELL2, 40)
    weapon_from_jab("crab-t2-flak", "fray", "-gun", SHELL2, 36)
    claw_from_jab("ceramtyr-daimyo-claw", "empress", DAIMYO, 4, 0.45)
    weapon_from_jab("ceramtyr-daimyo-gun", "empress", "-cannon", DAIMYO, 48)
    weapon_from_jab("ceramtyr-daimyo-mortar", "empress", "-cannon", DAIMYO, 52)
    weapon_from_jab("ceramtyr-daimyo-fang", "empress", "-fang", DAIMYO, 40)

    for n, part, sc in [
        ("quake-bulwark-mortar", "-cannon", 52), ("quake-bulwark-gun", "-cannon", 44),
        ("quake-bulwark-flak", "-cannon", 40), ("quake-bulwark-missile", "-cannon", 44),
        ("quake-bulwark-rail", "-cannon", 48),
    ]:
        weapon_from_jab(n, "octoclasm", part, STEEL, sc)
    for n, part, sc in [
        ("storm-sovereign-beam", "-laser", 52), ("storm-sovereign-rail", "-cannon", 48),
        ("storm-sovereign-emp", "-cannon", 44), ("storm-sovereign-missile", "-gun", 44),
    ]:
        weapon_from_jab(n, "oraxia", part, STORM, sc)
    claw_from_jab("eclipse-tyrant-claw", "broodmother", T6, 4, 0.55)
    for n, part, sc in [
        ("eclipse-tyrant-mortar", "-cannon", 64), ("eclipse-tyrant-beam", "-laser", 56),
        ("eclipse-tyrant-missile", "-gun", 52), ("eclipse-tyrant-rail", "-cannon", 56),
    ]:
        weapon_from_jab(n, "broodmother", part, T6, sc)
    claw_from_jab("crabzilla-claw", "broodmother", T7, 5, 0.65)
    for n, part, sc in [
        ("crabzilla-mortar", "-cannon", 72), ("crabzilla-beam", "-laser", 64),
        ("crabzilla-rail", "-cannon", 64), ("crabzilla-missile", "-gun", 56),
        ("crabzilla-flak", "-cannon", 48), ("crabzilla-nova", "-laser", 72),
    ]:
        weapon_from_jab(n, "broodmother", part, T7, sc)

    # remaining guns (serpents / mechs / naval / bahamut) — jababa-flavored mounts
    gun_map = [
        ("snake-fang", "empress", "-fang", SNAKE, 32),
        ("snake-spit", "fray", "-gun", SNAKE, 32),
        ("snake-t2-fang", "empress", "-fang", SNAKE, 36),
        ("snake-t2-spit", "fray", "-gun", SNAKE, 36),
        ("snake-t2-sap", "oraxia", "-laser", SNAKE, 36),
        ("cinder-millipede-spit", "inferno", "-cannon", SLAG, 40),
        ("cinder-millipede-slag", "inferno", "-cannon", SLAG, 44),
        ("cinder-millipede-fang", "empress", "-fang", SLAG, 36),
        ("payload-serpent-hook", "fray", "-gun", AEGIS, 40),
        ("payload-serpent-spit-l", "fray", "-gun", AEGIS, 36),
        ("payload-serpent-spit-r", "fray", "-gun", AEGIS, 36),
        ("payload-serpent-rear", "destroyer", "-cannon", AEGIS, 40),
        ("payload-serpent-sap", "oraxia", "-laser", AEGIS, 36),
        ("singularity-eel-rift", "phantom", "-lightning", VOID, 44),
        ("singularity-eel-bolt", "phantom", "-cannon", VOID, 40),
        ("singularity-eel-spores", "fray", "-gun", VOID, 36),
        ("singularity-eel-missile", "decimator", "-missile-launcher", VOID, 40),
        ("ouroboros-prime-maw", "oblivion", "-laser", ABYSS, 56),
        ("ouroboros-prime-bolt", "oblivion", "-cannon", ABYSS, 48),
        ("ouroboros-prime-missile", "oblivion", "-missile-launcher", ABYSS, 48),
        ("ouroboros-prime-emp", "oblivion", "-cannon", ABYSS, 44),
        ("foundry-orbiter-laser", "inferno", "-cannon", STEEL, 48),
        ("foundry-orbiter-shotgun", "destroyer", "-cannon", STEEL, 44),
        ("foundry-orbiter-missile", "decimator", "-missile-launcher", STEEL, 44),
        ("foundry-orbiter-flak", "destroyer", "-support-cannon", STEEL, 40),
        ("aegis-walker-gun", "destroyer", "-cannon", AEGIS, 48),
        ("aegis-walker-shotgun", "destroyer", "-support-cannon", AEGIS, 44),
        ("aegis-walker-missile", "decimator", "-missile-launcher", AEGIS, 44),
        ("aegis-walker-emp", "destroyer", "-cannon", AEGIS, 44),
        ("nexus-prime-core", "inferno", "-cannon", GOLD, 52),
        ("nexus-prime-laser", "inferno", "-cannon", GOLD, 48),
        ("nexus-prime-point", "inferno", "-support-cannon", GOLD, 40),
        ("nexus-prime-missile", "decimator", "-missile-launcher", GOLD, 44),
        ("nexus-prime-flak", "destroyer", "-support-cannon", GOLD, 40),
        ("apotheosis-core-nova", "decimator", "-cannon", T6, 64),
        ("apotheosis-core-batteries", "decimator", "-cannon2", T6, 56),
        ("apotheosis-core-rail", "decimator", "-cannon", T6, 56),
        ("apotheosis-core-missile", "decimator", "-missile-launcher", T6, 52),
        ("apotheosis-core-emp", "decimator", "-support-cannon", T6, 48),
        ("naval-cannon", "leviathan", "-cannon2", NAVAL, 40),
        ("naval-torpedo", "glacial", "-cannon", NAVAL, 40),
        ("naval-flak", "aquarail", "-cannon", NAVAL, 36),
        ("naval-t2-cannon", "leviathan", "-cannon", NAVAL, 44),
        ("naval-t2-shell", "leviathan", "-cannon2", NAVAL, 44),
        ("naval-t2-laser", "leviathan", "-beam", NAVAL, 44),
        ("iron-reef-battery", "brinneclaw", "-cannon", STEEL, 48),
        ("iron-reef-flak", "aquarail", "-cannon", STEEL, 40),
        ("iron-reef-missile", "glacial", "-lance", STEEL, 44),
        ("needle-skiff-rack", "glacial", "-lance", NAVAL, 44),
        ("needle-skiff-rack-l", "glacial", "-cannon", NAVAL, 40),
        ("needle-skiff-rack-r", "glacial", "-cannon", NAVAL, 40),
        ("needle-skiff-ciws", "aquarail", "-cannon", NAVAL, 36),
        ("needle-skiff-beam", "leviathan", "-beam", NAVAL, 44),
        ("leviathan-crown-main", "leviathan", "-cannon", NAVAL, 56),
        ("leviathan-crown-flak", "leviathan", "-cannon2", NAVAL, 44),
        ("leviathan-crown-beam", "leviathan", "-beam", NAVAL, 48),
        ("leviathan-crown-torpedo", "glacial", "-lance", NAVAL, 44),
        ("leviathan-crown-rail", "ocelexis", "-cannon", NAVAL, 48),
        ("mare-imperator-main", "ocelexis", "-cannon", T6, 64),
        ("mare-imperator-ciws", "ocelexis", "-cannon2", T6, 48),
        ("mare-imperator-beam", "ocelexis", "-laser", T6, 56),
        ("mare-imperator-missile", "ocelexis", "-collapse", T6, 52),
        ("mare-imperator-rail", "ocelexis", "-lightning", T6, 56),
        ("bahamut-catastrophe", "nemesis", "-cannon", DAIMYO, 72),
        ("bahamut-skyfall", "nemesis", "-cannon2", DAIMYO, 56),
        ("bahamut-breath", "nemesis", "-photosynthesis", DAIMYO, 64),
        ("bahamut-claw", "empress", "-fang", DAIMYO, 56),
        ("bahamut-orb", "fray", "-gun", GOLD, 40),
        ("bahamut-wing-missile", "nemesis", "-web", DAIMYO, 48),
        ("bahamut-emp", "phantom", "-lightning", STORM, 48),
    ]
    for name, ju, jp, pal, sc in gun_map:
        weapon_from_jab(name, ju, jp, pal, sc)

    for lab in "abc":
        weapon_from_jab(f"boomeranger-orb-{lab}", "fray", "-gun", GOLD, 28)
    for lab in "abcde":
        weapon_from_jab(f"boomeranger-t2-orb-{lab}", "ripjaw", "-cannon", GOLD, 32)

    # --- blocks (jababa drills/turrets/conveyors language) ---
    drill = jaba_block("cryostal-drill", "cryostal-drill.png") or jaba_block("cryostal-drill.png")
    for stem, tiles, pal, extras in [
        ("dark-drill", 2, VOID, ["-rotator", "-top"]),
        ("void-drill", 3, VOID, ["-rotator", "-top"]),
        ("mythril-drill", 3, STEEL, ["-rotator", "-top", "-rim"]),
    ]:
        tint_save_block(stem, drill, tiles, pal)
        for ex in extras:
            src = jaba_block("cryostal-drill", f"cryostal-drill{ex}.png")
            tint_save_block(stem + ex, src, tiles, pal)

    # sample turrets / factories from jababa
    for stem, tiles, jabfile, pal in [
        ("shard-turret", 1, "turrets", VOID),
        ("wave-scatter", 2, "turrets", NAVAL),
        ("eclipse-beam", 2, "turrets", GOLD),
        ("tyrant-rail", 3, "turrets", DAIMYO),
        ("void-flak", 2, "turrets", VOID),
        ("aether-missile", 3, "turrets", NAVAL),
        ("ceramite-howitzer", 3, "turrets", SHELL),
        ("singularity-lance", 4, "turrets", ABYSS),
        ("abyss-fortress", 4, "turrets", ABYSS),
        ("storm-battery", 3, "turrets", STORM),
        ("nocturne-bolt", 2, "turrets", VOID),
        ("tide-pulse", 3, "turrets", NAVAL),
        ("crab-howitzer", 4, "turrets", T7),
        ("dark-generator", 1, "flux-reactor.png", SLAG),
        ("ember-generator", 2, "flux-reactor.png", SLAG),
        ("aether-reactor", 3, "flux-reactor.png", NAVAL),
        ("mythril-reactor", 4, "anti-matter-warper.png", STEEL),
        ("ground-fabricator", 3, "basic-unit-printer.png", STEEL),
        ("naval-fabricator", 3, "basic-unit-printer.png", NAVAL),
        ("ground-reconstructor", 3, "advanced-unit-printer.png", STEEL),
        ("naval-reconstructor", 3, "advanced-unit-printer.png", NAVAL),
    ]:
        if jabfile.endswith(".png"):
            src = jaba_block(jabfile)
        else:
            # first png in turrets folder
            folder = JABA_B / jabfile
            src = None
            if folder.is_dir():
                pngs = sorted(folder.glob("*.png"))
                src = Image.open(pngs[hash(stem) % len(pngs)]).convert("RGBA") if pngs else None
            else:
                src = jaba_block(jabfile)
        tint_save_block(stem, src, tiles, pal)

    # items from jababa item icons if present
    if JABA_I.exists():
        items = sorted(JABA_I.glob("*.png"))
        aoen_items = [
            "void-shard", "ceramite", "aether-dust", "nocturne-ore", "abyssal-quartz",
            "tide-coral", "ember-slag", "pale-mythril", "nocturne-plate", "abyssal-alloy", "tide-composite",
        ]
        pals = [VOID, SHELL, NAVAL, VOID, ABYSS, NAVAL, SLAG, STEEL, VOID, ABYSS, NAVAL]
        for i, stem in enumerate(aoen_items):
            src = items[i % len(items)] if items else None
            im = Image.open(src).convert("RGBA") if src else None
            dark, mid, hi = pals[i]
            if im is None:
                im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
                d = ImageDraw.Draw(im)
                d.ellipse([4, 4, 27, 27], fill=mid + (255,), outline=hi + (255,))
                im.save(SPR_I / f"{stem}.png")
            else:
                fit(tint_hard(im, dark, mid, hi), 32).save(SPR_I / f"{stem}.png")

    print("rebuild jababa-style OK", len(list(SPR_U.glob("*.png"))), "unit pngs")


if __name__ == "__main__":
    main()
