from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(name: str) -> None:
    print("==>", name)
    subprocess.check_call([sys.executable, str(ROOT / name)], cwd=str(ROOT))


def main() -> None:
    run("fix_inline_parts.py")
    run("build_hd_sprites.py")  # NH / Exogenesis / Jababarium style remap
    run("build_snake_sprites.py")
    run("build_bahamut_sprites.py")
    run("build_naval_sprites.py")
    run("ensure_unit_sprites.py")
    run("build_block_sprites.py")
    run("fix_ohno.py")
    run("validate_mod.py")


if __name__ == "__main__":
    main()
