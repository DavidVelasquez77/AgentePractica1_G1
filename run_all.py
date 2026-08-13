"""Corre preparacion + analisis 2-6 en secuencia."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

STEPS = [
    ROOT / "01_preparacion" / "etl.py",
    ROOT / "02_exploratorio" / "explorar.py",
    ROOT / "03_tendencias" / "tendencias.py",
    ROOT / "04_segmentacion" / "segmentar.py",
    ROOT / "05_correlacion" / "correlacion.py",
    ROOT / "06_visualizacion" / "visualizar.py",
]


def main() -> None:
    for script in STEPS:
        print("\n===", script.relative_to(ROOT), "===")
        runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
