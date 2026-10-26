"""Build aoen.zip and install ONLY that into Steam Mindustry mods. Remove folder duplicates."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

SRC = Path.home() / "OneDrive" / "Desktop" / "Aoen"
STEAM_MODS = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Mindustry\saves\mods")
APP_MODS = Path.home() / "AppData" / "Roaming" / "Mindustry" / "mods"
ZIP_NAME = "aoen.zip"
SKIP = {"tools", "__pycache__", ".git"}


def kill_path(p: Path) -> None:
    if not p.exists():
        return
    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        print("removed", p)
    except OSError as e:
        print("keep/fail", p, e)


def collect_files() -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for path in SRC.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(SRC)
        if rel.parts and rel.parts[0] in SKIP:
            continue
        if path.suffix.lower() in {".zip", ".pyc"}:
            continue
        # never pack double-prefixed sprites
        if path.suffix.lower() == ".png" and path.name.startswith("aoen-"):
            print("skip double-prefix sprite", rel)
            continue
        out.append((path, "/".join(rel.parts)))
    return out


def build_zip(dest: Path) -> int:
    files = collect_files()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arc in sorted(files, key=lambda x: x[1]):
            zf.write(src, arc)
    return len(files)


def wipe_aoen_everywhere() -> None:
    """Remove every aoen/Aoen/dark-page folder or zip except we recreate aoen.zip after."""
    for root in (STEAM_MODS, APP_MODS):
        if not root.exists():
            continue
        for p in list(root.iterdir()):
            n = p.name.lower()
            if any(k in n for k in ("aoen", "dark-page", "darkpage", "parade-aoen", "misha-dark")):
                kill_path(p)


def main() -> int:
    # also clear Desktop leftover zips that confuse installs
    for name in ("Aoen.zip", "Aoen-flat.zip", "aoen.zip", "dark-page.zip"):
        kill_path(SRC.parent / name)

    wipe_aoen_everywhere()

    steam_zip = STEAM_MODS / ZIP_NAME
    n = build_zip(steam_zip)
    # mirror on Desktop for backup (single zip)
    desk_zip = SRC.parent / ZIP_NAME
    shutil.copy2(steam_zip, desk_zip)

    # if Windows left a folder somehow, kill it again (case-insensitive)
    for name in ("aoen", "Aoen", "AOEN"):
        p = STEAM_MODS / name
        if p.exists() and p.is_dir():
            kill_path(p)
        p2 = APP_MODS / name
        if p2.exists():
            kill_path(p2)

    left = [p.name for p in STEAM_MODS.iterdir() if "aoen" in p.name.lower()]
    print(f"installed {steam_zip} ({n} files)")
    print(f"desktop copy: {desk_zip}")
    print("steam aoen entries:", left)
    return 0 if left == [ZIP_NAME] or left == ["aoen.zip"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
