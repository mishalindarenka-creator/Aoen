"""Ensure sprites exist on disk WITHOUT mod prefix.

Mindustry packs sprites/units/crab.png as atlas region 'aoen-crab'
(mod name + filename). Files named aoen-crab.png become aoen-aoen-crab → oh no.
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw

MOD = Path(__file__).resolve().parents[1]
UNITS = MOD / "content" / "units"
SPR = MOD / "sprites" / "units"
MIN_ALPHA = 8
PAL = ((62, 58, 66, 255), (255, 211, 127, 255), (120, 22, 28, 255), (140, 120, 200, 255), (55, 95, 120, 255))


def disk_name(atlas_or_stem: str) -> str:
    """Atlas id aoen-X → filename X.png"""
    return atlas_or_stem.removeprefix("aoen-")


def visible(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 32:
        return False
    try:
        a = Image.open(path).convert("RGBA").split()[3].getextrema()
        return a is not None and a[1] >= MIN_ALPHA
    except Exception:
        return False


def stub(size: int, color) -> Image.Image:
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    p = max(1, size // 8)
    d.ellipse([p, p, size - 1 - p, size - 1 - p], fill=color, outline=(255, 230, 180, 255))
    return im


def parse_unit(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    stem = path.stem  # crab → unit id aoen-crab, sprite file crab.png
    utype = "legs"
    m = re.search(r"^type:\s*(\w+)", text, re.M)
    if m:
        utype = m.group(1)
    segs = 0
    if utype == "crawl":
        sm = re.search(r"segments:\s*(\d+)", text)
        segs = int(sm.group(1)) if sm else (8 if "t2" in stem else 6)
    weapons = []
    hits = list(re.finditer(r"(?m)^    name:\s*([\w-]+)\s*$", text))
    for i, wm in enumerate(hits):
        raw = wm.group(1)
        start, end = wm.end(), hits[i + 1].start() if i + 1 < len(hits) else len(text)
        block = text[start:end]
        if not re.search(r"\b(bullet|reload|parts|shootY)\b", block):
            continue
        # weapon file stem = raw without aoen-
        wstem = disk_name(raw)
        suf = re.findall(r"suffix:\s*(-\w[\w-]*)", block)
        # RegionPart name: aoen-crab-claw-seg1 → file crab-claw-seg1.png
        absn = [disk_name(n) for n in re.findall(r"(?m)^ {8}name:\s*([\w-]+)\s*$", block)]
        spr = [disk_name(n) for n in re.findall(r"sprite:\s*([\w-]+)", block)]
        weapons.append((wstem, suf, absn + spr))
    # unit-level RegionPart suffixes (bahamut wings/chains/tail/…)
    body_suf = re.findall(r"(?ms)^parts:\s*\[(.*?)(?=^weapons:|\Z)", text)
    unit_parts = []
    if body_suf:
        unit_parts = re.findall(r"suffix:\s*(-\w[\w-]*)", body_suf[0])
    return {"stem": stem, "type": utype, "segments": segs, "weapons": weapons, "unit_parts": unit_parts}


def required(info: dict) -> list[tuple[Path, str, int]]:
    s = info["stem"]
    out = [(SPR / f"{s}.png", "body", 0), (SPR / f"{s}-preview.png", "preview", 0)]
    if info["type"] == "legs":
        out += [(SPR / f"{s}-leg.png", "leg", 0), (SPR / f"{s}-cell.png", "cell", 0)]
    elif info["type"] == "mech":
        out.append((SPR / f"{s}-leg.png", "leg", 0))
    elif info["type"] == "crawl":
        for i in range(info["segments"]):
            out += [(SPR / f"{s}-segment{i}.png", "seg", i), (SPR / f"{s}-segment-outline{i}.png", "seg", i)]
    for wi, (wstem, sufs, absn) in enumerate(info["weapons"]):
        out.append((SPR / f"{wstem}.png", "weapon", wi))
        for si, suf in enumerate(sufs):
            out.append((SPR / f"{wstem}{suf}.png", "part", si))
        for si, n in enumerate(absn):
            out.append((SPR / f"{n}.png", "part", si + 50))
    for si, suf in enumerate(info.get("unit_parts") or []):
        out.append((SPR / f"{s}{suf}.png", "upart", si))
    return out


def ensure(info: dict) -> list[str]:
    fixed = []
    body_p = SPR / f"{info['stem']}.png"
    if not visible(body_p):
        stub(48, PAL[0]).save(body_p)
        fixed.append(str(body_p.relative_to(MOD)))
    body = Image.open(body_p).convert("RGBA") if visible(body_p) else None
    for path, kind, idx in required(info):
        if visible(path):
            continue
        im = stub(48 if kind == "preview" else 24, PAL[idx % len(PAL)])
        if kind == "preview" and body is not None:
            im = body.resize((48, 48), Image.Resampling.NEAREST)
        path.parent.mkdir(parents=True, exist_ok=True)
        im.save(path)
        fixed.append(str(path.relative_to(MOD)))
    return fixed


def discover() -> list[dict]:
    SPR.mkdir(parents=True, exist_ok=True)
    return [parse_unit(p) for p in sorted(UNITS.glob("*.hjson"))]


def main() -> int:
    # delete wrongly double-prefixed leftovers
    for p in list(SPR.glob("aoen-*.png")):
        p.unlink()
        print("removed double-prefix", p.name)
    fixed, n = [], 0
    for info in discover():
        n += len(required(info))
        fixed.extend(ensure(info))
    missing = [str(p.relative_to(MOD)) for info in discover() for p, _, _ in required(info) if not visible(p)]
    print(f"ensure_unit_sprites: fixed {len(fixed)} / {n}" if fixed else f"ensure_unit_sprites: OK ({n})")
    if missing:
        print("STILL MISSING")
        for x in missing:
            print(" ", x)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
