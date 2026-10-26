"""Fix RegionPart offsets: claws chain along +Y (shoot forward), gun barrels stack +Y."""
from __future__ import annotations

import re
from pathlib import Path

UNITS = Path(__file__).resolve().parents[1] / "content" / "units"


def fix_seg_xy(text: str) -> str:
    """For each -segN RegionPart, set x=0 and y=(n-1)*3."""

    def repl(m: re.Match) -> str:
        n = int(m.group(1))
        block = m.group(0)
        y = (n - 1) * 3
        block = re.sub(r"(?m)^(\s*)x:\s*-?\d+(?:\.\d+)?", rf"\1x: 0", block, count=1)
        block = re.sub(r"(?m)^(\s*)y:\s*-?\d+(?:\.\d+)?", rf"\1y: {y}", block, count=1)
        block = re.sub(
            r"\{ type: PartMove, progress: reload, x: [^,]+, y: [^,]+, rot: ([^}]+) \}",
            rf"{{ type: PartMove, progress: reload, x: 0, y: {0.4 + n * 0.15:.2f}, rot: \1 }}",
            block,
        )
        return block

    # match full RegionPart including nested PartMove braces
    return re.sub(
        r"\{\s*type:\s*RegionPart[^{}]*?suffix:\s*-seg(\d+)(?:[^{}]|\{[^{}]*\})*\}",
        repl,
        text,
        flags=re.S,
    )


def fix_gun_parts(text: str) -> str:
    def y_for(suf: str) -> int | None:
        if suf == "-breech":
            return 0
        if suf.startswith("-barrel") and suf[-1].isdigit():
            return 3 + int(suf[-1])
        if suf == "-muzzle":
            return 7
        if suf in ("-mag", "-coil"):
            return 1
        return None

    def repl(m: re.Match) -> str:
        block = m.group(0)
        suf_m = re.search(r"suffix:\s*(-\w+)", block)
        if not suf_m:
            return block
        y = y_for(suf_m.group(1))
        if y is None:
            return block
        block = re.sub(r"(?m)^(\s*)x:\s*-?\d+(?:\.\d+)?", r"\1x: 0", block, count=1)
        block = re.sub(r"(?m)^(\s*)y:\s*-?\d+(?:\.\d+)?", rf"\1y: {y}", block, count=1)
        return block

    return re.sub(
        r"\{\s*type:\s*RegionPart(?:[^{}]|\{[^{}]*\})*\}",
        repl,
        text,
        flags=re.S,
    )


def main() -> None:
    for path in sorted(UNITS.glob("*.hjson")):
        raw = path.read_text(encoding="utf-8")
        fixed = fix_gun_parts(fix_seg_xy(raw))
        if fixed != raw:
            path.write_text(fixed, encoding="utf-8")
            print("fixed", path.name)
        else:
            print("ok", path.name)


if __name__ == "__main__":
    main()
