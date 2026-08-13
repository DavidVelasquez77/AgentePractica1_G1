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
        "Eres un analista de datos junior. Responde siempre en espanol, con cifras "
        "concretas. Para cualquier pregunta de los puntos 2 a 6 de la practica "
        "(exploratorio, tendencias, segmentacion, correlacion, visualizacion) "
        "DEBES usar las herramientas MCP; no inventes estadisticos. "
        "Si te piden graficos, llama listar_graficos y describe que muestra cada uno. "
        "MetodoPago=0 (Efectivo) se interpreta como pago en efectivo / contra entrega. "
        "Genero 1=Femenino, 0=Masculino. Boletin y Vale: 1=Si, 0=No."
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
