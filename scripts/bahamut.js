/**
 * Proto Bahamut (GBF) — summon aura + Catastrophe / shackle-break behaviour.
 * Lore: "In response to an earnest plea, the dragon breaks its shackles."
 */
const lib = require("lib");
const bullets = require("bullets");
const abilities = require("abilities");

/** Proto Bahamut's Aura — all elemental ATK feel → ally damage buff field */
exports.protoAura = function () {
  return extend(Ability, {
    update(unit) {
      Units.nearby(unit.team, unit.x, unit.y, 72, u => {
        if (u !== unit) {
          u.apply(StatusEffects.overclock, 20);
        }
      });
    },
    draw(unit) {
      Draw.z(Layer.effect);
      const f = Mathf.absin(Time.time, 16, 1);
      Draw.color(Color.valueOf("aa2244"));
      Draw.alpha(0.1 + f * 0.08);
      Lines.stroke(2);
      Lines.circle(unit.x, unit.y, 48 + f * 4);
      Draw.color(Color.valueOf("c0c8d8"));
      Draw.alpha(0.15);
      Lines.circle(unit.x, unit.y, 36);
      Draw.reset();
    },
    localized() {
      return "Proto Bahamut's Aura";
    },
    copy() {
      return exports.protoAura();
    }
  });
};

exports.apply = function () {
  const u = lib.unit("aoen-bahamut");
  if (u == null) {
    Log.warn("[Aoen] Proto Bahamut missing");
    return;
  }
  // Prefer localized name feel
  try {
    u.localizedName = "Proto Bahamut";
  } catch (e) {}

  lib.addAbility(u, abilities.bahamutShackles());
  lib.addAbility(u, exports.protoAura());

  lib.eachWeapon(u, w => {
    const n = w.name != null ? ("" + w.name) : "";
    if (n.indexOf("catastrophe") >= 0) {
      w.bullet = bullets.catastrophe;
      // reinforce GBF Catastrophe numbers
      w.bullet.damage = 320;
      w.bullet.splashDamage = 520;
      w.bullet.splashDamageRadius = 88;
    }
    if (n.indexOf("breath") >= 0) {
      w.bullet = bullets.darkBreath;
    }
    if (n.indexOf("wing-missile") >= 0 || n.indexOf("orb") >= 0) {
      // keep HJSON; orb already weave
    }
    if (n.indexOf("claw") >= 0 && w.bullet != null) {
      const bleed = lib.status("aoen-bleeding");
      if (bleed != null) {
        w.bullet.status = bleed;
        w.bullet.statusDuration = 180;
      }
      w.bullet.damage = Math.max(w.bullet.damage, 155);
    }
  });

  Log.info("[Aoen] Proto Bahamut GBF 1:1 behaviours applied");
};
