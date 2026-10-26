"""Rewrite mod.hjson / mod.json as UTF-8 without BOM (Mindustry needs meta.name).

Keeps version in sync with bump_version.py — do not hardcode an older release.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = "2.0.1"

HJSON = f"""name: aoen
displayName: Aoen
author: Paradew
description: "[#888888]Aoen[] — ores/materials/turrets/walls, MH naval, serpents, Proto Bahamut."
version: "{VER}"
minGameVersion: 160.7
dependencies: []
hidden: false
"""

JSON = f"""{{
  "name": "aoen",
  "displayName": "Aoen",
  "author": "Paradew",
  "description": "Aoen — ores/materials/turrets/walls, MH naval, serpents, Proto Bahamut.",
  "version": "{VER}",
  "minGameVersion": "160.7",
  "dependencies": [],
  "hidden": false
}}
"""


def main() -> None:
    for name, text in (("mod.hjson", HJSON), ("mod.json", JSON)):
        path = ROOT / name
        data = text.encode("utf-8")
        if data.startswith(b"\xef\xbb\xbf"):
            raise SystemExit(f"refusing to write BOM into {name}")
        path.write_bytes(data)
        head = path.read_bytes()[:16]
        print(name, "OK", VER, head)


if __name__ == "__main__":
    main()
