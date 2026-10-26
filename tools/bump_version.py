from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = "2.3.0"
HJSON = f"""name: aoen
displayName: Aoen
author: Paradew
description: "[#888888]Aoen[] — unique AI-generated textures for units/blocks/items."
version: "{VER}"
minGameVersion: 160.7
dependencies: []
hidden: false
"""
JSON = f"""{{
  "name": "aoen",
  "displayName": "Aoen",
  "author": "Paradew",
  "description": "Aoen — unique AI-generated textures for units/blocks/items.",
  "version": "{VER}",
  "minGameVersion": "160.7",
  "dependencies": [],
  "hidden": false
}}
"""
(ROOT / "mod.hjson").write_bytes(HJSON.encode("utf-8"))
(ROOT / "mod.json").write_bytes(JSON.encode("utf-8"))
print("bumped", VER)
