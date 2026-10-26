from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = "1.9.1"
HJSON = f"""name: aoen
displayName: Aoen
author: Paradew
description: "[#888888]Aoen[] — MH/jababarium naval, Calamity serpents, JS weapons, Bahamut."
version: "{VER}"
minGameVersion: 160.7
dependencies: []
hidden: false
"""
JSON = f"""{{
  "name": "aoen",
  "displayName": "Aoen",
  "author": "Paradew",
  "description": "Aoen — MH/jababarium naval, Calamity serpents, JS weapons, Bahamut.",
  "version": "{VER}",
  "minGameVersion": "160.7",
  "dependencies": [],
  "hidden": false
}}
"""
(ROOT / "mod.hjson").write_bytes(HJSON.encode("utf-8"))
(ROOT / "mod.json").write_bytes(JSON.encode("utf-8"))
print("bumped", VER)
