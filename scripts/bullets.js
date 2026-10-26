/**
 * Aoen custom bullet types — unique behaviour beyond HJSON.
 * Each line gets signature projectiles; enhance.js wires them onto weapons.
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

const fragCatastrophe = extend(BasicBulletType, {
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
  statusDuration: 80
});

/** Proto Bahamut — Catastrophe */
exports.catastrophe = extend(BasicBulletType, {
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
  fragBullet: fragCatastrophe,
  update(b) {
    this.super$update(b);
    Units.nearbyEnemies(b.team, b.x, b.y, 64, u => {
      u.vel.trns(Angles.angle(u.x, u.y, b.x, b.y), 0.35 * Time.delta);
    });
  },
  hit(b, x, y) {
    this.super$hit(b, x, y);
    Units.nearbyEnemies(b.team, x, y, 56, u => {
      u.apply(StatusEffects.unmoving, 50);
      u.apply(StatusEffects.sapped, 120);
      if (u.shield > 0) u.shield = Math.max(0, u.shield - 120);
    });
  },
  draw(b) {
    this.super$draw(b);
    Draw.z(Layer.bullet + 1);
    Draw.color(lib.c("ff6688"));
    Fill.circle(b.x, b.y, 5 + Mathf.absin(b.time, 6, 3));
    Draw.color(Color.white);
    Fill.circle(b.x, b.y, 2);
    Draw.reset();
  }
});

exports.darkBreath = extend(ContinuousLaserBulletType, {
  damage: 95,
  length: 180,
  width: 16,
  lifetime: 55,
  shake: 1.5,
  buildingDamageMultiplier: 1.2,
  status: StatusEffects.melting,
  statusDuration: 100,
  update(b) {
    this.super$update(b);
    if (b.time > 20) {
      b.damage = this.damage * (1 + Math.min(b.time / 55, 1) * 0.6);
    }
  }
});
exports.darkBreath.colors = [lib.c("ff4466"), lib.c("aa1122"), lib.c("1a0810")];

exports.wingMissile = extend(MissileBulletType, {
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
  hitEffect: Fx.blastExplosion,
  update(b) {
    this.super$update(b);
    if (Mathf.chance(0.2 * Time.delta)) Fx.smoke.at(b.x, b.y);
  }
});

exports.venomFang = function (damage, splash) {
  return extend(BasicBulletType, {
    damage: damage,
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
    despawnEffect: fxVenom,
    hit(b, x, y) {
      this.super$hit(b, x, y);
      Damage.damage(b.team, x, y, 14, splash, false, true);
      Units.nearbyEnemies(b.team, x, y, 14, u => {
        u.apply(StatusEffects.corroded, 80);
        u.apply(StatusEffects.slow, 40);
      });
    }
  });
};

/** Crab claw shredder — short pierce shrapnel-feel */
exports.clawShred = function (dmg) {
  return extend(ShrapnelBulletType, {
    damage: dmg,
    length: 42,
    width: 16,
    lifetime: 14,
    fromColor: lib.c("e8d8b0"),
    toColor: lib.c("665544"),
    status: lib.status("aoen-bleeding") || StatusEffects.sapped,
    statusDuration: 90,
    hitEffect: fxBleed,
    shootEffect: Fx.sparkShoot
  });
};

/** Crabzilla / tyrant mega shred */
exports.kaijuShred = function (dmg, len) {
  return extend(ShrapnelBulletType, {
    damage: dmg,
    length: len || 110,
    width: 40,
    lifetime: 18,
    fromColor: lib.c("ff8866"),
    toColor: lib.c("881122"),
    buildingDamageMultiplier: 1.15,
    status: lib.status("aoen-bleeding") || StatusEffects.sapped,
    statusDuration: 220,
    hitEffect: fxBleed,
    shootEffect: Fx.sparkShoot
  });
};

/** Ember slag mortar */
exports.slagShell = function (dmg, splash) {
  return extend(ArtilleryBulletType, {
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
    despawnEffect: fxEmber,
    hit(b, x, y) {
      this.super$hit(b, x, y);
      try {
        const t = Vars.world.tileWorld(x, y);
        if (t != null) Fires.create(t);
      } catch (e) {}
    }
  });
};

/** Tide wet pulse */
exports.tidePulse = function (dmg) {
  return extend(BasicBulletType, {
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
    despawnEffect: fxTide,
    hit(b, x, y) {
      this.super$hit(b, x, y);
      Units.nearbyEnemies(b.team, x, y, 24, u => u.apply(StatusEffects.wet, 70));
    }
  });
};

/** Void rift bolt — pulls + saps */
exports.voidRift = function (dmg) {
  return extend(BasicBulletType, {
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
    hitEffect: fxVoid,
    update(b) {
      this.super$update(b);
      Units.nearbyEnemies(b.team, b.x, b.y, 28, u => {
        u.vel.trns(Angles.angle(u.x, u.y, b.x, b.y), 0.2 * Time.delta);
      });
    }
  });
};

/** Storm EMP spark */
exports.stormEmp = function (dmg) {
  return extend(BasicBulletType, {
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
    frontColor: lib.c("aaccff"),
    backColor: lib.c("334466"),
    hitEffect: fxStorm,
    hit(b, x, y) {
      this.super$hit(b, x, y);
      for (var i = 0; i < 3; i++) {
        Lightning.create(b.team, lib.c("88ccff"), dmg * 0.2, x, y, b.rotation() + Mathf.range(40), 6);
      }
    }
  });
};

/** Gold orb bounce-ish (boomeranger) */
exports.goldOrb = function (dmg) {
  return extend(BasicBulletType, {
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
    trailColor: lib.c("ffcc66"),
    draw(b) {
      this.super$draw(b);
      Draw.color(lib.c("ffe080"));
      Fill.circle(b.x, b.y, 3 + Mathf.absin(b.time, 5, 2));
      Draw.reset();
    }
  });
};

/** Aegis green slug */
exports.aegisSlug = function (dmg) {
  return extend(BasicBulletType, {
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
    hitEffect: Fx.hitBulletColor,
    hit(b, x, y) {
      this.super$hit(b, x, y);
      // small heal pulse to allies
      Units.nearby(b.team, x, y, 20, u => {
        if (u.damaged()) u.heal(1.5);
      });
    }
  });
};

/** Naval torpedo — wet + splash */
exports.torpedo = function (dmg) {
  return extend(BasicBulletType, {
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
  });
};

/** Crabzilla nova shell */
exports.kaijuNova = function () {
  return extend(BasicBulletType, {
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
    despawnEffect: Fx.massiveExplosion,
    hit(b, x, y) {
      this.super$hit(b, x, y);
      Units.nearbyEnemies(b.team, x, y, 96, u => {
        u.apply(StatusEffects.unmoving, 40);
        u.apply(StatusEffects.burning, 80);
      });
    }
  });
};

Log.info("[Aoen] custom bullets ready (claw/venom/slag/tide/void/storm/orb/aegis/torpedo/kaiju)");
