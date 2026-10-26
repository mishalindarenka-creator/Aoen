/**
 * Calamity-style worm body: head = unit, body = trail of segment sprites.
 * Replaces broken crawl stacking.
 */
const lib = require("lib");

function atlasSeg(stem, i) {
  const r = Core.atlas.find("aoen-" + stem + "-segment" + i);
  if (r != null && r.found()) return r;
  return Core.atlas.find("aoen-" + stem);
}

/**
 * @param {{stem:string, segs:number, spacing:number, dps:number, hitR:number, status?:StatusEffect, statusDur?:number, tint?:Color, name?:string}} cfg
 */
exports.wormBody = function (cfg) {
  const stem = cfg.stem;
  const segs = cfg.segs;
  const spacing = cfg.spacing;
  const dps = cfg.dps;
  const hitR = cfg.hitR;
  const status = cfg.status || null;
  const statusDur = cfg.statusDur || 40;
  const tint = cfg.tint || null;
  const label = cfg.name || "Serpent Body";

  return extend(Ability, {
    trail: null,
    update(unit) {
      if (this.trail == null) this.trail = [];

      const need = this.trail.length === 0 ||
        Mathf.dst(this.trail[0].x, this.trail[0].y, unit.x, unit.y) >= spacing;

      if (need) {
        this.trail.unshift({ x: unit.x, y: unit.y, rot: unit.rotation });
        while (this.trail.length > segs) {
          this.trail.pop();
        }
      } else if (this.trail.length > 0) {
        // soft follow: ease first knot toward head for smoother curve
        this.trail[0].x = Mathf.lerp(this.trail[0].x, unit.x, 0.15);
        this.trail[0].y = Mathf.lerp(this.trail[0].y, unit.y, 0.15);
        this.trail[0].rot = Mathf.slerpDelta(this.trail[0].rot, unit.rotation, 0.2);
      }

      // body contact damage (Calamity worm hitboxes)
      for (var i = 0; i < this.trail.length; i++) {
        const p = this.trail[i];
        const r = hitR * (1 - i / (segs + 2) * 0.35);
        Units.nearbyEnemies(unit.team, p.x, p.y, r, u => {
          u.damagePierce(dps * Time.delta);
          if (status != null && Mathf.chance(0.05 * Time.delta)) {
            u.apply(status, statusDur);
          }
        });
        if (i % 2 === 0) {
          Damage.damage(unit.team, p.x, p.y, r * 0.85, dps * 0.35 * Time.delta, false, true);
        }
      }
    },
    draw(unit) {
      if (this.trail == null || this.trail.length === 0) return;
      Draw.z(Layer.groundUnit - 1);
      for (var i = this.trail.length - 1; i >= 0; i--) {
        const p = this.trail[i];
        const si = Math.min(i, segs - 1);
        const reg = atlasSeg(stem, si);
        if (tint != null) Draw.color(tint);
        Draw.rect(reg, p.x, p.y, p.rot - 90);
        Draw.color();
      }
      Draw.reset();
    },
    localized() {
      return label;
    },
    copy() {
      return exports.wormBody(cfg);
    }
  });
};

/** Desert Scourge — sand burst when moving fast */
exports.desertBurrow = function () {
  return extend(Ability, {
    update(unit) {
      if (unit.vel.len() > 1.2 && Mathf.chance(0.15 * Time.delta)) {
        Fx.smoke.at(unit.x + Mathf.range(6), unit.y + Mathf.range(6));
        Units.nearbyEnemies(unit.team, unit.x, unit.y, 18, u => {
          u.apply(StatusEffects.slow, 25);
        });
      }
    },
    localized() { return "Sand Burrow"; },
    copy() { return exports.desertBurrow(); }
  });
};

/** Aquatic — wet aura */
exports.aquaticMiasma = function (range) {
  const r = range || 28;
  return extend(Ability, {
    update(unit) {
      Units.nearbyEnemies(unit.team, unit.x, unit.y, r, u => {
        u.apply(StatusEffects.wet, 30);
        u.apply(StatusEffects.corroded, 20);
      });
    },
    draw(unit) {
      Draw.z(Layer.effect);
      Draw.color(Color.valueOf("66aacc"));
      Draw.alpha(0.12);
      Fill.circle(unit.x, unit.y, r);
      Draw.reset();
    },
    localized() { return "Toxic Tide"; },
    copy() { return exports.aquaticMiasma(r); }
  });
};

/** Brimstone fire trail */
exports.brimstoneTrail = function () {
  return extend(Ability, {
    update(unit) {
      if (Mathf.chance(0.18 * Time.delta)) {
        // Fx.fireSmoke may be missing — prefer burning + smoke
        try {
          if (typeof Fx.burning !== "undefined" && Fx.burning != null) {
            Fx.burning.at(unit.x + Mathf.range(4), unit.y + Mathf.range(4));
          } else {
            Fx.smoke.at(unit.x + Mathf.range(4), unit.y + Mathf.range(4));
          }
        } catch (e2) {
          Fx.smoke.at(unit.x + Mathf.range(4), unit.y + Mathf.range(4));
        }
        try {
          const t = Vars.world.tileWorld(unit.x, unit.y);
          if (t != null) Fires.create(t);
        } catch (e) {}
      }
      Units.nearbyEnemies(unit.team, unit.x, unit.y, 22, u => {
        u.apply(StatusEffects.burning, 40);
      });
    },
    localized() { return "Brimstone Wake"; },
    copy() { return exports.brimstoneTrail(); }
  });
};

/** Storm Weaver — lightning while flying */
exports.stormWeave = function () {
  return extend(Ability, {
    t: 0,
    update(unit) {
      this.t += Time.delta;
      if (this.t < 35) return;
      this.t = 0;
      const tx = unit.x + Mathf.range(48);
      const ty = unit.y + Mathf.range(48);
      Lightning.create(unit.team, StatusEffects.shocked.color, 28, unit.x, unit.y, unit.angleTo(tx, ty), 12);
    },
    localized() { return "Storm Weave"; },
    copy() { return exports.stormWeave(); }
  });
};

/** DoG-style void pulse */
exports.voidDevour = function () {
  return extend(Ability, {
    t: 0,
    update(unit) {
      this.t += Time.delta;
      Units.nearbyEnemies(unit.team, unit.x, unit.y, 40, u => {
        u.apply(StatusEffects.sapped, 30);
        u.vel.trns(Angles.angle(u.x, u.y, unit.x, unit.y), 0.2 * Time.delta);
      });
      if (this.t >= 100) {
        this.t = 0;
        Damage.damage(unit.team, unit.x, unit.y, 56, 120, true, true);
        Fx.explosion.at(unit.x, unit.y);
      }
    },
    localized() { return "Cosmic Devour"; },
    copy() { return exports.voidDevour(); }
  });
};

Log.info("[Aoen] Calamity-style serpent system ready");
