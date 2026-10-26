"""Bump hitSize to match larger top-down sprites."""
from __future__ import annotations

import re
from pathlib import Path

UNITS = Path(__file__).resolve().parents[1] / "content" / "units"

HIT = {
    "crab": 11,
    "crab-t2": 13,
    "ceramtyr-daimyo": 18,
    "quake-bulwark": 22,
    "storm-sovereign": 28,
    "eclipse-tyrant": 36,
    "snake": 10,
    "snake-t2": 12,
    "cinder-millipede": 16,
    "payload-serpent": 18,
    "singularity-eel": 22,
    "ouroboros-prime": 28,
    "boomeranger": 10,
    "boomeranger-t2": 13,
    "foundry-orbiter": 18,
    "aegis-walker": 22,
    "nexus-prime": 28,
    "apotheosis-core": 32,
    "naval": 12,
    "naval-t2": 15,
    "iron-reef": 20,
    "needle-skiff": 24,
    "leviathan-crown": 32,
    "mare-imperator": 40,
}


def main() -> int:
    for p in sorted(UNITS.glob("*.hjson")):
        if p.stem not in HIT:
            continue
        text = p.read_text(encoding="utf-8-sig")
        hs = HIT[p.stem]
        if re.search(r"(?m)^hitSize:\s*", text):
            text = re.sub(r"(?m)^hitSize:\s*[^\n]+", f"hitSize: {hs}", text, count=1)
        else:
            text = re.sub(r"(?m)^(health:\s*[^\n]+\n)", rf"\1hitSize: {hs}\n", text, count=1)
        p.write_text(text, encoding="utf-8")
        print(p.stem, hs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
