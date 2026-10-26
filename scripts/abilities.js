// Custom abilities — full Ability API (update/draw/death)

/** Body crush — continuous serpent damage in hitbox (JS-only) */
exports.serpentCrush = function (dps, radiusMul) {
  const dps0 = dps;
  const rMul = radiusMul == null ? 1.15 : radiusMul;
  return extend(Ability, {
    update(unit) {
      const r = unit.hitSize * rMul;
      Units.nearbyEnemies(unit.team, unit.x, unit.y, r, u => {
        u.damagePierce(dps0 * Time.delta);
        if (Mathf.chance(0.04 * Time.delta)) {
          u.apply(StatusEffects.slow, 20);
        }
      });
      // crush tiles/buildings under body
      Damage.damage(unit.team, unit.x, unit.y, r, dps0 * 0.45 * Time.delta, false, true);
    },
    draw(unit) {
      Draw.z(Layer.flyingUnitLow);
      Draw.color(Color.valueOf("aa88ff"));
      Draw.alpha(0.12);
      Fill.circle(unit.x, unit.y, unit.hitSize * rMul);
      Draw.reset();
    },
    localized() {
      return "Serpent Crush";
    },
    copy() {
      return exports.serpentCrush(dps0, rMul);
    }
  });
};

/** Bahamut shackles — sap aura + periodic chain-break EMP + death nova */
exports.bahamutShackles = function () {
  return extend(Ability, {
    timer: 0,
    update(unit) {
      this.timer += Time.delta;
      Units.nearbyEnemies(unit.team, unit.x, unit.y, 64, u => {
        u.apply(StatusEffects.sapped, 20);
      });
      if (this.timer >= 90) {
        this.timer = 0;
        Effect.shake(3, 3, unit);
        Units.nearbyEnemies(unit.team, unit.x, unit.y, 72, u => {
          u.apply(StatusEffects.unmoving, 35);
          u.damage(40);
          if (u.shield > 0) {
            u.shield = Math.max(0, u.shield - 80);
          }
        });
        Fx.explosion.at(unit.x, unit.y);
      }
    },
    draw(unit) {
      Draw.z(Layer.effect);
      const f = Mathf.absin(Time.time, 12, 1);
      Draw.color(Color.valueOf("c0c8d8"));
      Draw.alpha(0.25 + f * 0.15);
      Lines.stroke(1.5);
      Lines.circle(unit.x, unit.y, 40 + f * 6);
      Draw.color(Color.valueOf("ff4466"));
      Draw.alpha(0.2);
      Lines.circle(unit.x, unit.y, 56);
      Draw.reset();
    },
    death(unit) {
      Damage.damage(unit.team, unit.x, unit.y, 96, 500, true, true);
      Fx.dynamicExplosion.at(unit.x, unit.y);
    },
    localized() {
      return "Wings of Terror";
    },
    copy() {
      return exports.bahamutShackles();
    }
  });
};

Log.info("[Aoen] custom abilities ready");
