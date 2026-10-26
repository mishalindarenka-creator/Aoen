"""Jababarium-style multi-part weapon mounts for Aoen units.

Each weapon gets: base mount + breech + barrel0/1 + muzzle (+ coil/mag for some styles).
Stem names only (no aoen- prefix).
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


def trim(im: Image.Image, pad: int = 1) -> Image.Image:
    im = harden(im)
    bbox = im.getbbox()
    if not bbox:
        return im
    c = im.crop(bbox)
    out = Image.new("RGBA", (c.width + pad * 2, c.height + pad * 2), (0, 0, 0, 0))
    out.paste(c, (pad, pad), c)
    return harden(out)


def save(name: str, im: Image.Image) -> None:
    harden(trim(im)).save(SPR / f"{name}.png")


def mount(name: str, w: int, h: int, dark, mid, hi, style: str) -> None:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 2, w - 2, h - 2], fill=dark, outline=hi)
    d.rectangle([2, 3, w - 3, h - 3], outline=mid)
    if style in ("gun", "autocannon", "twin"):
        d.rectangle([w // 2 - 2, 0, w // 2 + 2, h // 2], fill=hi)
        if style == "twin":
            d.rectangle([w // 2 - 5, 1, w // 2 - 3, h // 2 - 1], fill=mid)
            d.rectangle([w // 2 + 3, 1, w // 2 + 5, h // 2 - 1], fill=mid)
    elif style in ("laser", "beam"):
        d.rectangle([3, h // 2 - 1, w - 4, h // 2 + 1], fill=hi)
        d.ellipse([w // 2 - 3, 1, w // 2 + 3, 7], fill=hi, outline=dark)
    elif style == "rail":
        d.rectangle([w // 2 - 3, 0, w // 2 + 3, h - 3], fill=mid, outline=hi)
        for y in range(3, h - 4, 4):
            d.ellipse([w // 2 - 5, y, w // 2 + 5, y + 3], outline=hi)
    elif style == "missile":
        for ox in (-4, 0, 4):
            d.ellipse([w // 2 + ox - 2, 1, w // 2 + ox + 2, 7], fill=hi)
            d.rectangle([w // 2 + ox - 1, 6, w // 2 + ox + 1, h - 3], fill=mid)
    elif style == "art":
        d.ellipse([w // 2 - 5, 1, w // 2 + 5, 11], fill=mid, outline=hi)
        d.rectangle([w // 2 - 2, 8, w // 2 + 2, h - 2], fill=hi)
    elif style == "flak":
        d.rectangle([w // 2 - 4, 0, w // 2 - 1, h // 2], fill=hi)
        d.rectangle([w // 2 + 1, 0, w // 2 + 4, h // 2], fill=hi)
    elif style == "sap":
        d.polygon([(w // 2, 0), (w - 3, h // 2), (w // 2, h - 2), (3, h // 2)], fill=hi, outline=dark)
    elif style == "fang":
        d.polygon([(2, h - 2), (w // 2, 1), (w - 3, h - 2)], fill=hi, outline=dark)
    elif style == "emp":
        d.ellipse([3, 2, w - 4, h - 3], outline=hi)
        d.ellipse([w // 2 - 3, h // 2 - 3, w // 2 + 3, h // 2 + 3], fill=hi)
    elif style == "flame":
        d.polygon([(w // 2, 0), (w // 2 + 5, 8), (w // 2 - 5, 8)], fill=hi)
        d.rectangle([w // 2 - 2, 7, w // 2 + 2, h - 2], fill=mid)
    save(name, im)

    # parts
    breech = Image.new("RGBA", (max(w - 2, 10), max(h - 4, 8)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(breech)
    bd.rectangle([0, 1, breech.width - 1, breech.height - 2], fill=dark, outline=hi)
    bd.rectangle([2, 3, breech.width - 3, breech.height - 4], outline=mid)
    save(f"{name}-breech", breech)

    for bi in range(2):
        bw, bh = max(6, w // 4 + bi), max(14, h + bi * 2)
        barrel = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        bld = ImageDraw.Draw(barrel)
        bld.rectangle([1, 0, bw - 2, bh - 1], fill=mid, outline=hi)
        bld.rectangle([bw // 2 - 1, 0, bw // 2 + 1, 4], fill=hi)
        save(f"{name}-barrel{bi}", barrel)

    muzzle = Image.new("RGBA", (max(w // 2, 10), 8), (0, 0, 0, 0))
    md = ImageDraw.Draw(muzzle)
    md.polygon([(0, 4), (muzzle.width // 2, 0), (muzzle.width - 1, 4), (muzzle.width // 2, 7)], fill=hi)
    save(f"{name}-muzzle", muzzle)

    if style in ("laser", "beam", "rail", "emp"):
        coil = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
        cd = ImageDraw.Draw(coil)
        cd.ellipse([1, 1, 10, 10], outline=hi)
        cd.ellipse([3, 3, 8, 8], fill=mid, outline=hi)
        save(f"{name}-coil", coil)

    if style == "missile":
        mag = Image.new("RGBA", (14, 10), (0, 0, 0, 0))
        md2 = ImageDraw.Draw(mag)
        md2.rectangle([1, 1, 12, 8], fill=dark, outline=hi)
        for ox in (3, 7):
            md2.ellipse([ox, 2, ox + 3, 6], fill=hi)
        save(f"{name}-mag", mag)


# palette shortcuts
STEEL = ((40, 46, 56, 255), (78, 90, 104, 255), (170, 190, 210, 255))
GOLD = ((28, 22, 14, 255), (120, 95, 35, 255), (245, 205, 90, 255))
DAIMYO = ((48, 12, 14, 255), (110, 28, 32, 255), (210, 70, 70, 255))
STORM = ((36, 32, 72, 255), (78, 68, 140, 255), (170, 160, 240, 255))
AEGIS = ((28, 52, 42, 255), (48, 110, 82, 255), (90, 210, 150, 255))
NAVAL = ((28, 44, 58, 255), (52, 88, 112, 255), (130, 195, 215, 255))
SHELL = ((36, 34, 40, 255), (68, 64, 72, 255), (160, 150, 130, 255))
VOID = ((18, 14, 22, 255), (55, 42, 70, 255), (160, 130, 210, 255))
SLAG = ((52, 28, 16, 255), (140, 70, 30, 255), (230, 140, 55, 255))
T6 = ((16, 14, 20, 255), (70, 55, 40, 255), (255, 200, 90, 255))
ABYSS = ((14, 10, 28, 255), (70, 40, 120, 255), (200, 160, 255, 255))
SNAKE = ((40, 34, 58, 255), (100, 88, 140, 255), (190, 175, 230, 255))


def gun_parts_block(indent: str = "    ") -> str:
    """HJSON RegionPart stack reused conceptually — actual HJSON written per-unit."""
    return ""


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    specs = [
        # crab line
        ("crab-spit", SHELL, "gun", 20, 14),
        ("crab-t2-spit", SHELL, "gun", 22, 14),
        ("crab-t2-flak", SHELL, "flak", 20, 12),
        ("ceramtyr-daimyo-gun", DAIMYO, "twin", 24, 14),
        ("ceramtyr-daimyo-mortar", DAIMYO, "art", 26, 16),
        ("ceramtyr-daimyo-fang", DAIMYO, "fang", 22, 14),
        # mech line
        ("foundry-orbiter-laser", STEEL, "laser", 24, 14),
        ("foundry-orbiter-shotgun", STEEL, "gun", 24, 14),
        ("foundry-orbiter-missile", STEEL, "missile", 22, 14),
        ("foundry-orbiter-flak", STEEL, "flak", 20, 12),
        ("aegis-walker-gun", AEGIS, "twin", 24, 14),
        ("aegis-walker-shotgun", AEGIS, "gun", 24, 14),
        ("aegis-walker-missile", AEGIS, "missile", 22, 14),
        ("aegis-walker-emp", AEGIS, "emp", 22, 14),
        ("nexus-prime-core", GOLD, "art", 28, 16),
        ("nexus-prime-laser", GOLD, "laser", 26, 14),
        ("nexus-prime-point", GOLD, "rail", 26, 14),
        ("nexus-prime-missile", GOLD, "missile", 24, 14),
        ("nexus-prime-flak", GOLD, "flak", 22, 12),
        ("apotheosis-core-nova", T6, "laser", 32, 18),
        ("apotheosis-core-batteries", T6, "twin", 28, 16),
        ("apotheosis-core-rail", T6, "rail", 30, 16),
        ("apotheosis-core-missile", T6, "missile", 26, 14),
        ("apotheosis-core-emp", T6, "emp", 26, 14),
        # legs T4-T6
        ("quake-bulwark-mortar", STEEL, "art", 28, 16),
        ("quake-bulwark-gun", STEEL, "twin", 24, 14),
        ("quake-bulwark-flak", STEEL, "flak", 22, 12),
        ("quake-bulwark-missile", STEEL, "missile", 24, 14),
        ("quake-bulwark-rail", STEEL, "rail", 26, 14),
        ("storm-sovereign-beam", STORM, "beam", 28, 16),
        ("storm-sovereign-rail", STORM, "rail", 26, 14),
        ("storm-sovereign-emp", STORM, "emp", 24, 14),
        ("storm-sovereign-missile", STORM, "missile", 24, 14),
        ("eclipse-tyrant-claw", T6, "fang", 30, 18),
        ("eclipse-tyrant-mortar", T6, "art", 32, 18),
        ("eclipse-tyrant-beam", T6, "beam", 30, 16),
        ("eclipse-tyrant-missile", T6, "missile", 28, 16),
        ("eclipse-tyrant-rail", T6, "rail", 28, 16),
        # naval
        ("naval-cannon", NAVAL, "gun", 22, 14),
        ("naval-torpedo", NAVAL, "missile", 20, 12),
        ("naval-flak", NAVAL, "flak", 18, 12),
        ("naval-t2-cannon", NAVAL, "twin", 24, 14),
        ("naval-t2-shell", NAVAL, "art", 24, 14),
        ("naval-t2-laser", NAVAL, "laser", 22, 12),
        ("iron-reef-battery", STEEL, "art", 26, 14),
        ("iron-reef-flak", STEEL, "flak", 22, 12),
        ("iron-reef-missile", STEEL, "missile", 22, 12),
        ("needle-skiff-rack", NAVAL, "missile", 24, 14),
        ("needle-skiff-rack-l", NAVAL, "missile", 22, 12),
        ("needle-skiff-rack-r", NAVAL, "missile", 22, 12),
        ("needle-skiff-ciws", NAVAL, "flak", 20, 12),
        ("needle-skiff-beam", NAVAL, "laser", 22, 12),
        ("leviathan-crown-main", DAIMYO, "art", 28, 16),
        ("leviathan-crown-flak", NAVAL, "flak", 22, 12),
        ("leviathan-crown-beam", STORM, "beam", 26, 14),
        ("leviathan-crown-torpedo", NAVAL, "missile", 24, 14),
        ("leviathan-crown-rail", STORM, "rail", 26, 14),
        ("mare-imperator-main", T6, "art", 32, 18),
        ("mare-imperator-ciws", T6, "flak", 24, 14),
        ("mare-imperator-beam", T6, "beam", 28, 16),
        ("mare-imperator-missile", T6, "missile", 26, 14),
        ("mare-imperator-rail", T6, "rail", 28, 16),
        # snakes
        ("snake-fang", SNAKE, "fang", 20, 14),
        ("snake-spit", SNAKE, "gun", 18, 12),
        ("snake-t2-fang", SNAKE, "fang", 22, 14),
        ("snake-t2-spit", SNAKE, "gun", 20, 12),
        ("snake-t2-sap", SNAKE, "sap", 20, 12),
        ("cinder-millipede-spit", SLAG, "flame", 22, 14),
        ("cinder-millipede-slag", SLAG, "art", 22, 14),
        ("cinder-millipede-fang", SLAG, "fang", 20, 12),
        ("payload-serpent-hook", AEGIS, "gun", 22, 14),
        ("payload-serpent-spit-l", AEGIS, "gun", 18, 12),
        ("payload-serpent-spit-r", AEGIS, "gun", 18, 12),
        ("payload-serpent-rear", AEGIS, "art", 20, 12),
        ("payload-serpent-sap", AEGIS, "sap", 20, 12),
        ("singularity-eel-rift", VOID, "beam", 24, 14),
        ("singularity-eel-bolt", VOID, "sap", 22, 12),
        ("singularity-eel-spores", VOID, "gun", 22, 12),
        ("singularity-eel-missile", VOID, "missile", 22, 12),
        ("ouroboros-prime-maw", ABYSS, "beam", 28, 16),
        ("ouroboros-prime-bolt", ABYSS, "laser", 26, 14),
        ("ouroboros-prime-missile", ABYSS, "missile", 24, 14),
        ("ouroboros-prime-emp", ABYSS, "emp", 24, 14),
    ]
    for name, pal, style, w, h in specs:
        mount(name, w, h, pal[0], pal[1], pal[2], style)
    print("weapon sprites:", len(specs), "mounts (+parts)")


if __name__ == "__main__":
    main()
