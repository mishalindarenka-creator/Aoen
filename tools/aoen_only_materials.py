"""Rewrite all content recipes/requirements to use ONLY Aoen items (no vanilla mats)."""
from __future__ import annotations

import re
from pathlib import Path

MOD = Path(__file__).resolve().parents[1]
CONTENT = MOD / "content"

# vanilla → aoen item id (with aoen- prefix as used in content)
MAP = {
    "copper": "aoen-nocturne-ore",
    "lead": "aoen-void-shard",
    "coal": "aoen-ember-slag",
    "graphite": "aoen-ember-slag",
    "silicon": "aoen-nocturne-plate",
    "titanium": "aoen-abyssal-quartz",
    "thorium": "aoen-pale-mythril",
    "metaglass": "aoen-tide-coral",
    "plastanium": "aoen-tide-composite",
    "phase-fabric": "aoen-aether-dust",
    "surge-alloy": "aoen-abyssal-alloy",
    "blast-compound": "aoen-ember-slag",
    "pyratite": "aoen-ember-slag",
    "sand": "aoen-void-shard",
    "scrap": "aoen-void-shard",
    "spore-pod": "aoen-tide-coral",
}

# research parents that point at vanilla tech trees
PARENT_MAP = {
    "ground-factory": "core-nucleus",
    "naval-factory": "core-nucleus",
    "graphite-press": "aoen-dark-conveyor",
    "duo": "aoen-dark-drill",
    "scatter": "aoen-shard-turret",
    "lancer": "aoen-nocturne-bolt",
    "ripple": "aoen-tide-pulse",
    "silicon-smelter": "aoen-void-smelter",
    "kiln": "aoen-nocturne-smelter",
    "plastanium-compressor": "aoen-tide-kiln",
    "phase-weaver": "aoen-aether-refinery",
    "surge-smelter": "aoen-abyssal-foundry",
    "combustion-generator": "aoen-dark-drill",
    "battery": "aoen-dark-generator",
    "mechanical-drill": "aoen-dark-conveyor",
    "pneumatic-drill": "aoen-dark-conveyor",
    "conveyor": "core-nucleus",
    "router": "aoen-dark-conveyor",
    "junction": "aoen-dark-conveyor",
    "copper-wall": "aoen-ceramite-forge",
    "titanium-wall": "aoen-ceramite-wall",
    "mend-projector": "aoen-tide-pulse",
    "core-shard": "core-nucleus",
}

ITEM_RE = re.compile(
    r"(?<![-\w])(" + "|".join(re.escape(k) for k in sorted(MAP, key=len, reverse=True)) + r")(?=/|\s*:)"
)


def merge_item_lines(block: str) -> str:
    """Inside a [...] list of item/amount lines, remap + merge duplicates."""
    lines = block.split("\n")
    out_lines = []
    bucket: dict[str, int] = {}
    order: list[str] = []
    indent = None
    collecting = False

    def flush():
        nonlocal collecting, bucket, order, indent
        if not collecting:
            return
        for k in order:
            out_lines.append(f"{indent}{k}/{bucket[k]}")
        bucket.clear()
        order.clear()
        collecting = False

    for line in lines:
        m = re.match(r"^(\s*)([a-z0-9-]+)/(\d+)\s*$", line)
        if m:
            ind, name, amt = m.group(1), m.group(2), int(m.group(3))
            if name in MAP:
                name = MAP[name]
            # bare aoen stems without prefix stay; vanilla already mapped
            if not collecting:
                collecting = True
                indent = ind
            if name not in bucket:
                order.append(name)
                bucket[name] = 0
            bucket[name] += amt
        else:
            flush()
            # remap ammoTypes keys like "copper:" or "silicon:"
            line2 = re.sub(
                r"(?m)^(\s*)(" + "|".join(map(re.escape, MAP)) + r")(\s*:)",
                lambda mm: f"{mm.group(1)}{MAP[mm.group(2)]}{mm.group(3)}",
                line,
            )
            # research parent: vanilla
            line2 = re.sub(
                r"(?m)^(\s*parent:\s*)([a-z0-9-]+)\s*$",
                lambda mm: f"{mm.group(1)}{PARENT_MAP.get(mm.group(2), mm.group(2))}",
                line2,
            )
            # outputItem: silicon/N
            line2 = re.sub(
                r"outputItem:\s*(" + "|".join(map(re.escape, MAP)) + r")/(\d+)",
                lambda mm: f"outputItem: {MAP[mm.group(1)]}/{mm.group(2)}",
                line2,
            )
            out_lines.append(line2)
    flush()
    return "\n".join(out_lines)


def process_text(text: str) -> str:
    # First pass: merge-aware rewrite of whole file via line scan
    text = merge_item_lines(text)
    # Safety: any leftover vanilla item/amount
    def repl_amt(m: re.Match) -> str:
        return f"{MAP[m.group(1)]}/{m.group(2)}"

    text = re.sub(
        r"(?<![-\w])(" + "|".join(map(re.escape, MAP)) + r")/(\d+)",
        repl_amt,
        text,
    )
    # leftover ammo keys
    text = re.sub(
        r"(?m)^(\s*)(" + "|".join(map(re.escape, MAP)) + r")(\s*:)",
        lambda mm: f"{mm.group(1)}{MAP[mm.group(2)]}{mm.group(3)}",
        text,
    )
    return text


def fix_bootstrap_crafters() -> None:
    """Ensure early smelters don't need items they produce circularly."""
    # void-smelter: refine ore into shards
    p = CONTENT / "blocks" / "void-smelter.hjson"
    p.write_text(
        """type: GenericCrafter
category: crafting
size: 2
consumes: {
  power: 1.8
  items: [
    aoen-nocturne-ore/2
    aoen-ember-slag/1
  ]
}
health: 320
craftTime: 50
hasItems: true
itemCapacity: 20
outputItem: aoen-void-shard/2
craftEffect: smeltsmoke
updateEffect: smeltsmoke
requirements: [
  aoen-nocturne-ore/60
  aoen-ember-slag/40
  aoen-void-shard/20
]
research: {
  parent: aoen-dark-conveyor
  requirements: [
    aoen-nocturne-ore/80
  ]
}
""",
        encoding="utf-8",
    )

    # nocturne-smelter: ore → plate (fuel = slag)
    p = CONTENT / "blocks" / "nocturne-smelter.hjson"
    p.write_text(
        """type: GenericCrafter
category: crafting
size: 2
consumes: {
  power: 2.4
  items: [
    aoen-nocturne-ore/2
    aoen-ember-slag/1
  ]
}
health: 380
craftTime: 55
hasItems: true
itemCapacity: 24
outputItem: aoen-nocturne-plate/1
craftEffect: smeltsmoke
updateEffect: smeltsmoke
requirements: [
  aoen-nocturne-ore/70
  aoen-void-shard/55
  aoen-ember-slag/45
]
research: {
  parent: aoen-void-smelter
  requirements: [
    aoen-nocturne-ore/80
    aoen-ember-slag/40
  ]
}
""",
        encoding="utf-8",
    )

    # ceramite-forge
    p = CONTENT / "blocks" / "ceramite-forge.hjson"
    p.write_text(
        """type: GenericCrafter
category: crafting
size: 3
consumes: {
  power: 4.2
  items: [
    aoen-void-shard/2
    aoen-abyssal-quartz/1
    aoen-ember-slag/1
  ]
}
health: 720
craftTime: 70
hasItems: true
itemCapacity: 30
outputItem: aoen-ceramite/1
craftEffect: smeltsmoke
requirements: [
  aoen-abyssal-quartz/120
  aoen-nocturne-plate/100
  aoen-void-shard/60
]
research: {
  parent: aoen-void-smelter
  requirements: [
    aoen-abyssal-quartz/80
    aoen-void-shard/40
  ]
}
""",
        encoding="utf-8",
    )

    # aether-refinery
    p = CONTENT / "blocks" / "aether-refinery.hjson"
    p.write_text(
        """type: GenericCrafter
category: crafting
size: 3
consumes: {
  power: 5.5
  items: [
    aoen-void-shard/1
    aoen-nocturne-plate/2
    aoen-ceramite/1
  ]
}
health: 800
craftTime: 90
hasItems: true
itemCapacity: 30
outputItem: aoen-aether-dust/2
craftEffect: formsmoke
requirements: [
  aoen-pale-mythril/140
  aoen-nocturne-plate/120
  aoen-ceramite/80
  aoen-tide-composite/60
]
research: {
  parent: aoen-ceramite-forge
  requirements: [
    aoen-pale-mythril/60
    aoen-ceramite/40
  ]
}
""",
        encoding="utf-8",
    )

    # void-compressor: plates from shards
    p = CONTENT / "blocks" / "void-compressor.hjson"
    if p.exists():
        t = p.read_text(encoding="utf-8-sig")
        t = re.sub(r"outputItem:\s*\S+", "outputItem: aoen-nocturne-plate/2", t)
        p.write_text(t, encoding="utf-8")


def main() -> int:
    fix_bootstrap_crafters()
    changed = 0
    for path in sorted(CONTENT.rglob("*.hjson")):
        raw = path.read_text(encoding="utf-8-sig")
        new = process_text(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed += 1
            print("fixed", path.relative_to(MOD))

    # verify no vanilla mats left
    leftovers = []
    van = set(MAP)
    for path in CONTENT.rglob("*.hjson"):
        t = path.read_text(encoding="utf-8-sig")
        for name in van:
            if re.search(rf"(?<![-\w]){re.escape(name)}(/|\s*:)", t):
                leftovers.append(f"{path.relative_to(MOD)}:{name}")
    print(f"rewrote {changed} files")
    if leftovers:
        print("LEFTOVER", len(leftovers))
        for x in leftovers[:40]:
            print(" ", x)
        return 1
    print("aoen_only_materials: OK — no vanilla mats")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
