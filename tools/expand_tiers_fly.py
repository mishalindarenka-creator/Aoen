"""Tier x2 scaling, forked crab legs, T7 for all lines, flying T1–T7, recon sprites/upgrades."""
from __future__ import annotations

import math
import re
from pathlib import Path

from PIL import Image, ImageDraw

MOD = Path(__file__).resolve().parents[1]
UNITS = MOD / "content" / "units"
BLOCKS = MOD / "content" / "blocks"
SPR_U = MOD / "sprites" / "units"
SPR_B = MOD / "sprites" / "blocks"

# lines: list of stems T1..Tn (existing). Missing T7 will be created from T6 template.
LINES = {
    "crab": ["crab", "crab-t2", "ceramtyr-daimyo", "quake-bulwark", "storm-sovereign", "eclipse-tyrant", "crabzilla"],
    "mech": ["boomeranger", "boomeranger-t2", "foundry-orbiter", "aegis-walker", "nexus-prime", "apotheosis-core", "apotheosis-omega"],
    "naval": ["naval", "naval-t2", "iron-reef", "needle-skiff", "leviathan-crown", "mare-imperator", "mare-absolution"],
    "snake": ["snake", "snake-t2", "cinder-millipede", "payload-serpent", "singularity-eel", "ouroboros-prime", "ouroboros-apex"],
    "fly": ["aether-mote", "gale-wisp", "storm-kite", "void-raptor", "aether-wyvern", "sky-colossus", "firmament-throne"],
}

FLY_BASE = {
    "type": "flying",
    "outlines": "false",
    "flying": "true",
    "lowAltitude": "true",
}

# T1 baselines for fly line
FLY_STATS = [
    # hit, hp, armor, speed, range, weapons count, dmg
    (9, 520, 3, 2.4, 42, 1, 18),
    (14, 1100, 7, 2.1, 55, 2, 36),
    (22, 2400, 12, 1.85, 72, 4, 72),
    (36, 5200, 18, 1.55, 95, 8, 144),
    (56, 12000, 26, 1.25, 125, 10, 288),
    (90, 28000, 38, 0.95, 160, 12, 576),
    (140, 64000, 52, 0.75, 210, 16, 1150),
]


def draw_forked_leg(path: Path, dark, mid, hi, w: int = 28, h: int = 48) -> None:
    """Leg shaft that splits into two tips at penultimate segment."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w // 2
    # upper shaft
    d.rectangle([cx - 3, 2, cx + 3, h // 2], fill=mid + (255,), outline=hi + (255,))
    # joint bulb (fork point / penultimate)
    jy = h // 2
    d.ellipse([cx - 5, jy - 4, cx + 5, jy + 6], fill=dark + (255,), outline=hi + (255,))
    # two forked tips
    for sx in (-1, 1):
        tip_x = cx + sx * 8
        d.line([(cx, jy + 2), (tip_x, h - 4)], fill=mid + (255,), width=4)
        d.polygon(
            [(tip_x - 3, h - 10), (tip_x, h - 1), (tip_x + 3, h - 10)],
            fill=hi + (255,),
        )
    im.save(path)


def draw_forked_foot(path: Path, mid, hi, size: int = 20) -> None:
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # dual pad
    d.ellipse([1, size // 3, size // 2 - 1, size - 2], fill=mid + (255,), outline=hi + (255,))
    d.ellipse([size // 2 + 1, size // 3, size - 2, size - 2], fill=mid + (255,), outline=hi + (255,))
    im.save(path)


def forked_legs_for_crab_line() -> None:
    pals = {
        "crab": ((36, 34, 40), (90, 82, 70), (210, 195, 150)),
        "crab-t2": ((40, 36, 44), (110, 90, 70), (230, 200, 130)),
        "ceramtyr-daimyo": ((48, 12, 14), (130, 32, 36), (220, 80, 70)),
        "quake-bulwark": ((40, 46, 56), (90, 105, 120), (180, 200, 220)),
        "storm-sovereign": ((36, 32, 72), (90, 75, 150), (180, 170, 245)),
        "eclipse-tyrant": ((16, 14, 20), (80, 60, 40), (255, 200, 90)),
        "crabzilla": ((12, 8, 18), (100, 30, 40), (255, 95, 70)),
    }
    for stem, (dark, mid, hi) in pals.items():
        scale = 1.0 + LINES["crab"].index(stem) * 0.35
        w, h = int(28 * scale), int(48 * scale)
        draw_forked_leg(SPR_U / f"{stem}-leg.png", dark, mid, hi, w, h)
        draw_forked_foot(SPR_U / f"{stem}-foot.png", mid, hi, max(16, int(18 * scale)))
        # leg-base: wide fork mount
        base = Image.new("RGBA", (max(40, int(36 * scale)), max(16, int(14 * scale))), (0, 0, 0, 0))
        bd = ImageDraw.Draw(base)
        bd.rectangle([2, 2, base.width - 3, base.height - 3], fill=dark + (255,), outline=hi + (255,))
        bd.line([(base.width // 2, 2), (base.width // 4, base.height - 2)], fill=mid + (255,), width=3)
        bd.line([(base.width // 2, 2), (3 * base.width // 4, base.height - 2)], fill=mid + (255,), width=3)
        base.save(SPR_U / f"{stem}-leg-base.png")
        print("forked legs", stem)


def set_field(text: str, key: str, value) -> str:
    pat = rf"(?m)^({re.escape(key)}:\s*)([^\n#]+)"
    if re.search(pat, text):
        return re.sub(pat, rf"\g<1>{value}", text, count=1)
    # insert after type line
    return re.sub(r"(?m)^(type:\s*\w+\s*)$", rf"\1\n{key}: {value}", text, count=1)


def scale_damage_in_text(text: str, mult: float) -> str:
    def repl(m: re.Match) -> str:
        v = float(m.group(2))
        # skip tiny floats that look like multipliers already handled
        if v < 0.01:
            return m.group(0)
        nv = v * mult
        if nv == int(nv):
            return f"{m.group(1)}{int(nv)}"
        return f"{m.group(1)}{nv:.2f}"

    # only bullet damage / splashDamage fields
    text = re.sub(r"(?m)^(\s*damage:\s*)([0-9.]+)", repl, text)
    text = re.sub(r"(?m)^(\s*splashDamage:\s*)([0-9.]+)", repl, text)
    return text


def duplicate_weapons(text: str, copies: int) -> str:
    """Duplicate weapons block entries to approach 2x per tier (clamped)."""
    if copies <= 1:
        return text
    m = re.search(r"weapons:\s*\[", text)
    if not m:
        return text
    # find matching closing of weapons array at indent 0-ish — crude parse
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth:
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        i += 1
    body = text[start : i - 1]
    # split top-level weapon objects
    weapons = []
    depth = 0
    buf = []
    for ch in body:
        if ch == "{":
            if depth == 0:
                buf = ["{"]
            else:
                buf.append(ch)
            depth += 1
        elif ch == "}":
            depth -= 1
            buf.append(ch)
            if depth == 0:
                weapons.append("".join(buf))
        elif depth > 0:
            buf.append(ch)
    if not weapons:
        return text
    out = list(weapons)
    # add clones with shifted x
    need = min(len(weapons) * copies, 16) - len(weapons)
    idx = 0
    while need > 0:
        src = weapons[idx % len(weapons)]
        clone = src
        # keep same weapon name so sprites resolve; only shift mount x
        # shift x
        def shift_x(mm: re.Match) -> str:
            try:
                xv = float(mm.group(2))
            except ValueError:
                return mm.group(0)
            return f"{mm.group(1)}{xv + 3 + (len(out) % 5)}"

        clone = re.sub(r"(?m)^(\s*x:\s*)(-?[0-9.]+)", shift_x, clone, count=1)
        out.append(clone)
        need -= 1
        idx += 1
    new_body = "\n".join("  " + w.replace("\n", "\n  ") if not w.startswith("\n") else w for w in out)
    # simpler join
    joined = "\n".join(out)
    return text[:start] + "\n" + joined + "\n" + text[i - 1 :]


def scale_unit_file(stem: str, tier: int, base_hit: float, base_hp: float) -> None:
    path = UNITS / f"{stem}.hjson"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    # size ~1.55^tier (readable), power/weapons true 2^(tier-1)
    size_m = 1.55 ** (tier - 1)
    pow_m = 2 ** (tier - 1)
    hit = max(8, round(base_hit * size_m, 1))
    hp = int(base_hp * pow_m)
    armor = max(1, int(3 * pow_m * 0.7))
    text = set_field(text, "hitSize", hit)
    text = set_field(text, "health", hp)
    # scale existing armor upward if present
    am = re.search(r"(?m)^armor:\s*([0-9.]+)", text)
    if am:
        text = set_field(text, "armor", max(float(am.group(1)), armor))
    # leg length for legs units
    if "type: legs" in text:
        text = set_field(text, "legLength", max(10, round(12 * size_m)))
        text = set_field(text, "legBaseOffset", max(2, round(3 * size_m * 0.5)))
    # damage x pow_m / current relative — apply once from T1 baseline by rewriting damage fields with pow_m/current
    # Safer: multiply all damage by (pow_m / estimated_current). We multiply by 2 relative to previous once.
    # Here apply absolute: multiply damages so average scales — use pow_m as target multiplier from raw file once.
    text = scale_damage_in_text(text, pow_m / max(1, 2 ** (tier - 2)) if tier > 1 else 1)
    # Actually that double-applies on re-run. Better absolute: set from reading first damage * ratio.
    # For idempotency: store comment marker
    if f"# aoen-tier: {tier}" not in text:
        # first pass: multiply damages by 2^(tier-1) / 1 relative to file's current — use soft approach
        # Reset: multiply damages only if marker missing, using pow_m against "assumed already buffed mid values"
        pass
    # weapon copies
    copies = min(2 ** (tier - 1), 8)
    if copies > 1 and f"# aoen-wep-x{copies}" not in text:
        text = duplicate_weapons(text, copies)
        text = f"# aoen-tier: {tier}\n# aoen-wep-x{copies}\n" + text
    else:
        if f"# aoen-tier:" not in text:
            text = f"# aoen-tier: {tier}\n" + text
    path.write_text(text, encoding="utf-8")
    print("scaled", stem, "T" + str(tier), "hit", hit, "hp", hp, "wepx", copies)


def clone_unit(src_stem: str, dst_stem: str, replacements: dict[str, str]) -> str:
    src = (UNITS / f"{src_stem}.hjson").read_text(encoding="utf-8")
    for a, b in replacements.items():
        src = src.replace(a, b)
    return src


def write_t7_from_t6(line: str, t6: str, t7: str, recon: str) -> None:
    path = UNITS / f"{t7}.hjson"
    if path.exists():
        print("exists", t7)
        return
    text = (UNITS / f"{t6}.hjson").read_text(encoding="utf-8")
    text = text.replace(t6, t7)
    text = re.sub(r"(?m)^health:\s*[0-9.]+", lambda m: f"health: {int(float(m.group(0).split(':')[1]) * 2)}", text, count=1)
    text = re.sub(r"(?m)^hitSize:\s*[0-9.]+", lambda m: f"hitSize: {float(m.group(0).split(':')[1]) * 1.55:.1f}", text, count=1)
    text = scale_damage_in_text(text, 2.0)
    text = duplicate_weapons(text, 2)
    # research / requirements block
    text = re.sub(
        r"block:\s*aoen-[\w-]+",
        f"block: {recon}",
        text,
    )
    text = re.sub(
        r"parent:\s*aoen-[\w-]+",
        f"parent: {recon}",
        text,
        count=1,
    )
    # bump item costs in requirements
    def bump_cost(m: re.Match) -> str:
        return f"{m.group(1)}{m.group(2)}/{int(m.group(3)) * 2}"

    text = re.sub(r"(aoen-[\w-]+)/(\d+)", lambda m: f"{m.group(1)}/{int(m.group(2)) * 2}", text)
    text = f"# aoen-tier: 7\n# aoen-wep-x2\n" + text
    path.write_text(text, encoding="utf-8")
    # copy sprites
    for p in SPR_U.glob(f"{t6}*.png"):
        dest = SPR_U / p.name.replace(t6, t7, 1)
        if not dest.exists():
            # scale up image ~1.55
            im = Image.open(p).convert("RGBA")
            nw = max(8, int(im.width * 1.55))
            nh = max(8, int(im.height * 1.55))
            im.resize((nw, nh), Image.Resampling.NEAREST).save(dest)
    print("created T7", t7)


def write_fly_units() -> None:
    names = LINES["fly"]
    for i, stem in enumerate(names):
        tier = i + 1
        hit, hp, armor, speed, rng, nweap, dmg = FLY_STATS[i]
        weapons = []
        for w in range(nweap):
            ang = (360 / max(nweap, 1)) * w
            rad = 2 + (w % 4)
            wx = round(math.cos(math.radians(ang)) * rad, 1)
            wy = round(math.sin(math.radians(ang)) * rad, 1)
            weapons.append(
                f"""  {{
    name: {stem}-gun-{w}
    x: {wx}
    y: {wy}
    reload: {max(8, 28 - tier * 2)}
    rotate: true
    mirror: false
    shootSound: {'missile' if tier >= 4 else 'shoot'}
    bullet: {{
      type: {'MissileBulletType' if tier >= 3 else 'BasicBulletType'}
      damage: {dmg}
      splashDamage: {int(dmg * 0.35)}
      splashDamageRadius: {10 + tier * 2}
      speed: {2.8 + tier * 0.15}
      lifetime: {40 + tier * 4}
      width: {6 + tier}
      height: {8 + tier}
      {'status: shocked' + chr(10) + '      statusDuration: 60' if tier >= 4 else 'statusDuration: 1'}
      frontColor: aaccff
      backColor: 334466
      trailChance: 0.3
    }}
  }}"""
            )
        recon = "aoen-air-fabricator" if tier == 1 else (
            "aoen-air-reconstructor" if tier == 2 else f"aoen-air-reconstructor-t{tier}"
        )
        parent = "aoen-air-fabricator" if tier == 1 else (
            "aoen-air-reconstructor" if tier == 2 else f"aoen-air-reconstructor-t{max(3, tier)}"
        )
        # fix parent chain
        if tier == 1:
            req_block = "aoen-air-fabricator"
            research_parent = "aoen-air-fabricator"
        elif tier == 2:
            req_block = "aoen-air-reconstructor"
            research_parent = "aoen-air-reconstructor"
        else:
            req_block = f"aoen-air-reconstructor-t{tier}"
            research_parent = f"aoen-air-reconstructor-t{tier}"

        cost = 20 * (2 ** (tier - 1))
        text = f"""# aoen-tier: {tier}
type: flying
outlines: false
flying: true
lowAltitude: true
health: {hp}
armor: {armor}
speed: {speed}
accel: 0.08
drag: 0.03
hitSize: {hit}
rotateSpeed: {3.5 - tier * 0.2:.1f}
range: {rng}
faceTarget: true
engineOffset: {hit * 0.35:.1f}
engineSize: {2 + tier * 0.6:.1f}
researchCostMultiplier: {0.45 + tier * 0.08:.2f}

weapons: [
{chr(10).join(weapons)}
]

requirements: {{
  block: {req_block}
  time: {600 * (2 ** (tier - 1))}
  requirements: [
    aoen-nocturne-plate/{cost}
    aoen-aether-dust/{max(5, cost // 3)}
    aoen-void-shard/{cost // 2}
  ]
}}

research: {{
  parent: {research_parent}
  requirements: [
    aoen-aether-dust/{max(10, cost // 4)}
  ]
}}
"""
        (UNITS / f"{stem}.hjson").write_text(text, encoding="utf-8")
        # sprite: simple flying disc + engines
        size = max(32, int(hit * 3))
        im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = size // 2
        r = size // 3
        pal = [
            ((40, 60, 90), (80, 140, 200), (180, 230, 255)),
            ((30, 50, 80), (70, 120, 190), (160, 210, 255)),
            ((50, 40, 90), (100, 80, 180), (200, 180, 255)),
            ((40, 20, 60), (110, 50, 140), (220, 140, 255)),
            ((20, 40, 70), (60, 120, 180), (140, 220, 255)),
            ((15, 20, 40), (70, 90, 140), (200, 210, 255)),
            ((10, 10, 30), (90, 70, 160), (255, 220, 140)),
        ][i]
        dark, mid, hi = pal
        d.ellipse([c - r, c - r, c + r, c + r], fill=mid + (255,), outline=hi + (255,))
        d.ellipse([c - r // 2, c - r // 2, c + r // 2, c + r // 2], fill=dark + (255,), outline=hi + (255,))
        d.polygon([(c - 4, c + r - 2), (c, c + r + 8), (c + 4, c + r - 2)], fill=hi + (255,))
        im.save(SPR_U / f"{stem}.png")
        prev = im.copy()
        prev.thumbnail((64, 64), Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        canvas.paste(prev, ((64 - prev.width) // 2, (64 - prev.height) // 2), prev)
        canvas.save(SPR_U / f"{stem}-preview.png")
        cell = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
        ImageDraw.Draw(cell).ellipse([4, 4, 19, 19], fill=(180, 220, 255, 255))
        cell.save(SPR_U / f"{stem}-cell.png")
        # gun sprites
        for w in range(nweap):
            g = Image.new("RGBA", (16, 22), (0, 0, 0, 0))
            gd = ImageDraw.Draw(g)
            gd.rectangle([4, 8, 11, 20], fill=dark + (255,), outline=hi + (255,))
            gd.rectangle([6, 1, 9, 12], fill=mid + (255,), outline=hi + (255,))
            g.save(SPR_U / f"{stem}-gun-{w}.png")
        print("fly", stem, "T" + str(tier))


def recon_hjson(stem: str, size: int, power: float, items: list[str], parent: str, floating: bool = False) -> str:
    fl = "\nfloating: true" if floating else ""
    reqs = "\n".join(f"  {it}" for it in items)
    cons = "\n".join(f"    {it}" for it in items[:4])
    return f"""type: Reconstructor
outlineIcon: false
category: units
size: {size}
consumes: {{
  power: {power}
  items: [
{cons}
  ]
}}{fl}
researchCostMultiplier: {0.5 + size * 0.05:.2f}
constructTime: {60 * size * size}
requirements: [
{reqs}
]
research: {{
  parent: {parent}
  requirements: [
    {items[0]}
  ]
}}
"""


def write_blocks_and_upgrades() -> None:
    # air fabricator
    (BLOCKS / "air-fabricator.hjson").write_text(
        """type: UnitFactory
outlineIcon: false
category: units
size: 3
consumes: {
  power: 1.4
}
itemCapacity: 12
researchCostMultiplier: 0.55
requirements: [
  aoen-nocturne-ore/90
  aoen-void-shard/100
  aoen-aether-dust/40
  aoen-nocturne-plate/70
]
research: {
  parent: core-nucleus
  requirements: [
    aoen-aether-dust/30
  ]
}
""",
        encoding="utf-8",
    )

    # reconstructors sizes: t2=3, t3=3, t4=5, t5=7, t6=9, t7=11
    sizes = {2: 3, 3: 3, 4: 5, 5: 7, 6: 9, 7: 11}
    for tier in range(2, 8):
        sz = sizes[tier]
        # costs double each tier
        base = 40 * (2 ** (tier - 2))
        items = [
            f"aoen-nocturne-plate/{base}",
            f"aoen-aether-dust/{base // 2}",
            f"aoen-void-shard/{base}",
            f"aoen-pale-mythril/{max(10, base // 3)}",
        ]
        if tier >= 5:
            items.append(f"aoen-abyssal-alloy/{base // 2}")
        name = "air-reconstructor" if tier == 2 else f"air-reconstructor-t{tier}"
        parent = "aoen-air-fabricator" if tier == 2 else (
            "aoen-air-reconstructor" if tier == 3 else f"aoen-air-reconstructor-t{tier - 1}"
        )
        # t3 parent is air-reconstructor (t2)
        if tier == 3:
            parent = "aoen-air-reconstructor"
        power = 2.5 * (2 ** (tier - 2))
        text = recon_hjson(name, sz, power, items, parent)
        # constructTime already in template; bump *2 per tier via size^2 — also set explicit longer
        text = text.replace(
            f"constructTime: {60 * sz * sz}",
            f"constructTime: {90 * (2 ** (tier - 1)) * sz}",
        )
        (BLOCKS / f"{name}.hjson").write_text(text, encoding="utf-8")

    # naval T7 reconstructor
    (BLOCKS / "naval-reconstructor-t7.hjson").write_text(
        recon_hjson(
            "naval-reconstructor-t7",
            11,
            40,
            [
                "aoen-nocturne-plate/420",
                "aoen-tide-coral/300",
                "aoen-pale-mythril/220",
                "aoen-abyssal-alloy/240",
                "aoen-aether-dust/180",
            ],
            "aoen-naval-reconstructor-t6",
            floating=True,
        ).replace("constructTime: 7260", "constructTime: 14000"),
        encoding="utf-8",
    )

    # ground reconstructor costs/time *2 progression bump
    for p in BLOCKS.glob("*reconstructor*.hjson"):
        text = p.read_text(encoding="utf-8")
        # ensure constructTime exists and is long
        if "constructTime:" not in text:
            # derive from size
            sm = re.search(r"size:\s*(\d+)", text)
            sz = int(sm.group(1)) if sm else 3
            tier_guess = 2
            if "-t3" in p.name:
                tier_guess = 3
            elif "-t4" in p.name:
                tier_guess = 4
            elif "-t5" in p.name:
                tier_guess = 5
            elif "-t6" in p.name:
                tier_guess = 6
            elif "-t7" in p.name:
                tier_guess = 7
            ct = 100 * (2 ** (tier_guess - 1)) * sz
            text = text.replace("category: units", f"category: units\nconstructTime: {ct}", 1)
        else:
            def bump_ct(m: re.Match) -> str:
                return f"constructTime: {int(float(m.group(1)) * 1.5)}"

            text = re.sub(r"constructTime:\s*([0-9.]+)", bump_ct, text, count=1)
        # bump consume item amounts ~1.5x once if no marker
        if "# aoen-cost-x2" not in text:
            text = re.sub(
                r"(aoen-[\w-]+)/(\d+)",
                lambda m: f"{m.group(1)}/{int(int(m.group(2)) * 2)}",
                text,
            )
            text = "# aoen-cost-x2\n" + text
        p.write_text(text, encoding="utf-8")

    # Write upgrades via JS helper file content for enhance - also embed in blocks if supported
    # Mindustry HJSON upgrades on Reconstructor:
    upgrades = {
        "ground-reconstructor": [("crab", "crab-t2"), ("snake", "snake-t2"), ("boomeranger", "boomeranger-t2")],
        "ground-reconstructor-t3": [
            ("crab-t2", "ceramtyr-daimyo"),
            ("snake-t2", "cinder-millipede"),
            ("boomeranger-t2", "foundry-orbiter"),
        ],
        "ground-reconstructor-t4": [
            ("ceramtyr-daimyo", "quake-bulwark"),
            ("cinder-millipede", "payload-serpent"),
            ("foundry-orbiter", "aegis-walker"),
        ],
        "ground-reconstructor-t5": [
            ("quake-bulwark", "storm-sovereign"),
            ("payload-serpent", "singularity-eel"),
            ("aegis-walker", "nexus-prime"),
        ],
        "ground-reconstructor-t6": [
            ("storm-sovereign", "eclipse-tyrant"),
            ("singularity-eel", "ouroboros-prime"),
            ("nexus-prime", "apotheosis-core"),
        ],
        "ground-reconstructor-t7": [
            ("eclipse-tyrant", "crabzilla"),
            ("ouroboros-prime", "ouroboros-apex"),
            ("apotheosis-core", "apotheosis-omega"),
        ],
        "naval-reconstructor": [("naval", "naval-t2")],
        "naval-reconstructor-t3": [("naval-t2", "iron-reef")],
        "naval-reconstructor-t4": [("iron-reef", "needle-skiff")],
        "naval-reconstructor-t5": [("needle-skiff", "leviathan-crown")],
        "naval-reconstructor-t6": [("leviathan-crown", "mare-imperator")],
        "naval-reconstructor-t7": [("mare-imperator", "mare-absolution")],
        "air-reconstructor": [("aether-mote", "gale-wisp")],
        "air-reconstructor-t3": [("gale-wisp", "storm-kite")],
        "air-reconstructor-t4": [("storm-kite", "void-raptor")],
        "air-reconstructor-t5": [("void-raptor", "aether-wyvern")],
        "air-reconstructor-t6": [("aether-wyvern", "sky-colossus")],
        "air-reconstructor-t7": [("sky-colossus", "firmament-throne")],
    }
    for block, pairs in upgrades.items():
        bp = BLOCKS / f"{block}.hjson"
        if not bp.exists():
            continue
        text = bp.read_text(encoding="utf-8")
        if "upgrades:" in text:
            continue
        lines = ["upgrades: ["]
        for a, b in pairs:
            lines.append(f"  [aoen-{a}, aoen-{b}]")
        lines.append("]")
        text = text.rstrip() + "\n\n" + "\n".join(lines) + "\n"
        bp.write_text(text, encoding="utf-8")
        print("upgrades", block)

    # fabricator plans for T1 units
    for fab, plans in [
        ("ground-fabricator", [("crab", 1200), ("snake", 1100), ("boomeranger", 1000)]),
        ("naval-fabricator", [("naval", 1300)]),
        ("air-fabricator", [("aether-mote", 1000)]),
    ]:
        bp = BLOCKS / f"{fab}.hjson"
        text = bp.read_text(encoding="utf-8")
        if "plans:" in text:
            continue
        pl = ["plans: ["]
        for unit, time in plans:
            pl.append("  {")
            pl.append(f"    unit: aoen-{unit}")
            pl.append(f"    time: {time}")
            pl.append("    requirements: [")
            pl.append("      aoen-nocturne-plate/20")
            pl.append("      aoen-void-shard/15")
            pl.append("    ]")
            pl.append("  }")
        pl.append("]")
        text = text.rstrip() + "\n\n" + "\n".join(pl) + "\n"
        bp.write_text(text, encoding="utf-8")
        print("plans", fab)


def rebuild_recon_sprites() -> None:
    """Distinct jababa-like reconstructor shells per size."""
    for p in list(BLOCKS.glob("*reconstructor*.hjson")) + [BLOCKS / "air-fabricator.hjson"]:
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        sm = re.search(r"size:\s*(\d+)", text)
        sz = int(sm.group(1)) if sm else 3
        px = 32 * sz
        stem = p.stem
        is_naval = "naval" in stem
        is_air = "air" in stem
        if is_air:
            dark, mid, hi = (30, 50, 80), (70, 130, 190), (180, 230, 255)
        elif is_naval:
            dark, mid, hi = (20, 40, 55), (50, 100, 120), (140, 210, 230)
        else:
            dark, mid, hi = (40, 44, 52), (90, 100, 110), (200, 210, 220)
        im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        m = 3
        d.rectangle([m, m, px - m - 1, px - m - 1], fill=dark + (255,), outline=hi + (255,))
        d.rectangle([m + 4, m + 4, px - m - 5, px - m - 5], outline=mid + (255,))
        # inner bay
        bay = px // 4
        d.rectangle([bay, bay, px - bay, px - bay], fill=mid + (255,), outline=hi + (255,))
        # rails
        d.rectangle([bay, px // 2 - 2, px - bay, px // 2 + 2], fill=hi + (255,))
        d.rectangle([px // 2 - 2, bay, px // 2 + 2, px - bay], fill=hi + (255,))
        # tier pips
        for i in range(min(sz, 8)):
            d.rectangle([6 + i * 6, 6, 10 + i * 6, 10], fill=hi + (255,))
        im.save(SPR_B / f"{stem}.png")
        im.save(SPR_B / f"{stem}-top.png")
        # in / out halves
        left = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        right = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        left.paste(im.crop((0, 0, px // 2, px)), (0, 0))
        right.paste(im.crop((px // 2, 0, px, px)), (px // 2, 0))
        left.save(SPR_B / f"{stem}-in.png")
        right.save(SPR_B / f"{stem}-out.png")
        print("recon sprite", stem, px)


def scale_existing_lines() -> None:
    bases = {
        "crab": (10, 700),
        "mech": (10, 680),
        "naval": (11, 1000),
        "snake": (9, 620),
    }
    for line, stems in LINES.items():
        if line == "fly":
            continue
        bh, bhp = bases.get(line, (10, 800))
        for i, stem in enumerate(stems):
            tier = i + 1
            if stem in ("apotheosis-omega", "mare-absolution", "ouroboros-apex"):
                continue  # created separately
            if (UNITS / f"{stem}.hjson").exists():
                # milder idempotent scale: set hitSize/health absolutely
                path = UNITS / f"{stem}.hjson"
                text = path.read_text(encoding="utf-8")
                size_m = 1.55 ** (tier - 1)
                pow_m = 2 ** (tier - 1)
                hit = max(8, round(bh * size_m, 1))
                hp = int(bhp * pow_m)
                text = set_field(text, "hitSize", hit)
                text = set_field(text, "health", hp)
                if "type: legs" in text:
                    text = set_field(text, "legLength", max(10, round(11 * size_m)))
                # damage: set via multiplying once — marker
                if f"# aoen-dmg-t{tier}" not in text:
                    # normalize: take damages and set to base_dmg * pow_m roughly by multiplying current to target
                    # Use replace of damage values with progressive: read first damage as seed
                    dm = re.search(r"(?m)^\s*damage:\s*([0-9.]+)", text)
                    if dm:
                        # replace each damage with escalating — simpler multiply all by 1.0 if already scaled
                        # Force: damage fields become max(current, template)
                        target_base = 24 if line != "naval" else 28
                        # sequential replace
                        count = [0]

                        def dmg_repl(m: re.Match) -> str:
                            count[0] += 1
                            return f"{m.group(1)}{int(target_base * pow_m)}"

                        text = re.sub(r"(?m)^(\s*damage:\s*)([0-9.]+)", dmg_repl, text)
                    text = f"# aoen-dmg-t{tier}\n" + text
                copies = min(2 ** (tier - 1), 8)
                if f"# aoen-wep-x{copies}" not in text and copies > 1:
                    text = duplicate_weapons(text, copies)
                    text = f"# aoen-wep-x{copies}\n" + text
                if f"# aoen-tier:" not in text:
                    text = f"# aoen-tier: {tier}\n" + text
                path.write_text(text, encoding="utf-8")
                print("retier", stem, "T" + str(tier), hit, hp)


def main() -> None:
    SPR_U.mkdir(parents=True, exist_ok=True)
    SPR_B.mkdir(parents=True, exist_ok=True)
    forked_legs_for_crab_line()
    write_t7_from_t6("mech", "apotheosis-core", "apotheosis-omega", "aoen-ground-reconstructor-t7")
    write_t7_from_t6("naval", "mare-imperator", "mare-absolution", "aoen-naval-reconstructor-t7")
    write_t7_from_t6("snake", "ouroboros-prime", "ouroboros-apex", "aoen-ground-reconstructor-t7")
    write_fly_units()
    write_blocks_and_upgrades()
    rebuild_recon_sprites()
    scale_existing_lines()
    print("expand done")


if __name__ == "__main__":
    main()
