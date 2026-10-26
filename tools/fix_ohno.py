"""Definitive oh-no fix for Mindustry mod aoen.

Root causes fixed:
1) RegionPart outline=true draws atlas.find(name+'-outline') WITHOUT found() check → error texture
2) Absolute RegionPart name mismatch → use suffix relative to weapon (mod-prefixed at parse)
3) Double-prefixed files aoen-*.png pack as aoen-aoen-* → delete them
4) Missing mount/body/segment sprites → ensure solid RGBA stubs
5) Unit outline generation edge cases → outlines: false on all units
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

MOD = Path(__file__).resolve().parents[1]
UNITS_H = MOD / "content" / "units"
SPR_U = MOD / "sprites" / "units"
SPR_B = MOD / "sprites" / "blocks"
SPR_I = MOD / "sprites" / "items"


def nuke_double_prefix() -> int:
    n = 0
    for folder in (SPR_U, SPR_B, SPR_I):
        if not folder.exists():
            continue
        for p in list(folder.rglob("aoen-*.png")):
            p.unlink()
            n += 1
            print("DEL double-prefix", p.relative_to(MOD))
    return n


def solid_rgba(path: Path, size: int = 32, color=(120, 100, 80, 255)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = max(2, size // 8)
    d.ellipse([m, m, size - 1 - m, size - 1 - m], fill=color, outline=(255, 220, 160, 255))
    im.save(path)


def visible(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 32:
        return False
    try:
        a = Image.open(path).convert("RGBA").split()[3].getextrema()
        return a is not None and a[1] >= 8
    except Exception:
        return False


def fix_unit_hjson(path: Path) -> None:
    text = path.read_text(encoding="utf-8-sig")
    # disable engine outline generation (prevents missing-outline oh-no)
    if re.search(r"(?m)^outlines:\s*", text):
        text = re.sub(r"(?m)^outlines:\s*[^\n]+", "outlines: false", text, count=1)
    else:
        text = re.sub(r"(?m)^(type:\s*\w+\s*\n)", r"\1outlines: false\n", text, count=1)

    # RegionPart: convert absolute aoen-* names → suffix, force outline false
    def part_fix(m: re.Match) -> str:
        block = m.group(0)
        # extract absolute name
        nm = re.search(r"(?m)^\s*name:\s*(aoen-[\w-]+)\s*$", block)
        if nm:
            absn = nm.group(1)
            # weapon is aoen-<stem>, part is aoen-<stem><suffix>
            # find weapon name above in file is hard; derive suffix from common pattern
            # Prefer: if name ends with -segN, suffix = -segN and drop absolute name
            sm = re.search(r"(-seg\d+)$", absn)
            if sm:
                suf = sm.group(1)
                block = re.sub(r"(?m)^\s*name:\s*aoen-[\w-]+\s*\n", f"        suffix: {suf}\n", block, count=1)
            else:
                # keep as suffix of full remaining after weapon — fallback strip to last -seg or use as suffix from last hyphen group
                # absolute name without leading aoen- as file; for RegionPart use name WITHOUT forcing double prefix:
                # Use suffix from weapon: replace name with suffix = '-' + after last weapon-like chunk
                # Safest: use name without mod prefix? NO — RegionPart absolute must be FULL atlas id.
                # Keep absolute atlas id (aoen-...) but ensure outline false — files are stem-only so atlas is aoen-stem.
                pass
        if re.search(r"(?m)^\s*outline:\s*", block):
            block = re.sub(r"(?m)^(\s*)outline:\s*[^\n]+", r"\1outline: false", block, count=1)
        else:
            block = re.sub(r"(?m)^(\s*)(type:\s*RegionPart\s*\n)", r"\1\2\1outline: false\n", block, count=1)
        return block

    text = re.sub(
        r"(?ms)^(\s*\{\s*\n\s*type:\s*RegionPart\b.*?\n\s*\})",
        part_fix,
        text,
    )

    # Also any remaining outline: true under parts
    text = re.sub(r"(?m)^(\s*)outline:\s*true\s*$", r"\1outline: false", text)

    # Convert remaining absolute RegionPart names to suffix when pattern *-segN
    def abs_to_suf(m: re.Match) -> str:
        indent, absn = m.group(1), m.group(2)
        sm = re.search(r"(-seg\d+)$", absn)
        if sm:
            return f"{indent}suffix: {sm.group(1)}"
        # leave absolute atlas name (correct if file is stem-only)
        return m.group(0)

    text = re.sub(r"(?m)^(\s*)name:\s*(aoen-[\w-]+)\s*$", abs_to_suf, text)

    path.write_text(text, encoding="utf-8")
    print("fixed hjson", path.name)


def ensure_outlines_for(path: Path) -> None:
    """Create dark outline sibling only if missing — not required when outline:false, but safe."""
    if path.name.endswith("-outline.png") or path.name.endswith("-preview.png"):
        return
    if path.name.endswith("-heat.png") or path.name.endswith("-cell.png"):
        return
    out = path.with_name(path.stem + "-outline.png")
    if visible(out):
        return
    if not visible(path):
        return
    im = Image.open(path).convert("RGBA")
    alpha = im.split()[3]
    # expand alpha as outline
    outline = Image.new("RGBA", im.size, (0, 0, 0, 0))
    px = alpha.load()
    op = outline.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            if px[x, y] < 20:
                continue
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or px[nx, ny] < 20:
                    op[x, y] = (45, 45, 55, 255)
                    break
    outline.save(out)


def ensure_required_sprites() -> None:
    SPR_U.mkdir(parents=True, exist_ok=True)
    for h in sorted(UNITS_H.glob("*.hjson")):
        stem = h.stem
        text = h.read_text(encoding="utf-8-sig")
        # body + preview
        for suf, size, col in [
            ("", 48, (70, 65, 75, 255)),
            ("-preview", 48, (90, 85, 95, 255)),
            ("-leg", 24, (60, 55, 65, 255)),
            ("-cell", 32, (255, 200, 100, 255)),
        ]:
            p = SPR_U / f"{stem}{suf}.png"
            if not visible(p):
                solid_rgba(p, size, col)
                print("stub", p.name)
        # crawl segments
        sm = re.search(r"segments:\s*(\d+)", text)
        if sm:
            n = int(sm.group(1))
            for i in range(n):
                for s in (f"-segment{i}", f"-segment-outline{i}"):
                    p = SPR_U / f"{stem}{s}.png"
                    if not visible(p):
                        solid_rgba(p, 28, (100, 80, 140, 255))
        # weapons: name: foo (not under RegionPart)
        for wm in re.finditer(r"(?m)^    name:\s*([\w-]+)\s*$", text):
            wname = wm.group(1).removeprefix("aoen-")
            p = SPR_U / f"{wname}.png"
            if not visible(p):
                solid_rgba(p, 20, (180, 150, 100, 255))
                print("stub weapon", p.name)
        # suffixes in parts
        for smx in re.finditer(r"(?m)^        suffix:\s*(-\w[\w-]*)\s*$", text):
            # need weapon name — scan backwards
            pass
        for smx in re.finditer(r"(?m)^        (?:suffix:\s*(-[\w-]+)|name:\s*aoen-([\w-]+))\s*$", text):
            suf = smx.group(1)
            absn = smx.group(2)
            if suf:
                # find preceding weapon name
                before = text[: smx.start()]
                wm = list(re.finditer(r"(?m)^    name:\s*([\w-]+)\s*$", before))
                if wm:
                    wstem = wm[-1].group(1).removeprefix("aoen-")
                    p = SPR_U / f"{wstem}{suf}.png"
                    if not visible(p):
                        solid_rgba(p, 22, (200, 160, 110, 255))
                        print("stub part", p.name)
            elif absn:
                p = SPR_U / f"{absn}.png"
                if not visible(p):
                    solid_rgba(p, 22, (200, 160, 110, 255))


def main() -> int:
    print("=== fix_ohno ===")
    n = nuke_double_prefix()
    print("removed double-prefix files:", n)
    for h in sorted(UNITS_H.glob("*.hjson")):
        fix_unit_hjson(h)
    ensure_required_sprites()
    # light outline pass for weapons (optional safety)
    for p in SPR_U.glob("*.png"):
        if "-seg" in p.name or p.name.endswith("-claw.png") or "-orb-" in p.name:
            ensure_outlines_for(p)
    print("=== fix_ohno done ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
