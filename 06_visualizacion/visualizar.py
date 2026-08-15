"""6. Visualizacion: al menos siete tipos de grafico."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.analysis import save_json  # noqa: E402
from lib.plots import generate_all_figures  # noqa: E402


def main() -> None:
    paths = generate_all_figures()
    payload = {
        "n_graficos": len(paths),
        "tipos": [
            "barras (ventas por mes)",
            "lineas (tendencia mensual)",
            "pastel (metodo de pago)",
            "dispersion (edad vs venta total)",
            "boxplot (venta por genero)",
            "heatmap (boletin vs vale)",
            "histograma (edad)",
            "barras (navegador)",
            "barras (ventas por boletin)",
            "barras (ventas por vale)",
        ],
        "archivos": paths,
    }
    save_json(payload, ROOT / "outputs" / "06_visualizacion.json")
    print("Graficos:", len(paths))
    for p in paths:
        print(" -", p)


if __name__ == "__main__":
    main()
