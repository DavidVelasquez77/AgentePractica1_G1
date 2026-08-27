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


GRAFICOS_CATALOGO = {
    "01_barras_ventas_mes.png": {
        "id": "1",
        "tema": "ventas_mes",
        "alias": ["mes", "ventas por mes", "barras mes", "marzo", "noviembre"],
        "tipo": "Gráfico de barras",
        "titulo": "Ventas por mes (2021)",
        "hallazgo_clave": "Marzo registró el mayor monto (Q22,994.34) y noviembre el menor (Q19,779.24).",
    },
    "02_lineas_tendencia_mes.png": {
        "id": "2",
        "tema": "tendencia_mes",
        "alias": ["tendencia", "lineas", "evolucion temporal", "serie de tiempo"],
        "tipo": "Gráfico de líneas",
        "titulo": "Tendencia mensual de ventas",
        "hallazgo_clave": "Comportamiento cíclico con picos en marzo y diciembre, y caída pronunciada en noviembre.",
    },
    "03_pastel_metodo_pago.png": {
        "id": "3",
        "tema": "metodo_pago",
        "alias": ["pago", "pastel", "tarjeta", "efectivo", "contra entrega"],
        "tipo": "Gráfico de pastel / circular",
        "titulo": "Participación de ventas por método de pago",
        "hallazgo_clave": "Tarjeta de crédito lidera con 59.1%, débito 22.7% y efectivo/contra entrega 18.6%.",
    },
    "04_dispersion_edad_venta.png": {
        "id": "4",
        "tema": "dispersion_edad_venta",
        "alias": ["dispersion", "edad venta", "scatter", "hexbin", "relacion edad"],
        "tipo": "Gráfico de dispersión (Hexbin) + Recta de regresión",
        "titulo": "¿La edad explica la venta total? No.",
        "hallazgo_clave": "Pearson r = -0.025 (p = 0.042), correlación nula. La edad no predice el monto acumulado.",
    },
    "05_boxplot_venta_genero.png": {
        "id": "5",
        "tema": "boxplot_genero",
        "alias": ["boxplot", "cajas", "genero", "mujeres vs hombres", "femenino masculino"],
        "tipo": "Diagrama de cajas (Boxplot)",
        "titulo": "¿Compran distinto mujeres y hombres?",
        "hallazgo_clave": "Medianas casi idénticas (Q137.60 mujeres vs Q137.30 hombres). No hay diferencia sustancial por género.",
    },
    "06_heatmap_boletin_vale.png": {
        "id": "6",
        "tema": "heatmap_boletin_vale",
        "alias": ["heatmap", "matriz", "boletin vale", "promociones", "contingencia"],
        "tipo": "Matriz / Heatmap de 4 cuadrantes",
        "titulo": "Distribución y cruce de Boletín vs Vale",
        "hallazgo_clave": "Chi² = 243.57 (p < 0.001). Los clientes que reciben boletín usan vales con mayor frecuencia y tienen el ticket más alto (Q242.57).",
    },
    "07_histograma_edad.png": {
        "id": "7",
        "tema": "histograma_edad",
        "alias": ["histograma", "distribucion edad", "edad", "media mediana moda"],
        "tipo": "Histograma de frecuencias",
        "titulo": "Distribución de edades de los clientes",
        "hallazgo_clave": "Media 36.31 años, mediana 36.00 años, moda 18.00 años. Fuerte presencia de compradores jóvenes.",
    },
    "08_barras_navegador.png": {
        "id": "8",
        "tema": "navegador",
        "alias": ["navegador", "canales", "tienda fisica", "navegadores"],
        "tipo": "Gráfico de barras",
        "titulo": "Ventas por canal / navegador",
        "hallazgo_clave": "Tienda física concentra 54.2% del volumen total (3,523 compras), mientras que Navegador 4 es el menos usado (3.0%).",
    },
    "09_ventas_boletin.png": {
        "id": "9",
        "tema": "ventas_boletin",
        "alias": ["boletin", "ventas boletin"],
        "tipo": "Gráfico de barras comparativo",
        "titulo": "Ventas según suscripción al boletín",
        "hallazgo_clave": "Clientes con boletín representan el 46.1% de la facturación y tienen un ticket promedio mayor.",
    },
    "10_ventas_vale.png": {
        "id": "10",
        "tema": "ventas_vale",
        "alias": ["vale", "ventas vale", "cupones"],
        "tipo": "Gráfico de barras comparativo",
        "titulo": "Ventas según redención de vales",
        "hallazgo_clave": "Clientes con vale generan un ticket promedio de Q44.95 vs Q38.55 de los clientes sin vale.",
    },
    "11_tendencia_boletines_vales_mes.png": {
        "id": "11",
        "tema": "boletines_vales_mes",
        "alias": [
            "boletin mes",
            "vale mes",
            "boletines por mes",
            "vales por mes",
            "promociones por mes",
            "tendencia promociones",
            "meses boletin",
            "meses vale",
            "3d",
            "tendencias promociones",
        ],
        "tipo": "Gráfico de barras agrupadas mensual",
        "titulo": "Uso mensual de boletines y vales (Punto 3.d)",
        "hallazgo_clave": "Diciembre y Marzo fueron los meses con mayor uso de boletines (262 y 261) y Marzo y Diciembre con mayor redención de vales (133 y 128), coincidiendo con las temporadas pico de venta.",
    },
}


@mcp.tool()
def listar_graficos() -> str:
    """Lista las visualizaciones disponibles (11 gráficos generados, cumpliendo los 7 tipos requeridos) con su ID, tipo, título y hallazgo clave."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    resumen = []
    for filename, info in GRAFICOS_CATALOGO.items():
        resumen.append(
            {
                "id": info["id"],
                "archivo": filename,
                "tipo": info["tipo"],
                "titulo": info["titulo"],
                "tema": info["tema"],
                "hallazgo": info["hallazgo_clave"],
                "ruta_relativa": f"outputs/figures/{filename}",
                "url_web": f"/figures/{filename}",
            }
        )
    return _dump({"total_graficos": len(resumen), "graficos": resumen})


@mcp.tool()
def obtener_grafico(consulta: str) -> str:
    """Obtiene la información, hallazgo y referencia markdown de una visualización específica para renderizarla directamente en el chat.
    
    Parámetro `consulta`: puede ser el número del gráfico ('1'..'11'), el nombre del archivo ('01_barras_ventas_mes.png') o palabras clave como 'mes', 'pago', 'edad', 'boxplot', 'heatmap', 'navegador', 'boletin', 'vale', 'boletin mes', etc.
    """
    consulta_clean = consulta.lower().strip()
    match = None

    for filename, info in GRAFICOS_CATALOGO.items():
        if (
            consulta_clean == info["id"]
            or consulta_clean == filename.lower()
            or any(alias in consulta_clean for alias in info["alias"])
            or info["tema"] in consulta_clean
        ):
            match = (filename, info)
            break

    if not match:
        match = list(GRAFICOS_CATALOGO.items())[0]

    filename, info = match
    fig_path = FIG_DIR / filename

    return _dump(
        {
            "archivo": filename,
            "tipo": info["tipo"],
            "titulo": info["titulo"],
            "hallazgo_clave": info["hallazgo_clave"],
            "markdown_img": f"![{info['titulo']}](/figures/{filename})",
            "ruta_archivo": str(fig_path),
            "url": f"/figures/{filename}",
            "instruccion_render": "Para mostrar esta imagen en la interfaz del chat, incluye la etiqueta markdown `![titulo](/figures/nombre.png)` en tu respuesta.",
        }
    )


if __name__ == "__main__":
    mcp.run()
