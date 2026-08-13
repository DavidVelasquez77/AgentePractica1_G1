"""2. Analisis exploratorio: stats y distribuciones desde la BD."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.analysis import (  # noqa: E402
    distribucion_categorica,
    estadisticas_basicas,
    load_analytics_frame,
    save_json,
    ventas_por_mes,
)
from lib.plots import generate_all_figures  # noqa: E402


def main() -> None:
    df = load_analytics_frame()
    payload = {
        "n_registros": int(len(df)),
        "estadisticas_basicas": estadisticas_basicas(df),
        "ventas_por_mes": ventas_por_mes(df),
        "por_metodo_pago": distribucion_categorica(df, "metodo_pago"),
        "por_navegador": distribucion_categorica(df, "navegador"),
        "por_boletin": distribucion_categorica(df, "boletin"),
        "por_vale": distribucion_categorica(df, "vale"),
        "figuras": generate_all_figures(df),
    }
    save_json(payload, ROOT / "outputs" / "02_exploratorio.json")
    print("OK exploratorio:", ROOT / "outputs" / "02_exploratorio.json")


if __name__ == "__main__":
    main()
