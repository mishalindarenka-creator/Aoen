/**
 * Aoen custom bullets — NO hit()/super$hit overrides (Rhino StackOverflow).
 * Status/splash/lightning via fields only; always sprite + load().
 */
const lib = require("lib");

function fxRing(life, c1, c2, grow) {
  return lib.fx(life, e => {
    Draw.color(lib.c(c1), lib.c(c2), e.fin());
    Lines.stroke(Math.max(0.5, 3 - e.fin() * 2.5));
    Lines.circle(e.x, e.y, 4 + e.fin() * grow);
  });
}

const fxBleed = fxRing(20, "ff6688", "440011", 22);
const fxVenom = fxRing(18, "aa88ff", "331155", 16);
const fxEmber = fxRing(22, "ff8844", "661100", 20);
const fxTide = fxRing(18, "66e0c8", "104040", 18);
const fxVoid = fxRing(24, "cc88ff", "220044", 28);
const fxStorm = fxRing(16, "aaccff", "223366", 14);
const fxGold = fxRing(18, "ffe080", "664400", 16);

function bleedStatus() {
  try {
    const s = lib.status("aoen-bleeding");
    if (s != null) return s;
  } catch (e) {}
  return StatusEffects.sapped;
}

function ready(b, sprite) {
  try {
    b.sprite = sprite || "bullet";
    b.load();
  } catch (e) {
    Log.warn("[Aoen] bullet load: " + e);
  }
  return b;
}

const fragCatastrophe = ready(extend(BasicBulletType, {
  damage: 45,
  splashDamage: 30,
  splashDamageRadius: 18,
  speed: 3.2,
  lifetime: 35,
  width: 10,
  height: 10,
  frontColor: lib.c("ff6688"),
  backColor: lib.c("440022"),
  status: StatusEffects.sapped,
  statusDuration: 80,
  hitEffect: fxBleed,
  despawnEffect: fxBleed
}), "bullet");

exports.catastrophe = ready(extend(BasicBulletType, {
  damage: 280,
  splashDamage: 420,
  splashDamageRadius: 72,
  speed: 2.2,
  lifetime: 90,
  width: 28,
  height: 28,
  pierce: true,
  pierceCap: 8,
  buildingDamageMultiplier: 1.35,
  trailLength: 14,
  trailWidth: 4.5,
  trailColor: lib.c("aa2244"),
  frontColor: lib.c("ee4488"),
  backColor: lib.c("220011"),
  hitEffect: fxBleed,
  despawnEffect: fxBleed,
  status: StatusEffects.sapped,
  statusDuration: 180,
  fragBullets: 12,
  fragBullet: fragCatastrophe
}), "shell");

exports.darkBreath = ready(extend(ContinuousLaserBulletType, {
  damage: 95,
  length: 180,
  width: 16,
  lifetime: 55,
  shake: 1.5,
  buildingDamageMultiplier: 1.2,
  status: StatusEffects.melting,
  statusDuration: 100
}), "laser");
exports.darkBreath.colors = [lib.c("ff4466"), lib.c("aa1122"), lib.c("1a0810")];

exports.wingMissile = ready(extend(MissileBulletType, {
  damage: 85,
  splashDamage: 55,
  splashDamageRadius: 22,
  speed: 3.8,
  lifetime: 70,
  width: 10,
  height: 14,
  homingPower: 0.14,
  homingRange: 96,
  trailChance: 0.45,
  status: StatusEffects.sapped,
  statusDuration: 70,
  frontColor: lib.c("cc4488"),
  backColor: lib.c("330022"),
  hitEffect: Fx.blastExplosion
}), "missile");

exports.venomFang = function (damage, splash) {
  return ready(extend(BasicBulletType, {
    damage: damage,
    splashDamage: splash,
    splashDamageRadius: 14,
    speed: 3.5,
    lifetime: 24,
    width: 8,
    height: 10,
    collidesAir: false,
    frontColor: lib.c("d0c0ff"),
    backColor: lib.c("554488"),
    status: StatusEffects.corroded,
    statusDuration: 100,
    hitEffect: fxVenom,
    despawnEffect: fxVenom
  }), "bullet");
};

exports.clawShred = function (dmg) {
  return ready(extend(ShrapnelBulletType, {
    damage: dmg,
    length: 42,
    width: 16,
    lifetime: 14,
    fromColor: lib.c("e8d8b0"),
    toColor: lib.c("665544"),
    status: bleedStatus(),
    statusDuration: 90,
    hitEffect: fxBleed,
    shootEffect: Fx.sparkShoot
  }), "bullet");
};

exports.kaijuShred = function (dmg, len) {
  return ready(extend(ShrapnelBulletType, {
    damage: dmg,
    length: len || 110,
    width: 40,
    lifetime: 18,
    fromColor: lib.c("ff8866"),
    toColor: lib.c("881122"),
    buildingDamageMultiplier: 1.15,
    status: bleedStatus(),
    statusDuration: 220,
    hitEffect: fxBleed,
    shootEffect: Fx.sparkShoot
  }), "bullet");
};

exports.slagShell = function (dmg, splash) {
  return ready(extend(ArtilleryBulletType, {
    damage: dmg,
    splashDamage: splash,
    splashDamageRadius: 36,
    speed: 2.0,
    lifetime: 90,
    width: 16,
    height: 16,
    makeFire: true,
    status: StatusEffects.burning,
    statusDuration: 140,
    frontColor: lib.c("ff8844"),
    backColor: lib.c("882200"),
    hitEffect: fxEmber,
    despawnEffect: fxEmber
  }), "shell");
};

exports.tidePulse = function (dmg) {
  return ready(extend(BasicBulletType, {
    damage: dmg,
    splashDamage: dmg * 0.55,
    splashDamageRadius: 22,
    speed: 3.6,
    lifetime: 55,
    width: 11,
    height: 13,
    status: StatusEffects.wet,
    statusDuration: 90,
    knockback: 1.1,
    frontColor: lib.c("70e0c8"),
    backColor: lib.c("206050"),
    hitEffect: fxTide,
    despawnEffect: fxTide
  }), "missile");
};

exports.voidRift = function (dmg) {
  return ready(extend(BasicBulletType, {
    damage: dmg,
    speed: 4.0,
    lifetime: 48,
    width: 10,
    height: 12,
    pierce: true,
    pierceCap: 3,
    status: StatusEffects.sapped,
    statusDuration: 100,
    frontColor: lib.c("cc88ff"),
    backColor: lib.c("330055"),
    trailChance: 0.4,
    trailColor: lib.c("aa66ff"),
    hitEffect: fxVoid
  }), "bullet");
};

exports.stormEmp = function (dmg) {
  return ready(extend(BasicBulletType, {
    damage: dmg,
    splashDamage: dmg * 0.4,
    splashDamageRadius: 28,
    speed: 3.2,
    lifetime: 40,
    width: 12,
    height: 12,
    status: StatusEffects.shocked,
    statusDuration: 80,
    lightning: 3,
    lightningLength: 7,
    lightningDamage: dmg * 0.25,
    lightningColor: lib.c("88ccff"),
    frontColor: lib.c("aaccff"),
    backColor: lib.c("334466"),
    hitEffect: fxStorm
  }), "bullet");
};

exports.goldOrb = function (dmg) {
  return ready(extend(BasicBulletType, {
    damage: dmg,
    speed: 2.8,
    lifetime: 70,
    width: 12,
    height: 12,
    weaveScale: 6,
    weaveMag: 2.5,
    status: StatusEffects.shocked,
    statusDuration: 40,
    frontColor: lib.c("ffe080"),
    backColor: lib.c("886600"),
    hitEffect: fxGold,
    trailChance: 0.35,
    trailColor: lib.c("ffcc66")
  }), "missile");
};

exports.aegisSlug = function (dmg) {
  return ready(extend(BasicBulletType, {
    damage: dmg,
    speed: 4.2,
    lifetime: 42,
    width: 9,
    height: 11,
    pierce: true,
    pierceCap: 2,
    status: StatusEffects.slow,
    statusDuration: 50,
    frontColor: lib.c("80e0b0"),
    backColor: lib.c("205040"),
    hitEffect: Fx.hitBulletColor
  }), "bullet");
};

exports.torpedo = function (dmg) {
  return ready(extend(BasicBulletType, {
    damage: dmg,
    splashDamage: dmg * 0.7,
    splashDamageRadius: 26,
    speed: 2.6,
    lifetime: 80,
    width: 10,
    height: 14,
    trailChance: 0.5,
    trailColor: lib.c("66aacc"),
    status: StatusEffects.wet,
    statusDuration: 100,
    frontColor: lib.c("88d0e8"),
    backColor: lib.c("204860"),
    hitEffect: fxTide,
    collidesAir: false
  }), "missile");
};

exports.kaijuNova = function () {
  return ready(extend(BasicBulletType, {
    damage: 320,
    splashDamage: 1100,
    splashDamageRadius: 110,
    speed: 2.8,
    lifetime: 18,
    width: 24,
    height: 24,
    status: StatusEffects.melting,
    statusDuration: 180,
    frontColor: lib.c("ffd37f"),
    backColor: lib.c("aa1122"),
    hitEffect: Fx.massiveExplosion,
    despawnEffect: Fx.massiveExplosion
  }), "shell");
};

Log.info("[Aoen] custom bullets ready (no recursive hit)");
