"""MCP Server de analisis de ventas. Lo consume Google ADK por stdio."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from lib.analysis import (  # noqa: E402
    correlaciones,
    distribucion_categorica,
    estadisticas_basicas,
    load_analytics_frame,
    segmentacion,
    tendencias,
    ventas_por_mes,
)
from lib.plots import FIG_DIR  # noqa: E402

mcp = FastMCP(
    "ventas-sog2",
    instructions=(
        "Herramientas de analisis de ventas online 2021. "
        "Usa estas tools para responder con cifras reales; no inventes datos."
    ),
)


def _dump(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str, indent=2)


@mcp.tool()
def estadisticas_descriptivas() -> str:
    """Media, mediana, moda y dispersion de variables numericas (edad, venta_total, n_compras, monto_compra, tiempo)."""
    return _dump(estadisticas_basicas())


@mcp.tool()
def exploratorio_distribuciones() -> str:
    """Distribucion de ventas por mes, metodo de pago, navegador, boletin y vale."""
    df = load_analytics_frame()
    return _dump(
        {
            "ventas_por_mes": ventas_por_mes(df),
            "por_metodo_pago": distribucion_categorica(df, "metodo_pago"),
            "por_navegador": distribucion_categorica(df, "navegador"),
            "por_boletin": distribucion_categorica(df, "boletin"),
            "por_vale": distribucion_categorica(df, "vale"),
        }
    )


@mcp.tool()
def analisis_tendencias() -> str:
    """Meses con mas/menos ventas, navegadores, efectivo/contra entrega, meses de boletines y vales."""
    return _dump(tendencias())


@mcp.tool()
def segmentacion_clientes() -> str:
    """Patrones de compra por rango de edad, genero y uso de boletin/vale."""
    return _dump(segmentacion())


@mcp.tool()
def analisis_correlacion() -> str:
    """Correlacion edad-venta_total, genero-metodo de pago, y boletin-vale."""
    return _dump(correlaciones())


@mcp.tool()
def listar_graficos() -> str:
    """Lista los PNG generados (al menos 7 tipos) para el informe y el chat."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(p.name for p in FIG_DIR.glob("*.png"))
    return _dump({"directorio": str(FIG_DIR), "graficos": files, "n": len(files)})


if __name__ == "__main__":
    mcp.run()
