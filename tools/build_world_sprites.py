"""Build item/block sprites WITHOUT mod prefix (stem.png → atlas aoen-stem)."""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageOps

MOD = Path(__file__).resolve().parents[1]
SPR_B = MOD / "sprites" / "blocks"
SPR_I = MOD / "sprites" / "items"
TMP = Path(os.environ.get("TEMP", ".")) / "mindustry-sprites"
BASE = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites"


def fetch(rel: str) -> Image.Image | None:
    dest = TMP / rel.replace("/", "__")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.stat().st_size < 40:
        try:
            urllib.request.urlretrieve(f"{BASE}/{rel}", dest)
        except Exception as e:
            print("skip", rel, e)
            return None
    try:
        return Image.open(dest).convert("RGBA")
    except Exception:
        return None


def tint(im: Image.Image, dark, mid, hi) -> Image.Image:
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    px, op = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            lum = (r * 299 + g * 587 + b * 114) / 1000
            c = hi if lum > 185 else mid if lum > 95 else dark
            op[x, y] = (c[0], c[1], c[2], a)
    return out


def solid(size: int, mid, hi, shape: str = "hex") -> Image.Image:
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = 3
    if shape == "hex":
        c = size // 2
        d.polygon(
            [(c, m), (size - m, c // 2 + 2), (size - m, size - c // 2 - 2), (c, size - m), (m, size - c // 2 - 2), (m, c // 2 + 2)],
            fill=mid,
            outline=hi,
        )
    elif shape == "sq":
        d.rounded_rectangle([m, m, size - m - 1, size - m - 1], radius=3, fill=mid, outline=hi)
    else:
        d.ellipse([m, m, size - m - 1, size - m - 1], fill=mid, outline=hi)
    return im


def item_icon(name: str, mid, hi) -> None:
    SPR_I.mkdir(parents=True, exist_ok=True)
    base = fetch("items/item-copper.png") or fetch("items/item-coal.png") or fetch("items/item-scrap.png")
    if base:
        tint(base, (20, 16, 24, 255), mid, hi).save(SPR_I / f"{name}.png")
    else:
        solid(32, mid, hi, "sq").save(SPR_I / f"{name}.png")


def save_block(name: str, im: Image.Image) -> None:
    SPR_B.mkdir(parents=True, exist_ok=True)
    im.save(SPR_B / f"{name}.png")


def conveyor_frames(stem: str, palette) -> None:
    dark, mid, hi = palette
    any_ok = False
    for a in range(5):
        for b in range(4):
            src = fetch(f"blocks/distribution/conveyors/conveyor-{a}-{b}.png")
            if src is None:
                continue
            any_ok = True
            tint(src, dark, mid, hi).save(SPR_B / f"{stem}-{a}-{b}.png")
    if not any_ok:
        for a in range(5):
            for b in range(4):
                im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
                d = ImageDraw.Draw(im)
                d.rectangle([2, 8, 29, 23], fill=mid, outline=hi)
                d.polygon([(10, 10), (22, 16), (10, 22)], fill=hi)
                im.save(SPR_B / f"{stem}-{a}-{b}.png")
    icon = fetch("blocks/distribution/conveyors/conveyor-0-0.png")
    if icon:
        tint(icon, dark, mid, hi).save(SPR_B / f"{stem}.png")
    else:
        solid(32, mid, hi, "sq").save(SPR_B / f"{stem}.png")


def copy_tint(van_rel: str, out_name: str, palette, size: int | None = None) -> None:
    dark, mid, hi = palette
    src = fetch(van_rel)
    if src is None:
        save_block(out_name, solid(size or 32, mid, hi, "sq"))
        return
    if size and (src.width != size or src.height != size):
        src = src.resize((size, size), Image.Resampling.NEAREST)
    save_block(out_name, tint(src, dark, mid, hi))


def ore_variants(stem: str, palette) -> None:
    dark, mid, hi = palette
    for i in range(1, 4):
        src = fetch(f"blocks/environment/ore-copper{i}.png") or fetch(f"blocks/environment/ore-copper-{i}.png")
        if src is None:
            im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            for _ in range(8):
                import random

                x, y = random.randint(4, 24), random.randint(4, 24)
                d.ellipse([x, y, x + 6, y + 5], fill=mid, outline=hi)
            save_block(f"{stem}{i}", im)
        else:
            save_block(f"{stem}{i}", tint(src, dark, mid, hi))


def turret(name: str, size: int, palette, van: str = "duo") -> None:
    dark, mid, hi = palette
    px = 32 * size
    src = (
        fetch(f"blocks/turrets/{van}/{van}.png")
        or fetch(f"blocks/turrets/{van}.png")
    )
    if src:
        im = tint(src.resize((px - 6, px - 6), Image.Resampling.NEAREST), dark, mid, hi)
        canvas = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        canvas.alpha_composite(im, ((px - im.width) // 2, (px - im.height) // 2))
        save_block(name, canvas)
    else:
        save_block(name, solid(px, mid, hi, "hex"))
    heat = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(heat)
    d.ellipse([px // 2 - 6, px // 2 - 6, px // 2 + 6, px // 2 + 6], fill=(255, 80, 40, 180))
    heat.save(SPR_B / f"{name}-heat.png")


def crafter(name: str, size: int, palette, top: bool = True) -> None:
    dark, mid, hi = palette
    px = 32 * size
    src = fetch("blocks/production/silicon-smelter.png") or fetch("blocks/production/graphite-press.png")
    if src:
        im = tint(src.resize((px, px), Image.Resampling.NEAREST), dark, mid, hi)
    else:
        im = solid(px, mid, hi, "sq")
    save_block(name, im)
    if top:
        top_im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(top_im)
        d.ellipse([px // 2 - 8, px // 2 - 8, px // 2 + 8, px // 2 + 8], fill=(*hi[:3], 200))
        top_im.save(SPR_B / f"{name}-top.png")


def wall(name: str, size: int, palette) -> None:
    dark, mid, hi = palette
    px = 32 * size
    src = fetch("blocks/walls/titanium-wall.png" if size == 1 else "blocks/walls/titanium-wall-large.png")
    if src:
        save_block(name, tint(src.resize((px, px), Image.Resampling.NEAREST), dark, mid, hi))
    else:
        save_block(name, solid(px, mid, hi, "sq"))


def drill(name: str, size: int, palette) -> None:
    dark, mid, hi = palette
    px = 32 * size
    src = fetch("blocks/drills/pneumatic-drill.png" if size == 2 else "blocks/drills/laser-drill.png")
    if src:
        save_block(name, tint(src.resize((px, px), Image.Resampling.NEAREST), dark, mid, hi))
    else:
        save_block(name, solid(px, mid, hi, "sq"))


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    SPR_B.mkdir(parents=True, exist_ok=True)
    SPR_I.mkdir(parents=True, exist_ok=True)

    VOID = ((18, 12, 28, 255), (70, 50, 110, 255), (180, 140, 255, 255))
    CER = ((40, 18, 16, 255), (120, 55, 40, 255), (230, 160, 90, 255))
    AETH = ((16, 40, 48, 255), (40, 120, 140, 255), (120, 230, 240, 255))
    DARK = ((28, 28, 36, 255), (70, 70, 88, 255), (200, 190, 140, 255))
    GOLD = ((30, 24, 12, 255), (120, 90, 30, 255), (255, 210, 90, 255))

    item_icon("void-shard", VOID[1], VOID[2])
    item_icon("ceramite", CER[1], CER[2])
    item_icon("aether-dust", AETH[1], AETH[2])

    ore_variants("ore-void-shard", VOID)
    ore_variants("ore-ceramite", CER)

    conveyor_frames("dark-conveyor", DARK)
    conveyor_frames("dark-conveyor-armored", CER)
    copy_tint("blocks/distribution/junction.png", "dark-junction", DARK)
    copy_tint("blocks/distribution/router.png", "dark-router", DARK)
    copy_tint("blocks/distribution/bridge-conveyor.png", "dark-bridge", DARK)
    copy_tint("blocks/distribution/overflow-gate.png", "dark-overflow", DARK)
    copy_tint("blocks/distribution/sorter.png", "dark-sorter", DARK)

    turret("shard-turret", 1, VOID, "duo")
    turret("wave-scatter", 2, AETH, "scatter")
    turret("eclipse-beam", 2, GOLD, "lancer")
    turret("tyrant-rail", 3, CER, "ripple")

    crafter("void-smelter", 2, VOID, True)
    crafter("ceramite-forge", 3, CER, True)
    crafter("aether-refinery", 3, AETH, True)
    drill("dark-drill", 2, DARK)
    drill("void-drill", 3, VOID)
    wall("ceramite-wall", 1, CER)
    wall("ceramite-wall-large", 2, CER)
    copy_tint("blocks/power/combustion-generator.png", "dark-generator", GOLD, 32)
    copy_tint("blocks/power/battery.png", "dark-battery", AETH, 32)

    print("world sprites blocks", len(list(SPR_B.glob("*.png"))), "items", len(list(SPR_I.glob("*.png"))))
    # kill any double-prefix leftovers (oh no source)
    for folder in (SPR_B, SPR_I, MOD / "sprites" / "units"):
        for p in list(folder.glob("aoen-*.png")):
            print("remove double", p.relative_to(MOD))
            p.unlink()


if __name__ == "__main__":
    main()
