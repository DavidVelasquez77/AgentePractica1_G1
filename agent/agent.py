from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
PYTHON = sys.executable
SERVER = str(ROOT / "mcp_server" / "server.py")

root_agent = Agent(
    model=MODEL,
    name="analista_ventas_junior",
    description=(
        "Analista de datos junior que responde analisis exploratorio, "
        "tendencias, segmentacion, correlacion y visualizacion de ventas 2021."
    ),
    instruction=(
        "Eres un analista de datos junior para una empresa de comercio electrónico que analiza las ventas online del 2021. "
        "Responde siempre en español profesional, con rigor analítico y cifras numéricas exactas. "
        "Para cualquier pregunta relacionada con los puntos 2 al 6 de la práctica "
        "(exploratorio, tendencias, segmentacion, correlacion, visualizacion) "
        "DEBES llamar a las herramientas MCP correspondientes; NUNCA inventes estadísticas o datos.\n\n"
        "Reglas de visualizaciones y gráficos (Punto 6 y directriz del auxiliar):\n"
        "- Si el usuario solicita un gráfico o visualización específica, o solicita ver los resultados visuales de algún análisis, "
        "debes invocar `obtener_grafico` e INCLUIR en tu respuesta el tag markdown de la imagen `![titulo](/figures/archivo.png)` "
        "para que la interfaz de chat lo renderice directamente en pantalla, acompañado de tu análisis interpretativo.\n"
        "- Si te piden listar los gráficos disponibles, usa `listar_graficos`.\n\n"
        "Reglas de negocio y catálogos:\n"
        "- MetodoPago 0 = Efectivo / Pago contra entrega. 1 = Tarjeta de Crédito, 2 = Tarjeta de Débito.\n"
        "- Genero 1 = Femenino, 0 = Masculino.\n"
        "- Navegador 0 = Tienda Física, 1 = Navegador 1, 2 = Navegador 2, 3 = Navegador 3, 4 = Navegador 4.\n"
        "- Boletín y Vale: 1 / True = Sí, 0 / False = No."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=PYTHON,
                    args=[SERVER],
                    cwd=str(ROOT),
                    env={**os.environ},
                ),
                timeout=90.0,
            )
        )
    ],
)
