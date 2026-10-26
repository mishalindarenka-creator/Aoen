"""Expand single-line RegionPart objects — Mindustry HJSON chokes on nested braces."""
from __future__ import annotations

import re
from pathlib import Path

UNITS = Path(__file__).resolve().parents[1] / "content" / "units"


def expand_one(indent: str, inner: str) -> str:
    moves = None
    mm = re.search(r",?\s*moves:\s*(\[.*\])\s*$", inner)
    if mm:
        moves = mm.group(1)
        inner = inner[: mm.start()]

    fields: list[tuple[str, str]] = []
    for part in re.split(r",\s*", inner.strip()):
        part = part.strip()
        if not part or ":" not in part:
            continue
        k, v = part.split(":", 1)
        fields.append((k.strip(), v.strip()))

    if not fields:
        raise ValueError(f"no fields parsed from: {inner!r}")

    base = indent + "  "
    lines = [f"{indent}{{"]
    for k, v in fields:
        lines.append(f"{base}{k}: {v}")
    if moves:
        lines.append(f"{base}moves: [")
        for pm in re.finditer(r"\{([^{}]+)\}", moves):
            lines.append(f"{base}  {{")
            for pair in re.split(r",\s*", pm.group(1).strip()):
                if ":" not in pair:
                    continue
                k, v = pair.split(":", 1)
                lines.append(f"{base}    {k.strip()}: {v.strip()}")
            lines.append(f"{base}  }}")
        lines.append(f"{base}]")
    lines.append(f"{indent}}}")
    return "\n".join(lines)


def process(text: str) -> str:
    pattern = re.compile(r"^([ \t]*)\{([^\n]*type:\s*RegionPart[^\n]*)\}$", re.M)

    def repl(m: re.Match) -> str:
        return expand_one(m.group(1), m.group(2))

    return pattern.sub(repl, text)


def main() -> None:
    n = 0
    for path in sorted(UNITS.glob("*.hjson")):
        raw = path.read_text(encoding="utf-8-sig")
        try:
            new = process(raw)
        except ValueError as e:
            print("FAIL", path.name, e)
            continue
        # safety: never write if we created empty objects
        if re.search(r"\{\s*\}", new) and not re.search(r"\{\s*\}", raw):
            print("ABORT empty braces", path.name)
            continue
        if new != raw:
            path.write_text(new, encoding="utf-8")
            n += 1
            print("fixed", path.name)
    print("expanded inline parts in", n, "files")


if __name__ == "__main__":
    main()
