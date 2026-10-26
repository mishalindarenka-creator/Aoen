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

function enhanceSnakes() {
  // Calamity-style trail worms (NOT crawl)
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
}

function enhanceBahamut() {
  require("bahamut").apply();
}

function enhanceNaval() {
  // MH-flavoured water wake / bubble pressure
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
          // Fx.bubble is not guaranteed across builds — use smoke wake
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
  Log.info("[Aoen] naval MH wake abilities");
}

function enhanceCrabzilla() {
  const z = lib.unit("aoen-crabzilla");
  if (z == null) return;
  try {
    z.localizedName = "Crabzilla";
  } catch (e) {}
  lib.addAbility(z, extend(Ability, {
    update(unit) {
      // crushing aura
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
  Log.info("[Aoen] Crabzilla kaiju aura");
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

function run() {
  if (enhanced) return;
  try {
    enhanceSnakes();
    enhanceNaval();
    enhanceBahamut();
    enhanceCrabzilla();
    enhanceBossWeapons();
    enhanced = true;
    Log.info("[Aoen] JS enhance complete");
  } catch (e) {
    Log.err("[Aoen] enhance failed: " + e);
  }
}

function forceRun() {
  enhanced = false;
  run();
}

Events.on(ClientLoadEvent, e => {
  Timer.schedule(run, 0.1);
});

Events.on(ServerLoadEvent, e => {
  Timer.schedule(run, 0.1);
});

exports.run = forceRun;
