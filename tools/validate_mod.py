from __future__ import annotations

import sys
from pathlib import Path

MOD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOD / "tools"))
from ensure_unit_sprites import discover, required, visible  # noqa: E402

SPR_B = MOD / "sprites" / "blocks"
SPR_I = MOD / "sprites" / "items"

FACTORY_BLOCKS = [
    "ground-fabricator",
    "ground-reconstructor",
    "ground-reconstructor-t3",
    "ground-reconstructor-t4",
    "ground-reconstructor-t5",
    "ground-reconstructor-t6",
    "naval-fabricator",
    "naval-reconstructor",
    "naval-reconstructor-t3",
    "naval-reconstructor-t4",
    "naval-reconstructor-t5",
    "naval-reconstructor-t6",
]

WORLD_BASE = [
    "dark-conveyor",
    "dark-conveyor-armored",
    "dark-junction",
    "dark-router",
    "dark-bridge",
    "dark-overflow",
    "dark-sorter",
    "shard-turret",
    "wave-scatter",
    "eclipse-beam",
    "tyrant-rail",
    "void-smelter",
    "ceramite-forge",
    "aether-refinery",
    "dark-drill",
    "void-drill",
    "ceramite-wall",
    "ceramite-wall-large",
    "dark-generator",
    "dark-battery",
]

ITEMS = ["void-shard", "ceramite", "aether-dust"]


def main() -> int:
    missing = []
    # double-prefix check
    for folder in (MOD / "sprites" / "units", SPR_B, SPR_I):
        for p in folder.glob("aoen-*.png"):
            missing.append(f"DOUBLE-PREFIX {p.relative_to(MOD)}")

    for info in discover():
        for path, _, _ in required(info):
            if not visible(path):
                missing.append(str(path.relative_to(MOD)))

    for bid in FACTORY_BLOCKS:
        for suf in ("", "-top", "-in", "-out"):
            if "fabricator" in bid and suf != "":
                continue
            bp = SPR_B / f"{bid}{suf}.png"
            if suf in ("", "-top") and not bp.exists():
                missing.append(str(bp.relative_to(MOD)))
            if "reconstructor" in bid and suf in ("-in", "-out") and not bp.exists():
                missing.append(str(bp.relative_to(MOD)))
            if bp.exists() and not visible(bp):
                missing.append(f"{bp.relative_to(MOD)} (transparent)")

    for bid in WORLD_BASE:
        bp = SPR_B / f"{bid}.png"
        if not bp.exists() or not visible(bp):
            missing.append(str(bp.relative_to(MOD)))

    # conveyor frames
    for stem in ("dark-conveyor", "dark-conveyor-armored"):
        for a in range(5):
            for b in range(4):
                bp = SPR_B / f"{stem}-{a}-{b}.png"
                if not bp.exists():
                    missing.append(str(bp.relative_to(MOD)))

    for ore in ("ore-void-shard", "ore-ceramite"):
        for i in range(1, 4):
            bp = SPR_B / f"{ore}{i}.png"
            if not bp.exists():
                missing.append(str(bp.relative_to(MOD)))

    for it in ITEMS:
        ip = SPR_I / f"{it}.png"
        if not ip.exists() or not visible(ip):
            missing.append(str(ip.relative_to(MOD)))

    if missing:
        print("MISSING", len(missing))
        for x in sorted(set(missing))[:80]:
            print(" ", x)
        if len(set(missing)) > 80:
            print(" ...")
        return 1
    print("validate_mod: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
