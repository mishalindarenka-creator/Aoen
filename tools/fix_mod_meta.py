"""Rewrite mod.hjson / mod.json as UTF-8 without BOM (Mindustry needs meta.name)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = "2.1.0"

HJSON = f"""name: aoen
displayName: Aoen
author: Paradew
description: "[#888888]Aoen[] — Crabzilla T7, redrawn crabs, expanded world blocks."
version: "{VER}"
minGameVersion: 160.7
dependencies: []
hidden: false
"""

JSON = f"""{{
  "name": "aoen",
  "displayName": "Aoen",
  "author": "Paradew",
  "description": "Aoen — Crabzilla T7, redrawn crabs, expanded world blocks.",
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
        print(name, "OK", VER)


if __name__ == "__main__":
    main()
