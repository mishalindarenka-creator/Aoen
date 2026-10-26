"""Rewrite mod.hjson / mod.json as UTF-8 without BOM (Mindustry needs meta.name)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HJSON = """name: aoen
displayName: Aoen
author: Paradew
description: "[#888888]Aoen[] — JS API layer: custom bullets/abilities, Proto Bahamut, serpents, T1–T6."
version: "1.7.0"
minGameVersion: 160.7
dependencies: []
hidden: false
"""

JSON = """{
  "name": "aoen",
  "displayName": "Aoen",
  "author": "Paradew",
  "description": "Aoen — JS API layer, Proto Bahamut, serpents, T1-T6.",
  "version": "1.7.0",
  "minGameVersion": "160.7",
  "dependencies": [],
  "hidden": false
}
"""


def main() -> None:
    for name, text in (("mod.hjson", HJSON), ("mod.json", JSON)):
        path = ROOT / name
        data = text.encode("utf-8")
        if data.startswith(b"\xef\xbb\xbf"):
            raise SystemExit(f"refusing to write BOM into {name}")
        path.write_bytes(data)
        head = path.read_bytes()[:16]
        print(name, "OK", head)


if __name__ == "__main__":
    main()
