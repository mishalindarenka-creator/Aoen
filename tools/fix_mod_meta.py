"""Rewrite mod.hjson / mod.json as UTF-8 without BOM."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = "2.2.0"

HJSON = f"""name: aoen
displayName: Aoen
author: Paradew
description: "[#888888]Aoen[] — NH/Exo/Jababarium-style sprites; content parse fixes."
version: "{VER}"
minGameVersion: 160.7
dependencies: []
hidden: false
"""

JSON = f"""{{
  "name": "aoen",
  "displayName": "Aoen",
  "author": "Paradew",
  "description": "Aoen — NH/Exo/Jababarium-style sprites; content parse fixes.",
  "version": "{VER}",
  "minGameVersion": "160.7",
  "dependencies": [],
  "hidden": false
}}
"""


def main() -> None:
    for name, text in (("mod.hjson", HJSON), ("mod.json", JSON)):
        (ROOT / name).write_bytes(text.encode("utf-8"))
        print(name, "OK", VER)


if __name__ == "__main__":
    main()
