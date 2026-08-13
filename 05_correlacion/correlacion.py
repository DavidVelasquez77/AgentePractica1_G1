"""5. Analisis de correlacion."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.analysis import correlaciones, save_json  # noqa: E402


def main() -> None:
    payload = correlaciones()
    save_json(payload, ROOT / "outputs" / "05_correlacion.json")
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
