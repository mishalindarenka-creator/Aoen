"""Proto Bahamut (Granblue Fantasy) — black wings, red horns/claws, silver shackles, segmented tail."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

SPR = Path(__file__).resolve().parents[1] / "sprites" / "units"

# GBF Proto Bahamut palette
BLACK = (18, 16, 22, 255)
WING = (28, 26, 34, 255)
WING_HI = (70, 68, 82, 255)
SILVER = (160, 168, 180, 255)
SILVER_DK = (70, 76, 88, 255)
RED = (180, 28, 36, 255)
RED_HI = (240, 70, 55, 255)
EYE = (255, 90, 70, 255)


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
    """Top-down dark dragon torso — elongated, red chest core, silver collar."""
    w, h = 72, 96
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # torso oval
    d.ellipse([16, 18, 55, 88], fill=BLACK, outline=WING_HI)
    d.ellipse([20, 24, 51, 80], outline=WING)
    # chest plate
    d.polygon([(28, 40), (44, 40), (48, 58), (36, 70), (24, 58)], fill=WING, outline=SILVER)
    d.ellipse([32, 48, 40, 58], fill=RED, outline=RED_HI)
    # neck
    d.rectangle([30, 8, 42, 28], fill=BLACK, outline=WING_HI)
    # head diamond
    d.polygon([(36, 2), (48, 14), (36, 26), (24, 14)], fill=BLACK, outline=RED)
    d.point((32, 12), fill=EYE)
    d.point((40, 12), fill=EYE)
    # jaw
    d.polygon([(28, 20), (36, 28), (44, 20)], fill=WING, outline=RED_HI)
    save("bahamut", im)
    prev = harden(trim(im, 2))
    prev.thumbnail((64, 64), Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
    canvas.save(SPR / "bahamut-preview.png")


def wing_seg(i: int, total: int = 6) -> None:
    """Membrane panel: longer outward, black with silver bone edge. Drawn for LEFT; mirror in JSON."""
    t = i / max(total - 1, 1)
    w = 18 + int(t * 28)
    h = 28 + int((1 - abs(t - 0.4)) * 22)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # membrane triangle-ish
    d.polygon([(2, h // 2), (w - 2, 4), (w - 2, h - 4)], fill=WING, outline=WING_HI)
    d.line([(2, h // 2), (w - 3, 6)], fill=SILVER, width=1)
    d.line([(2, h // 2), (w - 3, h - 6)], fill=SILVER_DK, width=1)
    # red claw tip on outer segments
    if i >= total - 2:
        d.polygon([(w - 8, h // 2 - 4), (w - 1, h // 2), (w - 8, h // 2 + 4)], fill=RED_HI)
    save(f"bahamut-wing-{i}", im)


def horn(side: str) -> None:
    w, h = 14, 28
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if side == "l":
        d.polygon([(12, 26), (2, 4), (10, 2), (13, 24)], fill=RED, outline=RED_HI)
    else:
        d.polygon([(2, 26), (12, 4), (4, 2), (1, 24)], fill=RED, outline=RED_HI)
    save(f"bahamut-horn-{side}", im)


def shackle(kind: str) -> None:
    sizes = {"neck": (28, 12), "chest": (36, 14), "waist": (32, 12), "wing": (20, 10)}
    w, h = sizes[kind]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=3, fill=SILVER_DK, outline=SILVER)
    d.rectangle([w // 2 - 2, 2, w // 2 + 2, h - 3], fill=SILVER)
    # lock nub
    d.ellipse([w // 2 - 3, h // 2 - 3, w // 2 + 3, h // 2 + 3], fill=BLACK, outline=SILVER)
    save(f"bahamut-shackle-{kind}", im)


def chain_link(i: int) -> None:
    w, h = 10, 16
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, w - 2, h // 2 + 1], outline=SILVER)
    d.ellipse([1, h // 2 - 2, w - 2, h - 2], outline=SILVER)
    d.rectangle([3, h // 2 - 1, w - 4, h // 2 + 1], fill=SILVER_DK)
    save(f"bahamut-chain-{i}", im)


def tail_seg(i: int, total: int = 7) -> None:
    t = i / max(total - 1, 1)
    w = max(10, int(22 - t * 12))
    h = max(14, int(26 - t * 10))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, w - 2, h - 2], fill=BLACK, outline=WING_HI)
    d.line([(w // 2, 2), (w // 2, h - 3)], fill=RED if i % 2 == 0 else SILVER_DK)
    if i == total - 1:
        d.polygon([(w // 2, h - 2), (2, h // 2), (w - 3, h // 2)], fill=RED_HI)
    save(f"bahamut-tail-{i}", im)


def weapon_mount(name: str, style: str, w: int = 28, h: int = 20) -> None:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([2, 4, w - 3, h - 3], fill=BLACK, outline=SILVER)
    if style == "breath":
        d.polygon([(w // 2, 0), (w // 2 + 6, 10), (w // 2 - 6, 10)], fill=RED_HI)
        d.rectangle([w // 2 - 2, 8, w // 2 + 2, h - 4], fill=RED)
    elif style == "nova":
        d.ellipse([6, 4, w - 7, h - 3], outline=SILVER)
        d.ellipse([w // 2 - 4, h // 2 - 4, w // 2 + 4, h // 2 + 4], fill=RED_HI)
    elif style == "missile":
        d.rectangle([w // 2 - 3, 1, w // 2 + 3, h - 4], fill=WING_HI, outline=SILVER)
        d.ellipse([w // 2 - 4, 0, w // 2 + 4, 8], fill=RED)
    elif style == "claw":
        d.polygon([(4, h - 2), (w // 2, 2), (w - 5, h - 2)], fill=RED, outline=RED_HI)
    else:
        d.rectangle([w // 2 - 2, 1, w // 2 + 2, h // 2], fill=SILVER)
    save(name, im)


def claw_parts(prefix: str, n: int = 4) -> None:
    for i in range(1, n + 1):
        w, h = 10 + i * 2, 16 - i
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        col = RED_HI if i == n else RED if i > 1 else (120, 20, 28, 255)
        d.rectangle([0, 1, w - 1, h - 2], fill=col, outline=BLACK)
        if i == n:
            d.polygon([(w - 4, 1), (w - 1, h // 2), (w - 4, h - 2)], fill=RED_HI)
        save(f"{prefix}-seg{i}", im)
    # mount already from weapon_mount


def gun_parts(prefix: str, barrels: int = 3) -> None:
    """Jababarium-style multi-barrel / breech / muzzle stack."""
    # breech
    im = Image.new("RGBA", (18, 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 2, 16, 12], fill=BLACK, outline=SILVER)
    d.rectangle([4, 4, 13, 10], outline=WING_HI)
    save(f"{prefix}-breech", im)
    for i in range(barrels):
        bw, bh = 8, 18 + i * 2
        bim = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bim)
        bd.rectangle([1, 0, bw - 2, bh - 1], fill=WING, outline=SILVER)
        bd.rectangle([bw // 2 - 1, 0, bw // 2 + 1, 4], fill=RED_HI)
        save(f"{prefix}-barrel{i}", bim)
    # muzzle flash plate
    mim = Image.new("RGBA", (14, 8), (0, 0, 0, 0))
    md = ImageDraw.Draw(mim)
    md.polygon([(0, 4), (7, 0), (13, 4), (7, 7)], fill=SILVER_DK, outline=SILVER)
    save(f"{prefix}-muzzle", mim)


def main() -> None:
    SPR.mkdir(parents=True, exist_ok=True)
    body()
    for i in range(6):
        wing_seg(i, 6)
    horn("l")
    horn("r")
    for k in ("neck", "chest", "waist", "wing"):
        shackle(k)
    for i in range(8):
        chain_link(i)
    for i in range(7):
        tail_seg(i, 7)
    weapon_mount("bahamut-breath", "breath", 32, 24)
    weapon_mount("bahamut-catastrophe", "nova", 36, 28)
    weapon_mount("bahamut-wing-missile", "missile", 22, 18)
    weapon_mount("bahamut-claw", "claw", 24, 20)
    weapon_mount("bahamut-emp", "nova", 26, 20)
    claw_parts("bahamut-claw", 4)
    gun_parts("bahamut-breath", 2)
    gun_parts("bahamut-catastrophe", 3)
    print("bahamut sprites ok")


if __name__ == "__main__":
    main()
