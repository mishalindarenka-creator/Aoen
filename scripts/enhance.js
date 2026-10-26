// Wire HJSON content into full JS behaviour after content loads
const lib = require("lib");
const bullets = require("bullets");
const abilities = require("abilities");

const SNAKES = [
  { id: "aoen-snake", dps: 2.8, r: 1.2 },
  { id: "aoen-snake-t2", dps: 4.0, r: 1.25 },
  { id: "aoen-cinder-millipede", dps: 5.2, r: 1.3 },
  { id: "aoen-payload-serpent", dps: 6.0, r: 1.3 },
  { id: "aoen-singularity-eel", dps: 7.5, r: 1.35 },
  { id: "aoen-ouroboros-prime", dps: 16, r: 1.4 }
];

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
  SNAKES.forEach(s => {
    const u = lib.unit(s.id);
    if (u == null) {
      Log.warn("[Aoen] snake missing: " + s.id);
      return;
    }
    u.canAttack = true;
    lib.addAbility(u, abilities.serpentCrush(s.dps, s.r));
    if (s.id === "aoen-snake" || s.id === "aoen-snake-t2") {
      replaceNamedBullet(
        u,
        "fang",
        bullets.venomFang(s.id === "aoen-snake" ? 28 : 42, s.id === "aoen-snake" ? 14 : 22)
      );
    }
    Log.info("[Aoen] enhanced snake " + s.id);
  });
}

function enhanceBahamut() {
  const u = lib.unit("aoen-bahamut");
  if (u == null) {
    Log.warn("[Aoen] bahamut missing");
    return;
  }
  lib.addAbility(u, abilities.bahamutShackles());
  replaceNamedBullet(u, "catastrophe", bullets.catastrophe);
  replaceNamedBullet(u, "breath", bullets.darkBreath);
  replaceNamedBullet(u, "wing-missile", bullets.wingMissile);

  const bleed = lib.status("aoen-bleeding");
  lib.eachWeapon(u, w => {
    const n = w.name != null ? ("" + w.name) : "";
    if (n.indexOf("claw") >= 0 && w.bullet != null) {
      w.bullet.damage = Math.max(w.bullet.damage, 140);
      if (bleed != null) {
        w.bullet.status = bleed;
        w.bullet.statusDuration = 160;
      }
    }
  });
  Log.info("[Aoen] enhanced bahamut (JS Catastrophe/Breath/Shackles)");
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
    enhanceBahamut();
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
