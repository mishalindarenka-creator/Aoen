"""Tune legs-unit locomotion to Mindustry/Jababarium spider style."""
from __future__ import annotations

import re
from pathlib import Path

UNITS = Path(__file__).resolve().parents[1] / "content" / "units"

# hitSize-scaled spider presets (widow→broodmother language)
PRESETS = {
        "crab": dict(
        legCount=8, legGroupSize=2, legLength=14, legSpeed=0.32, legForwardScl=1.4,
        legBaseOffset=3, legMoveSpace=1.15, legExtension=-7, legPairOffset=2,
        legLengthScl=1, legMaxLength=1.75, legMinLength=0.75, rippleScale=0.4,
        shadowElevation=0.12, groundLayer=60,
    ),
    "crab-t2": dict(
        legCount=8, legGroupSize=2, legLength=18, legSpeed=0.28, legForwardScl=1.45,
        legBaseOffset=4, legMoveSpace=1.2, legExtension=-8, legPairOffset=2,
        legLengthScl=1, legMaxLength=1.75, legMinLength=0.75, rippleScale=0.45,
        shadowElevation=0.16, groundLayer=61,
    ),
    "ceramtyr-daimyo": dict(
        legCount=8, legGroupSize=4, legLength=24, legSpeed=0.24, legForwardScl=1.5,
        legBaseOffset=6, legMoveSpace=1.25, legExtension=-9, legPairOffset=4,
        legLengthScl=1, legMaxLength=1.8, legMinLength=0.7, rippleScale=0.55,
        shadowElevation=0.22, groundLayer=62,
    ),
    "quake-bulwark": dict(
        legCount=8, legGroupSize=4, legLength=32, legSpeed=0.2, legForwardScl=1.45,
        legBaseOffset=8, legMoveSpace=1.3, legExtension=-10, legPairOffset=4,
        legLengthScl=1, legMaxLength=1.85, legMinLength=0.7, rippleScale=0.6,
        shadowElevation=0.28, groundLayer=65,
    ),
    "storm-sovereign": dict(
        legCount=8, legGroupSize=4, legLength=40, legSpeed=0.18, legForwardScl=1.5,
        legBaseOffset=10, legMoveSpace=1.35, legExtension=-12, legPairOffset=5,
        legLengthScl=1, legMaxLength=1.9, legMinLength=0.65, rippleScale=0.7,
        shadowElevation=0.35, groundLayer=70,
    ),
    "eclipse-tyrant": dict(
        legCount=10, legGroupSize=5, legLength=90, legSpeed=0.14, legForwardScl=1.55,
        legBaseOffset=18, legMoveSpace=1.4, legExtension=-16, legPairOffset=6,
        legLengthScl=1, legMaxLength=1.95, legMinLength=0.6, rippleScale=1.0,
        shadowElevation=0.5, groundLayer=80,
    ),
    "crabzilla": dict(
        legCount=12, legGroupSize=4, legLength=130, legSpeed=0.11, legForwardScl=1.6,
        legBaseOffset=26, legMoveSpace=1.45, legExtension=-20, legPairOffset=7,
        legLengthScl=1, legMaxLength=2.0, legMinLength=0.55, rippleScale=1.2,
        shadowElevation=0.6, groundLayer=85,
    ),
}

FLAGS = """
lockLegBase: true
allowLegStep: true
legContinuousMove: true
hovering: true
flipBackLeg: true
"""


def upsert(text: str, key: str, value) -> str:
    pat = rf"(?m)^{re.escape(key)}:\s*.*$"
    line = f"{key}: {value}"
    if re.search(pat, text):
        return re.sub(pat, line, text, count=1)
    # insert after type: legs block header — after researchCostMultiplier or hitSize
    m = re.search(r"(?m)^(hitSize:\s*.*)$", text)
    if m:
        return text[: m.end()] + "\n" + line + text[m.end() :]
    return text + "\n" + line + "\n"


def ensure_flags(text: str) -> str:
    for line in FLAGS.strip().splitlines():
        key = line.split(":")[0].strip()
        if re.search(rf"(?m)^{re.escape(key)}:", text):
            text = upsert(text, key, line.split(":", 1)[1].strip())
        else:
            m = re.search(r"(?m)^(hovering:\s*.*)$", text)
            if m:
                text = text[: m.end()] + "\n" + line + text[m.end() :]
            else:
                text = text.replace("type: legs\n", "type: legs\n" + line + "\n", 1)
    return text


def main() -> None:
    for stem, preset in PRESETS.items():
        path = UNITS / f"{stem}.hjson"
        if not path.exists():
            print("skip", stem)
            continue
        text = path.read_text(encoding="utf-8")
        for k, v in preset.items():
            text = upsert(text, k, v)
        text = ensure_flags(text)
        # remove broken tiny min length leftovers if duplicated oddly — already upserted
        path.write_text(text, encoding="utf-8")
        print("legs", stem)


if __name__ == "__main__":
    main()
