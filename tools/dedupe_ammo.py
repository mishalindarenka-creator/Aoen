"""Remove duplicate ammoTypes keys after vanilla→aoen remap (keep last = usually stronger)."""
from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path

BLOCKS = Path(__file__).resolve().parents[1] / "content" / "blocks"


def dedupe_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8-sig")
    m = re.search(r"(ammoTypes:\s*\{)(.*)(\n\})", text, re.S)
    if not m:
        return False
    body = m.group(2)
    entries: list[tuple[str, str]] = []
    for em in re.finditer(r"(?m)^  ([a-z0-9-]+):\s*\{", body):
        key = em.group(1)
        brace = body.find("{", em.start())
        depth = 0
        j = brace
        while j < len(body):
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        entries.append((key, body[em.start() : j].rstrip()))
    if not entries:
        return False
    seen: OrderedDict[str, str] = OrderedDict()
    for k, block in entries:
        seen[k] = block
    if len(seen) == len(entries):
        return False
    # Prefer stronger: for nocturne-bolt, plate pierce > plate missile — keep first pierce, rename last
    # Simple policy: keep last
    new_body = "\n" + "\n".join(seen.values()) + "\n"
    new_text = text[: m.start(2)] + new_body + text[m.end(2) :]
    path.write_text(new_text, encoding="utf-8")
    print("dedup", path.name, "→", list(seen))
    return True


def main() -> None:
    n = 0
    for p in sorted(BLOCKS.glob("*.hjson")):
        if dedupe_file(p):
            n += 1
    # special: nocturne-bolt — restore missile as aether ammo
    bolt = BLOCKS / "nocturne-bolt.hjson"
    t = bolt.read_text(encoding="utf-8-sig")
    if "aoen-aether-dust:" not in t and "MissileBulletType" not in t:
        # append aether missile ammo if missing after dedupe
        t = t.replace(
            "  aoen-ember-slag: {\n    type: BasicBulletType\n    damage: 30\n    speed: 4.4\n    lifetime: 52\n    width: 8\n    height: 10\n    pierce: true\n    pierceCap: 2\n  }\n}",
            """  aoen-ember-slag: {
    type: BasicBulletType
    damage: 30
    speed: 4.4
    lifetime: 52
    width: 8
    height: 10
    pierce: true
    pierceCap: 2
  }
  aoen-aether-dust: {
    type: MissileBulletType
    damage: 24
    splashDamage: 12
    splashDamageRadius: 12
    speed: 3.6
    lifetime: 60
    width: 7
    height: 9
    homingPower: 0.1
  }
}""",
        )
        bolt.write_text(t, encoding="utf-8")
        print("restored nocturne-bolt aether missile")
    # shard-turret: ensure lead-weak entry gone, keep strong void-shard; add nocturne-plate if only one void
    print("done", n)


if __name__ == "__main__":
    main()
