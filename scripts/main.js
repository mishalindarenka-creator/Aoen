/**
 * Aoen — JavaScript is the primary logic layer (full Mindustry API).
 * HJSON defines static content/sprites; scripts override bullets, abilities, combat.
 */
require("lib");
require("bullets");
require("abilities");
require("serpent");
require("bahamut");
require("enhance");

const AOEN_UNITS = [
  "aoen-crab", "aoen-crab-t2", "aoen-ceramtyr-daimyo", "aoen-quake-bulwark", "aoen-storm-sovereign", "aoen-eclipse-tyrant", "aoen-crabzilla",
  "aoen-snake", "aoen-snake-t2", "aoen-cinder-millipede", "aoen-payload-serpent", "aoen-singularity-eel", "aoen-ouroboros-prime", "aoen-ouroboros-apex",
  "aoen-boomeranger", "aoen-boomeranger-t2", "aoen-foundry-orbiter", "aoen-aegis-walker", "aoen-nexus-prime", "aoen-apotheosis-core", "aoen-apotheosis-omega",
  "aoen-naval", "aoen-naval-t2", "aoen-iron-reef", "aoen-needle-skiff", "aoen-leviathan-crown", "aoen-mare-imperator", "aoen-mare-absolution",
  "aoen-aether-mote", "aoen-gale-wisp", "aoen-storm-kite", "aoen-void-raptor", "aoen-aether-wyvern", "aoen-sky-colossus", "aoen-firmament-throne",
  "aoen-bahamut"
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
    const col = i % 6;
    const row = Math.floor(i / 6);
    const x = (cx - 12 + col * 6) * Vars.tilesize;
    const y = (cy - 8 + row * 6) * Vars.tilesize;
    ut.spawn(team, x, y);
    i++;
  });
  Log.info("[Aoen] proving gallery: spawned " + i + " units");
}

Events.on(WorldLoadEvent, e => {
  Timer.schedule(() => spawnGallery(), 1.5);
});

Events.on(PlayerChatEvent, e => {
  try {
    const msg = e.message;
    if (msg === "/aoen-buff" || msg === "aoen-buff") {
      require("enhance").run();
      if (e.player != null) {
        e.player.sendMessage("[accent][Aoen][] JS enhance re-applied.");
      }
    }
  } catch (err) {
    Log.err(err);
  }
});

Log.info("[Aoen] JS API layer loaded (bullets + abilities + enhance)");
