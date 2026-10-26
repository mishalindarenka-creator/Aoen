"""Proto Bahamut (GBF 1:1 silhouette) — black wings, red horns/claws, silver divinity shackles."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

SPR = Path(__file__).resolve().parents[1] / "sprites" / "units"

# Exact GBF Proto Bahamut palette (summon / Relink)
BLACK = (12, 10, 16, 255)
OBSIDIAN = (22, 20, 28, 255)
WING = (32, 30, 40, 255)
BONE = (190, 195, 205, 255)
BONE_DK = (90, 95, 105, 255)
SILVER = (168, 176, 188, 255)
SHACKLE = (140, 148, 160, 255)
RED = (200, 24, 36, 255)
RED_GLOW = (255, 48, 40, 255)
CRIMSON = (120, 16, 28, 255)
EYE = (255, 70, 55, 255)


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


def save(name: str, im: Image.Image) -> None:
    harden(trim(im, 2)).save(SPR / f"{name}.png")


def body() -> None:
    """Top-down Proto Bahamut torso — black wyrm, red maw core, silver collar plate."""
    w, h = 80, 108
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w // 2
    # abdomen / torso
    d.ellipse([18, 22, 61, 98], fill=BLACK, outline=BONE_DK)
    d.ellipse([22, 28, 57, 90], fill=OBSIDIAN, outline=WING)
    # armored chest (silver divinity plate)
    d.polygon([(28, 38), (52, 38), (56, 58), (40, 72), (24, 58)], fill=OBSIDIAN, outline=SILVER)
    d.ellipse([35, 48, 45, 60], fill=RED, outline=RED_GLOW)
    d.ellipse([37, 50, 43, 56], fill=RED_GLOW)
    # neck
    d.rectangle([34, 12, 46, 32], fill=BLACK, outline=BONE)
    # head — angular GBF snout
    d.polygon([(cx, 2), (58, 18), (50, 32), (30, 32), (22, 18)], fill=BLACK, outline=RED)
    d.polygon([(cx, 8), (50, 20), (cx, 28), (30, 20)], fill=OBSIDIAN, outline=CRIMSON)
    # eyes
    d.rectangle([30, 14, 34, 18], fill=EYE)
    d.rectangle([46, 14, 50, 18], fill=EYE)
    # open maw
    d.polygon([(32, 24), (cx, 36), (48, 24)], fill=CRIMSON, outline=RED_GLOW)
    # spine ridges
    for y in range(40, 92, 10):
        d.rectangle([cx - 2, y, cx + 2, y + 4], fill=BONE_DK, outline=BONE)
    save("bahamut", im)
    prev = harden(trim(im, 2))
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR / "bahamut-preview.png")


def wing(i: int, n: int = 8) -> None:
    """Black Wings of Terror — membrane + bone spar; outer tip crimson claw."""
    t = i / max(n - 1, 1)
    w = 16 + int(t * 36)
    h = 22 + int((1 - abs(t - 0.35)) * 28)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # membrane (black)
    d.polygon([(1, h // 2), (w - 2, 2), (w - 4, h // 2), (w - 2, h - 3)], fill=WING, outline=OBSIDIAN)
    d.polygon([(2, h // 2), (w - 6, 6), (w - 6, h - 7)], fill=BLACK)
    # bone spars (silver-white — GBF wing structure)
    d.line([(2, h // 2), (w - 3, 4)], fill=BONE, width=2)
    d.line([(2, h // 2), (w - 3, h // 2)], fill=BONE_DK, width=1)
    d.line([(2, h // 2), (w - 3, h - 5)], fill=BONE, width=1)
    # finger joints
    for fx in (w // 3, 2 * w // 3, w - 5):
        d.ellipse([fx - 2, h // 2 - 2, fx + 1, h // 2 + 1], fill=SILVER)
    if i >= n - 2:
        d.polygon([(w - 10, h // 2 - 5), (w - 1, h // 2), (w - 10, h // 2 + 5)], fill=RED_GLOW, outline=RED)
    save(f"bahamut-wing-{i}", im)


def horn(name: str, big: bool) -> None:
    w, h = (16, 34) if big else (12, 22)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # curved crimson horn (GBF signature)
    if "l" in name:
        d.polygon([(w - 2, h - 2), (2, 4), (6, 1), (w - 1, h - 6)], fill=RED, outline=RED_GLOW)
        d.line([(w - 3, h - 4), (5, 6)], fill=CRIMSON)
    else:
        d.polygon([(1, h - 2), (w - 3, 4), (w - 7, 1), (2, h - 6)], fill=RED, outline=RED_GLOW)
        d.line([(2, h - 4), (w - 6, 6)], fill=CRIMSON)
    save(f"bahamut-horn-{name}", im)


def shackle(kind: str) -> None:
    sizes = {
        "neck": (32, 14),
        "chest": (40, 16),
        "waist": (36, 14),
        "wrist": (18, 12),
        "wing": (22, 12),
        "divinity": (28, 18),  # Relink Divinity Shackle
    }
    w, h = sizes[kind]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=3, fill=SHACKLE, outline=SILVER)
    d.rectangle([3, 3, w - 4, h - 4], outline=BONE_DK)
    # lock
    d.ellipse([w // 2 - 4, h // 2 - 4, w // 2 + 4, h // 2 + 4], fill=BLACK, outline=BONE)
    d.rectangle([w // 2 - 1, h // 2 - 1, w // 2 + 1, h // 2 + 3], fill=SILVER)
    if kind == "divinity":
        d.polygon([(w // 2, 2), (w - 4, h // 2), (w // 2, h - 3), (4, h // 2)], outline=RED_GLOW)
    save(f"bahamut-shackle-{kind}", im)


def chain(i: int) -> None:
    w, h = 11, 18
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, w - 2, h // 2 + 2], outline=SILVER)
    d.ellipse([1, h // 2 - 3, w - 2, h - 2], outline=SILVER)
    d.rectangle([3, h // 2 - 1, w - 4, h // 2 + 1], fill=SHACKLE)
    save(f"bahamut-chain-{i}", im)


def spine(i: int) -> None:
    w, h = 10, 12 + i
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w // 2, 0), (w - 1, h - 1), (0, h - 1)], fill=OBSIDIAN, outline=BONE)
    save(f"bahamut-spine-{i}", im)


def tail(i: int, n: int = 8) -> None:
    t = i / max(n - 1, 1)
    w = max(10, int(24 - t * 14))
    h = max(14, int(28 - t * 12))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, w - 2, h - 2], fill=BLACK, outline=BONE_DK)
    d.line([(w // 2, 2), (w // 2, h - 3)], fill=RED if i % 2 == 0 else BONE_DK)
    if i == n - 1:
        d.polygon([(w // 2, h - 1), (2, h // 2), (w - 3, h // 2)], fill=RED_GLOW)
    save(f"bahamut-tail-{i}", im)


def claw_mount() -> None:
    im = Image.new("RGBA", (28, 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, 22, 18], fill=BLACK, outline=RED)
    d.polygon([(6, 16), (14, 2), (22, 16)], fill=RED, outline=RED_GLOW)
    save("bahamut-claw", im)
    for i in range(1, 5):
        w, h = 10 + i * 2, 16 - i
        seg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sd = ImageDraw.Draw(seg)
        col = RED_GLOW if i == 4 else RED if i > 1 else CRIMSON
        sd.rectangle([0, 1, w - 1, h - 2], fill=col, outline=BLACK)
        if i == 4:
            sd.polygon([(w - 4, 1), (w - 1, h // 2), (w - 4, h - 2)], fill=RED_GLOW)
        save(f"bahamut-claw-seg{i}", seg)


def weapon(name: str, style: str, w: int = 30, h: int = 22) -> None:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([2, 4, w - 3, h - 3], fill=BLACK, outline=SILVER)
    if style == "catastrophe":
        # dark nova core — Catastrophe call
        d.ellipse([6, 3, w - 7, h - 3], outline=RED_GLOW)
        d.ellipse([w // 2 - 5, h // 2 - 5, w // 2 + 5, h // 2 + 5], fill=RED, outline=BONE)
        d.ellipse([w // 2 - 2, h // 2 - 2, w // 2 + 2, h // 2 + 2], fill=RED_GLOW)
    elif style == "skyfall":
        d.polygon([(w // 2, 0), (w - 4, 10), (w // 2, 8), (4, 10)], fill=BONE, outline=SILVER)
        d.ellipse([w // 2 - 3, 10, w // 2 + 3, 16], fill=RED_GLOW)
    elif style == "breath":
        d.polygon([(w // 2, 0), (w // 2 + 7, 12), (w // 2 - 7, 12)], fill=RED_GLOW)
        d.rectangle([w // 2 - 2, 10, w // 2 + 2, h - 3], fill=RED)
    elif style == "orb":
        for ox in (-6, 0, 6):
            d.ellipse([w // 2 + ox - 3, 2, w // 2 + ox + 3, 8], fill=BONE, outline=RED_GLOW)
        d.rectangle([w // 2 - 4, 8, w // 2 + 4, h - 3], fill=OBSIDIAN, outline=SILVER)
    elif style == "emp":
        d.ellipse([5, 3, w - 6, h - 3], outline=SILVER)
        d.ellipse([w // 2 - 4, h // 2 - 4, w // 2 + 4, h // 2 + 4], fill=RED_GLOW)
    else:
        d.rectangle([w // 2 - 2, 1, w // 2 + 2, h // 2], fill=SILVER)
    save(name, im)
    # parts
    breech = Image.new("RGBA", (16, 12), (0, 0, 0, 0))
    bd = ImageDraw.Draw(breech)
    bd.rectangle([0, 1, 15, 10], fill=BLACK, outline=SILVER)
    save(f"{name}-breech", breech)
    for bi in range(2):
        b = Image.new("RGBA", (8, 18 + bi), (0, 0, 0, 0))
        bld = ImageDraw.Draw(b)
        bld.rectangle([1, 0, 6, 17 + bi], fill=WING, outline=SILVER)
        bld.rectangle([3, 0, 5, 3], fill=RED_GLOW)
        save(f"{name}-barrel{bi}", b)
    m = Image.new("RGBA", (14, 8), (0, 0, 0, 0))
    md = ImageDraw.Draw(m)
    md.polygon([(0, 4), (7, 0), (13, 4), (7, 7)], fill=SILVER)
    save(f"{name}-muzzle", m)
    if style in ("catastrophe", "breath", "emp"):
        coil = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
        cd = ImageDraw.Draw(coil)
        cd.ellipse([1, 1, 10, 10], outline=RED_GLOW)
        cd.ellipse([3, 3, 8, 8], fill=BLACK, outline=SILVER)
        save(f"{name}-coil", coil)


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    body()
    for i in range(8):
        wing(i, 8)
    for name, big in (("l", True), ("r", True), ("l2", False), ("r2", False)):
        horn(name, big)
    for k in ("neck", "chest", "waist", "wrist", "wing", "divinity"):
        shackle(k)
    for i in range(10):
        chain(i)
    for i in range(5):
        spine(i)
    for i in range(8):
        tail(i, 8)
    claw_mount()
    weapon("bahamut-catastrophe", "catastrophe", 36, 28)
    weapon("bahamut-skyfall", "skyfall", 30, 24)
    weapon("bahamut-breath", "breath", 32, 24)
    weapon("bahamut-orb", "orb", 28, 20)
    weapon("bahamut-emp", "emp", 26, 20)
    weapon("bahamut-wing-missile", "orb", 22, 18)
    print("Proto Bahamut GBF sprites OK")


if __name__ == "__main__":
    main()
