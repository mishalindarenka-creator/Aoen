"""Make all T6 colossi ~3× eclipse-tyrant footprint + richer T5 special weapons."""
from __future__ import annotations

from pathlib import Path

UNITS = Path(__file__).resolve().parents[1] / "content" / "units"

# eclipse baseline was hitSize 48 → ×3 = 144
T6 = {
    "eclipse-tyrant": dict(
        health=90000, armor=60, speed=0.18, hitSize=144, range=220,
        legCount=12, legLength=120, shadowElevation=0.55, groundLayer=80,
    ),
    "ouroboros-prime": dict(
        health=82000, armor=50, speed=0.7, hitSize=120, range=170,
        segments=14, crushDamage=12,
    ),
    "apotheosis-core": dict(
        health=88000, armor=58, speed=0.22, hitSize=132, range=200,
    ),
    "mare-imperator": dict(
        health=95000, armor=55, speed=0.35, hitSize=150, range=240,
    ),
}


def set_fields(text: str, fields: dict) -> str:
    import re

    for k, v in fields.items():
        if re.search(rf"(?m)^{k}:\s*", text):
            text = re.sub(rf"(?m)^({k}:\s*)([^\n#]+)", rf"\g<1>{v}", text, count=1)
        else:
            text = re.sub(r"(?m)^(outlines:\s*[^\n]+\n)", rf"\1{k}: {v}\n", text, count=1)
    return text


def main() -> int:
    for stem, fields in T6.items():
        p = UNITS / f"{stem}.hjson"
        if not p.exists():
            print("missing", stem)
            continue
        text = p.read_text(encoding="utf-8-sig")
        text = set_fields(text, fields)
        p.write_text(text, encoding="utf-8")
        print("T6 colossus", stem, "hitSize", fields.get("hitSize"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
