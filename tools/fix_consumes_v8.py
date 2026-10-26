"""Rewrite consumePower/consumeItems → consumes{} for Mindustry 160."""
from __future__ import annotations

import re
from pathlib import Path

BLOCKS = Path(__file__).resolve().parents[1] / "content" / "blocks"


def fix(text: str) -> str:
    # remove unknown fabricator constructTime
    text = re.sub(r"(?m)^constructTime:\s*[^\n]+\n", "", text)

    power = re.search(r"(?m)^consumePower:\s*([0-9.]+)\s*$", text)
    items = re.search(r"(?ms)^consumeItems:\s*\[(.*?)\]\s*$", text)
    buffered = re.search(r"(?m)^consumePowerBuffered:\s*([0-9.]+)\s*$", text)

    if not power and not items and not buffered:
        return text

    text = re.sub(r"(?m)^consumePower:\s*[^\n]+\n", "", text)
    text = re.sub(r"(?ms)^consumeItems:\s*\[.*?\]\s*\n", "", text)
    text = re.sub(r"(?m)^consumePowerBuffered:\s*[^\n]+\n", "", text)

    lines = []
    if power:
        lines.append(f"  power: {power.group(1)}")
    if buffered:
        lines.append(f"  powerBuffered: {buffered.group(1)}")
    if items:
        inner = items.group(1).strip()
        # keep as array
        lines.append("  items: [")
        for ln in inner.splitlines():
            ln = ln.strip().rstrip(",")
            if ln:
                lines.append(f"    {ln}")
        lines.append("  ]")

    block = "consumes: {\n" + "\n".join(lines) + "\n}\n"
    # insert after category or size
    if re.search(r"(?m)^consumes:\s*\{", text):
        return text
    if re.search(r"(?m)^size:\s*", text):
        text = re.sub(r"(?m)^(size:\s*[^\n]+\n)", r"\1" + block, text, count=1)
    else:
        text = block + text
    return text


def main() -> int:
    for p in sorted(BLOCKS.glob("*.hjson")):
        old = p.read_text(encoding="utf-8-sig")
        new = fix(old)
        if new != old:
            p.write_text(new, encoding="utf-8")
            print("consumes", p.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
