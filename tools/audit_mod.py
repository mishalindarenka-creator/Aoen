"""Audit Aoen content for Mindustry load-time failures."""
from __future__ import annotations

import re
from pathlib import Path

MOD = Path(__file__).resolve().parents[1]
CONTENT = MOD / "content"
SPR_U = MOD / "sprites" / "units"
SPR_B = MOD / "sprites" / "blocks"
SPR_I = MOD / "sprites" / "items"

VALID_STATUS = {
    "none",
    "burning",
    "freezing",
    "unmoving",
    "slow",
    "fast",
    "wet",
    "muddy",
    "melting",
    "sapped",
    "tarred",
    "overdrive",
    "overclock",
    "shielded",
    "shocked",
    "blasted",
    "corroded",
    "boss",
    "spore-slowed",
    "disarmed",
    "electrified",
    "invincible",
    "dynamic",
}
# mod statuses
for p in (CONTENT / "status").glob("*.hjson"):
    VALID_STATUS.add(p.stem)
    VALID_STATUS.add(f"aoen-{p.stem}")

INVALID_HIT = {"freeze"}  # use freezing

KNOWN_FX = {
    "none",
    "shootSmall",
    "shootBig",
    "shootSnap",
    "sparkShoot",
    "hitBulletColor",
    "hitBulletBig",
    "hitLaserBlast",
    "hitLancer",
    "hitEmpSpark",
    "explosion",
    "massiveExplosion",
    "blastExplosion",
    "flakExplosion",
    "smeltsmoke",
    "freezing",
    "casing1",
}


def main() -> int:
    issues: list[str] = []
    blocks = {p.stem for p in (CONTENT / "blocks").glob("*.hjson")}
    units = {p.stem for p in (CONTENT / "units").glob("*.hjson")}
    items = {p.stem for p in (CONTENT / "items").glob("*.hjson")}

    # meta BOM / name
    for meta in ("mod.hjson", "mod.json"):
        b = (MOD / meta).read_bytes()
        if b.startswith(b"\xef\xbb\xbf"):
            issues.append(f"{meta}: UTF-8 BOM")
        if meta == "mod.hjson" and not b.startswith(b"name:"):
            issues.append(f"{meta}: must start with name:")
        if meta == "mod.json" and b"\"name\"" not in b[:80]:
            issues.append(f"{meta}: missing name")

    for p in CONTENT.rglob("*.hjson"):
        t = p.read_text(encoding="utf-8-sig")
        rel = str(p.relative_to(MOD))

        for m in re.finditer(r"(?m)^\s*status:\s*([\w-]+)\s*$", t):
            s = m.group(1)
            if s not in VALID_STATUS:
                issues.append(f"{rel}: unknown status '{s}'")

        for m in re.finditer(r"(?m)^\s*hitEffect:\s*([\w-]+)\s*$", t):
            fx = m.group(1)
            if fx in INVALID_HIT:
                issues.append(f"{rel}: bad hitEffect '{fx}'")

        for m in re.finditer(r"parent:\s*aoen-([\w-]+)", t):
            pid = m.group(1)
            if pid not in blocks and pid not in units:
                issues.append(f"{rel}: missing research parent aoen-{pid}")

        for m in re.finditer(r"previous:\s*aoen-([\w-]+)", t):
            pid = m.group(1)
            if pid not in units:
                issues.append(f"{rel}: missing previous aoen-{pid}")

        for m in re.finditer(r"\baoen-([\w-]+)/", t):
            iid = m.group(1)
            # could be item or block in requirements
            if iid not in items and iid not in blocks and iid not in units:
                # status bleeding etc.
                if iid not in {s.removeprefix("aoen-") for s in VALID_STATUS if s.startswith("aoen-")}:
                    if not (CONTENT / "status" / f"{iid}.hjson").exists():
                        # allow fabricator plans referencing units in other files only via previous
                        pass

    # unit body + weapons
    for p in (CONTENT / "units").glob("*.hjson"):
        stem = p.stem
        t = p.read_text(encoding="utf-8-sig")
        if not (SPR_U / f"{stem}.png").exists():
            issues.append(f"unit {stem}: missing body sprite")
        if not (SPR_U / f"{stem}-preview.png").exists():
            issues.append(f"unit {stem}: missing preview")
        ut = re.search(r"^type:\s*(\w+)", t, re.M)
        kind = ut.group(1) if ut else ""
        if kind == "legs" and not (SPR_U / f"{stem}-leg.png").exists():
            issues.append(f"unit {stem}: missing leg sprite")
        if kind == "mech" and not (SPR_U / f"{stem}-leg.png").exists():
            issues.append(f"unit {stem}: missing leg sprite")
        if kind == "crawl":
            sm = re.search(r"segments:\s*(\d+)", t)
            n = int(sm.group(1)) if sm else 0
            for i in range(n):
                if not (SPR_U / f"{stem}-segment{i}.png").exists():
                    issues.append(f"unit {stem}: missing segment{i}")

        # unit-level parts
        body = re.search(r"(?ms)^parts:\s*\[(.*?)(?=^weapons:|\Z)", t)
        if body:
            for suf in re.findall(r"suffix:\s*(-\w[\w-]*)", body.group(1)):
                if not (SPR_U / f"{stem}{suf}.png").exists():
                    issues.append(f"unit {stem}: missing part {stem}{suf}.png")

        hits = list(re.finditer(r"(?m)^    name:\s*([\w-]+)\s*$", t))
        for i, wm in enumerate(hits):
            wstem = wm.group(1).removeprefix("aoen-")
            start, end = wm.end(), hits[i + 1].start() if i + 1 < len(hits) else len(t)
            block = t[start:end]
            if not re.search(r"\b(bullet|reload|shootY)\b", block):
                continue
            if not (SPR_U / f"{wstem}.png").exists():
                issues.append(f"unit {stem}: missing weapon {wstem}.png")
            for suf in re.findall(r"suffix:\s*(-\w[\w-]*)", block):
                if not (SPR_U / f"{wstem}{suf}.png").exists():
                    issues.append(f"unit {stem}: missing {wstem}{suf}.png")

    # blocks with sprites expected
    for stem in blocks:
        if stem.startswith("ore-"):
            for i in range(1, 4):
                if not (SPR_B / f"{stem}{i}.png").exists():
                    issues.append(f"ore {stem}: missing variant {i}")
            continue
        # skip if no sprite needed? all placeable need sprite
        if not (SPR_B / f"{stem}.png").exists():
            # factories may be generated by build_block_sprites
            issues.append(f"block {stem}: missing sprite")

    for stem in items:
        if not (SPR_I / f"{stem}.png").exists():
            issues.append(f"item {stem}: missing sprite")

    # double prefix
    for folder in (SPR_U, SPR_B, SPR_I):
        for p in folder.glob("aoen-*.png"):
            issues.append(f"DOUBLE-PREFIX {p.relative_to(MOD)}")

    uniq = sorted(set(issues))
    print(f"audit: {len(uniq)} issue(s)")
    for x in uniq[:100]:
        print(" ", x)
    if len(uniq) > 100:
        print(f"  ... +{len(uniq) - 100} more")
    return 1 if uniq else 0


if __name__ == "__main__":
    raise SystemExit(main())
