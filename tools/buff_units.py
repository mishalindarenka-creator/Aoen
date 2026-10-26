"""Set ABSOLUTE unit stats (safe to re-run). Strong vs vanilla."""
from __future__ import annotations

import re
from pathlib import Path

UNITS = Path(__file__).resolve().parents[1] / "content" / "units"

# health, armor, speed, range, damages (in file order), reloads (optional same order)
STATS: dict[str, dict] = {
    "crab": {"health": 700, "armor": 7, "speed": 0.62, "range": 50, "dmg": [48], "reload": [14]},
    "crab-t2": {"health": 2200, "armor": 12, "speed": 0.55, "range": 58, "dmg": [72], "reload": [12]},
    "ceramtyr-daimyo": {"health": 4800, "armor": 18, "speed": 0.48, "range": 78, "dmg": [110], "reload": [9]},
    "quake-bulwark": {"health": 11000, "armor": 28, "speed": 0.32, "range": 100, "dmg": [240], "reload": [28]},
    "storm-sovereign": {"health": 24000, "armor": 34, "speed": 0.36, "range": 130, "dmg": [72], "reload": [40]},
    "eclipse-tyrant": {"health": 52000, "armor": 48, "speed": 0.3, "range": 155, "dmg": [130, 320], "reload": [11, 36]},
    "snake": {"health": 620, "armor": 4, "speed": 1.2, "range": 24, "dmg": [], "reload": []},
    "snake-t2": {"health": 1800, "armor": 9, "speed": 1.25, "range": 40, "dmg": [], "reload": []},
    "cinder-millipede": {"health": 3400, "armor": 12, "speed": 1.05, "range": 42, "dmg": [36], "reload": [16]},
    "payload-serpent": {"health": 5600, "armor": 15, "speed": 1.35, "range": 36, "dmg": [28], "reload": [14]},
    "singularity-eel": {"health": 18000, "armor": 24, "speed": 0.95, "range": 78, "dmg": [150], "reload": [18]},
    "ouroboros-prime": {"health": 48000, "armor": 38, "speed": 1.0, "range": 110, "dmg": [58], "reload": [14]},
    "boomeranger": {"health": 680, "armor": 5, "speed": 0.58, "range": 48, "dmg": [32, 32, 32], "reload": [24, 24, 24]},
    "boomeranger-t2": {"health": 2100, "armor": 12, "speed": 0.52, "range": 56, "dmg": [38, 38, 38, 38, 38], "reload": [20, 20, 20, 20, 20]},
    "foundry-orbiter": {"health": 4000, "armor": 16, "speed": 0.45, "range": 72, "dmg": [18], "reload": [8]},
    "aegis-walker": {"health": 7200, "armor": 26, "speed": 0.42, "range": 62, "dmg": [78], "reload": [9]},
    "nexus-prime": {"health": 22000, "armor": 32, "speed": 0.38, "range": 100, "dmg": [200], "reload": [22]},
    "apotheosis-core": {"health": 50000, "armor": 46, "speed": 0.34, "range": 145, "dmg": [65, 80], "reload": [16, 10]},
    "naval": {"health": 1000, "armor": 7, "speed": 1.15, "range": 55, "dmg": [28, 40], "reload": [14, 28]},
    "naval-t2": {"health": 2400, "armor": 13, "speed": 0.98, "range": 70, "dmg": [14, 55], "reload": [8, 22]},
    "iron-reef": {"health": 4200, "armor": 18, "speed": 0.78, "range": 105, "dmg": [95], "reload": [18]},
    "needle-skiff": {"health": 5600, "armor": 16, "speed": 1.15, "range": 88, "dmg": [42], "reload": [10]},
    "leviathan-crown": {"health": 24000, "armor": 30, "speed": 0.62, "range": 140, "dmg": [280, 40], "reload": [32, 6]},
    "mare-imperator": {"health": 56000, "armor": 44, "speed": 0.55, "range": 175, "dmg": [380, 32, 48], "reload": [28, 5, 50]},
}


def set_field(text: str, key: str, value) -> str:
    pat = rf"(?m)^({key}:\s*)([^\n#]+)"
    if re.search(pat, text):
        return re.sub(pat, rf"\g<1>{value}", text, count=1)
    return text


def replace_seq(text: str, key: str, values: list) -> str:
    if not values:
        return text
    it = iter(values)

    def repl(m: re.Match) -> str:
        try:
            v = next(it)
        except StopIteration:
            return m.group(0)
        return f"{m.group(1)}{v}"

    return re.sub(rf"(?m)^(\s*{key}:\s*)([0-9.]+)", repl, text)


def buff_file(path: Path) -> None:
    key = path.stem
    if key not in STATS:
        print("skip", key)
        return
    s = STATS[key]
    text = path.read_text(encoding="utf-8-sig")
    text = set_field(text, "health", s["health"])
    text = set_field(text, "armor", s["armor"])
    text = set_field(text, "speed", s["speed"])
    text = set_field(text, "range", s["range"])
    text = replace_seq(text, "damage", s.get("dmg", []))
    text = replace_seq(text, "reload", s.get("reload", []))
    path.write_text(text, encoding="utf-8")
    print(f"buffed {key}: {s['health']}hp / {s['armor']}ar")


def main() -> int:
    for p in sorted(UNITS.glob("*.hjson")):
        buff_file(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
