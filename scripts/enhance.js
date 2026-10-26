// Wire HJSON content into full JS behaviour after content loads
const lib = require("lib");
const bullets = require("bullets");
const abilities = require("abilities");
const serpent = require("serpent");

var enhanced = false;

function replaceNamedBullet(unitType, weaponNameEnds, bullet) {
  if (unitType == null || bullet == null) return;
  lib.eachWeapon(unitType, w => {
    const n = w.name != null ? ("" + w.name) : "";
    if (n.indexOf(weaponNameEnds) >= 0) {
      w.bullet = bullet;
    }
  });
}

function wireAll(unitId, map) {
  const u = lib.unit(unitId);
  if (u == null) return;
  for (var key in map) {
    if (!map.hasOwnProperty(key)) continue;
    replaceNamedBullet(u, key, map[key]);
  }
}

function enhanceSnakes() {
  const specs = [
    {
      id: "aoen-snake",
      stem: "snake",
      segs: 8,
      spacing: 9,
      dps: 3.2,
      hitR: 10,
      status: StatusEffects.corroded,
      extras: [serpent.desertBurrow()],
      fang: true
    },
    {
      id: "aoen-snake-t2",
      stem: "snake-t2",
      segs: 10,
      spacing: 9.5,
      dps: 4.5,
      hitR: 11,
      status: StatusEffects.wet,
      extras: [serpent.aquaticMiasma(30)],
      fang: true
    },
    {
      id: "aoen-cinder-millipede",
      stem: "cinder-millipede",
      segs: 10,
      spacing: 10,
      dps: 5.8,
      hitR: 12,
      status: StatusEffects.burning,
      extras: [serpent.brimstoneTrail()]
    },
    {
      id: "aoen-payload-serpent",
      stem: "payload-serpent",
      segs: 11,
      spacing: 10.5,
      dps: 6.5,
      hitR: 13,
      status: StatusEffects.sapped,
      extras: []
    },
    {
      id: "aoen-singularity-eel",
      stem: "singularity-eel",
      segs: 12,
      spacing: 11,
      dps: 8,
      hitR: 14,
      status: StatusEffects.shocked,
      extras: [serpent.stormWeave()],
      tint: Color.valueOf("aaccff")
    },
    {
      id: "aoen-ouroboros-prime",
      stem: "ouroboros-prime",
      segs: 16,
      spacing: 13,
      dps: 18,
      hitR: 18,
      status: StatusEffects.sapped,
      extras: [serpent.voidDevour()],
      tint: Color.valueOf("cc88ff")
    }
  ];

  specs.forEach(s => {
    const u = lib.unit(s.id);
    if (u == null) {
      Log.warn("[Aoen] serpent missing: " + s.id);
      return;
    }
    u.canAttack = true;
    lib.addAbility(u, serpent.wormBody({
      stem: s.stem,
      segs: s.segs,
      spacing: s.spacing,
      dps: s.dps,
      hitR: s.hitR,
      status: s.status,
      statusDur: 50,
      tint: s.tint || null,
      name: "Worm Segments"
    }));
    (s.extras || []).forEach(ab => lib.addAbility(u, ab));
    if (s.fang) {
      replaceNamedBullet(
        u,
        "fang",
        bullets.venomFang(s.id === "aoen-snake" ? 30 : 44, s.id === "aoen-snake" ? 14 : 22)
      );
    }
    Log.info("[Aoen] Calamity worm: " + s.id + " (" + s.segs + " segs)");
  });

  wireAll("aoen-cinder-millipede", {
    slag: bullets.slagShell(55, 70),
    fang: bullets.venomFang(36, 18),
    spit: bullets.slagShell(28, 36)
  });
  wireAll("aoen-payload-serpent", {
    spit: bullets.aegisSlug(42),
    rear: bullets.slagShell(48, 55),
    sap: bullets.voidRift(38),
    hook: bullets.aegisSlug(50)
  });
  wireAll("aoen-singularity-eel", {
    rift: bullets.voidRift(70),
    bolt: bullets.voidRift(48),
    spores: bullets.venomFang(32, 16),
    missile: bullets.wingMissile
  });
  wireAll("aoen-ouroboros-prime", {
    maw: bullets.voidRift(110),
    bolt: bullets.voidRift(85),
    missile: bullets.wingMissile,
    emp: bullets.stormEmp(95)
  });
}

function enhanceBahamut() {
  require("bahamut").apply();
  const u = lib.unit("aoen-bahamut");
  if (u == null) return;
  replaceNamedBullet(u, "wing-missile", bullets.wingMissile);
  replaceNamedBullet(u, "orb", bullets.goldOrb(70));
  replaceNamedBullet(u, "emp", bullets.stormEmp(90));
  replaceNamedBullet(u, "claw", bullets.clawShred(155));
}

function enhanceNaval() {
  const wakeIds = [
    "aoen-naval",
    "aoen-naval-t2",
    "aoen-iron-reef",
    "aoen-needle-skiff",
    "aoen-leviathan-crown",
    "aoen-mare-imperator"
  ];
  wakeIds.forEach(id => {
    const u = lib.unit(id);
    if (u == null) return;
    lib.addAbility(u, extend(Ability, {
      update(unit) {
        if (unit.vel.len() > 0.6 && Mathf.chance(0.12 * Time.delta)) {
          Fx.smoke.at(unit.x + Mathf.range(8), unit.y + Mathf.range(8));
        }
        Units.nearbyEnemies(unit.team, unit.x, unit.y, unit.hitSize * 1.1, e => {
          if (Mathf.chance(0.03 * Time.delta)) {
            e.apply(StatusEffects.wet, 35);
          }
        });
      },
      localized() {
        return "Tide Wake";
      },
      copy() {
        return this;
      }
    }));
  });

  wireAll("aoen-naval", {
    torpedo: bullets.torpedo(38),
    cannon: bullets.tidePulse(32),
    flak: bullets.stormEmp(18)
  });
  wireAll("aoen-naval-t2", {
    cannon: bullets.tidePulse(48),
    shell: bullets.tidePulse(55),
    laser: bullets.tidePulse(40)
  });
  wireAll("aoen-iron-reef", {
    battery: bullets.tidePulse(62),
    flak: bullets.stormEmp(28),
    missile: bullets.torpedo(55)
  });
  wireAll("aoen-needle-skiff", {
    rack: bullets.torpedo(48),
    ciws: bullets.stormEmp(22),
    beam: bullets.tidePulse(50)
  });
  wireAll("aoen-leviathan-crown", {
    main: bullets.tidePulse(95),
    flak: bullets.stormEmp(36),
    beam: bullets.tidePulse(80),
    torpedo: bullets.torpedo(90),
    rail: bullets.tidePulse(110)
  });
  wireAll("aoen-mare-imperator", {
    main: bullets.tidePulse(160),
    ciws: bullets.stormEmp(55),
    beam: bullets.tidePulse(140),
    missile: bullets.torpedo(130),
    rail: bullets.tidePulse(180)
  });
  Log.info("[Aoen] naval MH wake + tide bullets");
}

function enhanceCrabLine() {
  wireAll("aoen-crab", {
    claw: bullets.clawShred(48),
    spit: bullets.venomFang(22, 12)
  });
  wireAll("aoen-crab-t2", {
    claw: bullets.clawShred(70),
    spit: bullets.venomFang(34, 16),
    flak: bullets.stormEmp(24)
  });
  wireAll("aoen-ceramtyr-daimyo", {
    claw: bullets.clawShred(95),
    gun: bullets.venomFang(48, 20),
    mortar: bullets.slagShell(70, 85),
    fang: bullets.venomFang(55, 22)
  });
  wireAll("aoen-quake-bulwark", {
    mortar: bullets.slagShell(90, 110),
    gun: bullets.clawShred(60),
    flak: bullets.stormEmp(36),
    missile: bullets.wingMissile,
    rail: bullets.voidRift(75)
  });
  wireAll("aoen-storm-sovereign", {
    beam: bullets.stormEmp(85),
    rail: bullets.stormEmp(100),
    emp: bullets.stormEmp(70),
    missile: bullets.wingMissile
  });
  wireAll("aoen-eclipse-tyrant", {
    claw: bullets.kaijuShred(180, 90),
    mortar: bullets.slagShell(140, 180),
    beam: bullets.voidRift(120),
    missile: bullets.wingMissile,
    rail: bullets.voidRift(150)
  });
}

function enhanceMechLine() {
  wireAll("aoen-boomeranger", {
    orb: bullets.goldOrb(28)
  });
  wireAll("aoen-boomeranger-t2", {
    orb: bullets.goldOrb(42)
  });
  wireAll("aoen-foundry-orbiter", {
    laser: bullets.slagShell(55, 40),
    shotgun: bullets.clawShred(48),
    missile: bullets.wingMissile,
    flak: bullets.stormEmp(30)
  });
  wireAll("aoen-aegis-walker", {
    gun: bullets.aegisSlug(55),
    shotgun: bullets.aegisSlug(48),
    missile: bullets.wingMissile,
    emp: bullets.stormEmp(45)
  });
  wireAll("aoen-nexus-prime", {
    core: bullets.goldOrb(80),
    laser: bullets.voidRift(70),
    point: bullets.goldOrb(55),
    missile: bullets.wingMissile,
    flak: bullets.stormEmp(40)
  });
  wireAll("aoen-apotheosis-core", {
    nova: bullets.kaijuNova(),
    batteries: bullets.goldOrb(95),
    rail: bullets.voidRift(140),
    missile: bullets.wingMissile,
    emp: bullets.stormEmp(90)
  });
}

function enhanceCrabzilla() {
  const z = lib.unit("aoen-crabzilla");
  if (z == null) return;
  try {
    z.localizedName = "Crabzilla";
  } catch (e) {}
  lib.addAbility(z, extend(Ability, {
    update(unit) {
      Units.nearbyEnemies(unit.team, unit.x, unit.y, unit.hitSize * 0.55, e => {
        e.damagePierce(0.35 * Time.delta);
        if (Mathf.chance(0.04 * Time.delta)) {
          e.apply(StatusEffects.unmoving, 20);
        }
      });
      if (unit.damaged() && Mathf.chance(0.05 * Time.delta)) {
        unit.heal(8 * Time.delta);
      }
    },
    draw(unit) {
      Draw.z(Layer.effect);
      Draw.color(Color.valueOf("ff6644"));
      Draw.alpha(0.08 + Mathf.absin(Time.time, 20, 0.06));
      Lines.stroke(3);
      Lines.circle(unit.x, unit.y, unit.hitSize * 0.5);
      Draw.reset();
    },
    localized() {
      return "Kaiju Presence";
    },
    copy() {
      return this;
    }
  }));
  wireAll("aoen-crabzilla", {
    claw: bullets.kaijuShred(260, 120),
    mortar: bullets.slagShell(220, 280),
    beam: bullets.voidRift(200),
    rail: bullets.voidRift(240),
    missile: bullets.wingMissile,
    flak: bullets.stormEmp(80),
    nova: bullets.kaijuNova()
  });
  Log.info("[Aoen] Crabzilla kaiju aura + bullets");
}

function enhanceBossWeapons() {
  const storm = lib.unit("aoen-storm-sovereign");
  if (storm != null) {
    lib.eachWeapon(storm, w => {
      if (w.bullet != null && w.bullet instanceof ContinuousLaserBulletType) {
        const src = w.bullet;
        w.bullet = extend(ContinuousLaserBulletType, {
          damage: src.damage,
          length: src.length,
          width: src.width,
          lifetime: src.lifetime,
          status: StatusEffects.shocked,
          statusDuration: 50,
          hit(b, x, y) {
            this.super$hit(b, x, y);
            Lightning.create(b.team, StatusEffects.shocked.color, 18, x, y, b.rotation() + Mathf.range(25), 8);
            Lightning.create(b.team, StatusEffects.shocked.color, 18, x, y, b.rotation() + Mathf.range(25), 8);
          }
        });
        if (src.colors != null) {
          w.bullet.colors = src.colors;
        }
      }
    });
  }

  const aegis = lib.unit("aoen-aegis-walker");
  if (aegis != null) {
    lib.addAbility(aegis, extend(Ability, {
      update(unit) {
        if (unit.damaged() && Mathf.chance(0.08 * Time.delta)) {
          unit.heal(2.5 * Time.delta);
        }
      },
      localized() {
        return "Aegis Regen";
      },
      copy() {
        return this;
      }
    }));
  }
}

function aoenEnhanceOnce() {
  if (enhanced) return;
  try {
    enhanceSnakes();
    enhanceNaval();
    enhanceBahamut();
    enhanceCrabLine();
    enhanceMechLine();
    enhanceCrabzilla();
    enhanceBossWeapons();
    enhanced = true;
    Log.info("[Aoen] JS enhance complete (all-line custom bullets)");
  } catch (e) {
    Log.err("[Aoen] enhance failed: " + e);
  }
}

function aoenEnhanceForce() {
  enhanced = false;
  aoenEnhanceOnce();
}

Events.on(ClientLoadEvent, e => {
  Timer.schedule(aoenEnhanceOnce, 0.1);
});

Events.on(ServerLoadEvent, e => {
  Timer.schedule(aoenEnhanceOnce, 0.1);
});

exports.run = aoenEnhanceForce;
