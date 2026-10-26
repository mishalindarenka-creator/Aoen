// Aoen: spawn all mod units on proving-grounds so textures are visible in-game.
const AOEN_UNITS = [
  "aoen-crab", "aoen-crab-t2", "aoen-ceramtyr-daimyo", "aoen-quake-bulwark", "aoen-storm-sovereign", "aoen-eclipse-tyrant",
  "aoen-snake", "aoen-snake-t2", "aoen-cinder-millipede", "aoen-payload-serpent", "aoen-singularity-eel", "aoen-ouroboros-prime",
  "aoen-boomeranger", "aoen-boomeranger-t2", "aoen-foundry-orbiter", "aoen-aegis-walker", "aoen-nexus-prime", "aoen-apotheosis-core",
  "aoen-naval", "aoen-naval-t2", "aoen-iron-reef", "aoen-needle-skiff", "aoen-leviathan-crown", "aoen-mare-imperator"
];

function isProving() {
  try {
    const n = Vars.state.map != null ? (Vars.state.map.name() || Vars.state.map.plainName() || "") : "";
    const tags = Vars.state.rules != null && Vars.state.rules.tags != null ? Vars.state.rules.tags.get("aoen-proving", "0") : "0";
    return n.toLowerCase().indexOf("proving") >= 0 || n.indexOf("aoen-proving") >= 0 || tags === "1";
  } catch (e) {
    return false;
  }
}

function spawnGallery() {
  if (!Vars.state || Vars.state.isEditor()) return;
  if (!isProving()) return;
  const team = Vars.player != null ? Vars.player.team() : Team.sharded;
  const cx = Vars.world.width() / 2;
  const cy = Vars.world.height() / 2;
  let i = 0;
  AOEN_UNITS.forEach(id => {
    const ut = Vars.content.unit(id);
    if (ut == null) {
      Log.warn("[Aoen] missing unit " + id);
      return;
    }
    const col = i % 5;
    const row = Math.floor(i / 5);
    const x = (cx - 10 + col * 6) * Vars.tilesize;
    const y = (cy - 6 + row * 6) * Vars.tilesize;
    ut.spawn(team, x, y);
    i++;
  });
  Log.info("[Aoen] proving gallery: spawned " + i + " units");
}

Events.on(WorldLoadEvent, e => {
  Timer.schedule(() => spawnGallery(), 1.5);
});
