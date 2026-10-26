// Aoen shared helpers — full Mindustry JS API surface
exports.c = function (hex) {
  return Color.valueOf(hex);
};

exports.unit = function (id) {
  return Vars.content.unit(id);
};

exports.block = function (id) {
  return Vars.content.block(id);
};

exports.status = function (id) {
  return Vars.content.statusEffect(id);
};

exports.eachWeapon = function (unitType, fn) {
  if (unitType == null || unitType.weapons == null) return;
  for (var i = 0; i < unitType.weapons.size; i++) {
    fn(unitType.weapons.get(i), i);
  }
};

exports.addAbility = function (unitType, ability) {
  if (unitType == null || ability == null) return;
  if (unitType.abilities == null) {
    unitType.abilities = new Seq();
  }
  unitType.abilities.add(ability);
};

exports.fx = function (life, drawer) {
  return new Effect(life, drawer);
};
