// Custom bullet types — overrides update/hit/draw (beyond HJSON)
const lib = require("lib");

const darkPulse = lib.fx(28, e => {
  Draw.color(lib.c("ff4466"), lib.c("220011"), e.fin());
  Lines.stroke(3 - e.fin() * 2);
  Lines.circle(e.x, e.y, 8 + e.fin() * 48);
  Fill.circle(e.x, e.y, 4 - e.fin() * 3);
});

const venomBurst = lib.fx(18, e => {
  Draw.color(lib.c("aa88ff"), lib.c("331155"), e.fin());
  Lines.stroke(2);
  Lines.circle(e.x, e.y, 4 + e.fin() * 16);
});

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

/** Proto Bahamut — Catastrophe: pulling nova + shield break + frags */
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
  hitEffect: darkPulse,
  despawnEffect: darkPulse,
  status: StatusEffects.sapped,
  statusDuration: 180,
  fragBullets: 12,
  fragBullet: fragCatastrophe,
  update(b) {
    this.super$update(b);
    Units.nearbyEnemies(b.team, b.x, b.y, 64, u => {
      const ang = Angles.angle(u.x, u.y, b.x, b.y);
      u.vel.trns(ang, 0.35 * Time.delta);
    });
    if (Mathf.chance(0.12 * Time.delta)) {
      darkPulse.at(b.x + Mathf.range(10), b.y + Mathf.range(10));
    }
  },
  hit(b, x, y) {
    this.super$hit(b, x, y);
    Units.nearbyEnemies(b.team, x, y, 56, u => {
      u.apply(StatusEffects.unmoving, 50);
      u.apply(StatusEffects.sapped, 120);
      if (u.shield > 0) {
        u.shield = Math.max(0, u.shield - 120);
      }
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

/** Continuous dark breath with escalating damage */
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
exports.darkBreath.colors = [
  lib.c("ff4466"),
  lib.c("aa1122"),
  lib.c("1a0810")
];

/** Snake venom fang — DoT splash on hit */
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
    hitEffect: venomBurst,
    despawnEffect: venomBurst,
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

/** Homing dark wing missile */
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
    if (Mathf.chance(0.2 * Time.delta)) {
      Fx.smoke.at(b.x, b.y);
    }
  }
});

Log.info("[Aoen] custom bullets ready");
