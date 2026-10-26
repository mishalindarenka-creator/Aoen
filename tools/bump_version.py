from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HJSON = """name: aoen
displayName: Aoen
author: Paradew
description: "[#888888]Aoen[] — Calamity-style trail serpents, JS weapons, Proto Bahamut, T1-T6."
version: "1.8.0"
minGameVersion: 160.7
dependencies: []
hidden: false
"""
JSON = """{
  "name": "aoen",
  "displayName": "Aoen",
  "author": "Paradew",
  "description": "Aoen — Calamity-style trail serpents, JS weapons, Proto Bahamut, T1-T6.",
  "version": "1.8.0",
  "minGameVersion": "160.7",
  "dependencies": [],
  "hidden": false
}
"""
(ROOT / "mod.hjson").write_bytes(HJSON.encode("utf-8"))
(ROOT / "mod.json").write_bytes(JSON.encode("utf-8"))
meta = ROOT / "tools" / "fix_mod_meta.py"
meta.write_text(
    meta.read_text(encoding="utf-8").replace("1.7.0", "1.8.0"),
    encoding="utf-8",
)
print("bumped 1.8.0")
