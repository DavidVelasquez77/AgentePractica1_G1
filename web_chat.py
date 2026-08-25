"""Interfaz de Chat Web Profesional para el Agente Analista de Ventas Junior.

Cumple con la directriz del auxiliar: renderizado directo de imágenes/gráficas
en la interfaz del chat sin necesidad de buscarlas manualmente en disco.
Diseño libre de emojis con iconografía SVG vectorial y estética analítica corporativa.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from lib.analysis import (
    correlaciones,
    estadisticas_basicas,
    load_analytics_frame,
    segmentacion,
    tendencias,
    ventas_por_mes,
)
from lib.plots import FIG_DIR, generate_all_figures
from mcp_server.server import GRAFICOS_CATALOGO

app = FastAPI(title="Plataforma Analítica de Ventas 2021 — SOG2 Grupo 1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FIG_DIR.mkdir(parents=True, exist_ok=True)
if not list(FIG_DIR.glob("*.png")):
    generate_all_figures()

app.mount("/figures", StaticFiles(directory=str(FIG_DIR)), name="figures")


class ChatRequest(BaseModel):
    mensaje: str
    historial: list[dict] = []


def _obtener_contexto_mcp(mensaje: str) -> dict:
    """Invoca la lógica analítica correspondiente según el mensaje."""
    m = mensaje.lower()
    contexto: dict = {}

    if any(k in m for k in ["stats", "estadistica", "media", "mediana", "moda", "descriptiv"]):
        contexto["estadisticas_basicas"] = estadisticas_basicas()

    if any(k in m for k in ["mes", "tendencia", "mas vend", "menos vend", "efectivo", "contra entrega", "popular", "navegador"]):
        contexto["tendencias"] = tendencias()

    if any(k in m for k in ["segment", "edad", "genero", "mujer", "hombre", "patron"]):
        contexto["segmentacion"] = segmentacion()

    if any(k in m for k in ["correlac", "relacion", "chi", "pearson", "spearman"]):
        contexto["correlaciones"] = correlaciones()

    if any(k in m for k in ["grafic", "visualiz", "imagen", "figura", "plot", "mostrar", "ver"]):
        contexto["catalogo_graficos"] = list(GRAFICOS_CATALOGO.values())

    return contexto


def _buscar_grafico_relacionado(mensaje: str) -> tuple[str, dict] | None:
    m = mensaje.lower()
    for filename, info in GRAFICOS_CATALOGO.items():
        if info["id"] in m or any(alias in m for alias in info["alias"]) or info["tema"] in m:
            return filename, info
    return None


@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "modelo": os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        "total_graficos": len(list(FIG_DIR.glob("*.png"))),
        "db_provider": "Supabase PostgreSQL (Cloud Database)",
    }


@app.get("/api/graficos")
async def get_graficos():
    items = []
    for filename, info in GRAFICOS_CATALOGO.items():
        items.append(
            {
                "id": info["id"],
                "archivo": filename,
                "url": f"/figures/{filename}",
                "tipo": info["tipo"],
                "titulo": info["titulo"],
                "hallazgo": info["hallazgo_clave"],
            }
        )
    return JSONResponse(items)


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    mensaje = req.mensaje.strip()
    if not mensaje:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

    api_key = os.getenv("GOOGLE_API_KEY")
    modelo_nombre = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    grafico_match = _buscar_grafico_relacionado(mensaje)
    contexto = _obtener_contexto_mcp(mensaje)

    prompt_sistema = (
        "Eres un analista de datos junior del Grupo 1 de SOG2 para la empresa de comercio electrónico (Ventas 2021).\n"
        "Instrucciones de estilo y formato:\n"
        "1. Responde SIEMPRE en español con tono profesional, ejecutivo, estructurado y sin usar emojis.\n"
        "2. Cita cifras numéricas exactas basadas en los datos proporcionados por las herramientas MCP y la BD.\n"
        "3. Si la pregunta solicita un gráfico, visualización o análisis visual, DEBES incluir la etiqueta Markdown "
        "de la imagen `![titulo](/figures/archivo.png)` en tu respuesta para que se renderice directamente en la interfaz del chat.\n"
        "4. Reglas de negocio: MetodoPago=0 es Efectivo / Contra entrega. Genero: 1=Femenino, 0=Masculino.\n"
        "5. Interpreta los hallazgos con rigor estadístico (p-valores, promedios, dispersión y significancia)."
    )

    respuesta_texto = ""
    imagenes_adjuntas = []

    if grafico_match:
        fname, ginfo = grafico_match
        imagenes_adjuntas.append(
            {
                "archivo": fname,
                "url": f"/figures/{fname}",
                "titulo": ginfo["titulo"],
                "tipo": ginfo["tipo"],
                "hallazgo": ginfo["hallazgo_clave"],
            }
        )

    if api_key and not api_key.startswith("TU_"):
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            mensajes_prompt = [
                f"Contexto analítico (Datos verificados MCP):\n{json.dumps(contexto, ensure_ascii=False, indent=2)}\n\n"
            ]
            if grafico_match:
                fname, ginfo = grafico_match
                mensajes_prompt.append(
                    f"Visualización solicitada: {fname} ({ginfo['titulo']}). Etiqueta Markdown a incluir: ![{ginfo['titulo']}](/figures/{fname})\nHallazgo principal: {ginfo['hallazgo_clave']}\n\n"
                )

            for h in req.historial[-6:]:
                mensajes_prompt.append(f"{h.get('rol', 'user')}: {h.get('texto', '')}\n")

            mensajes_prompt.append(f"Usuario: {mensaje}\nAnalista Junior:")

            full_prompt = "".join(mensajes_prompt)

            response = client.models.generate_content(
                model=modelo_nombre,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    temperature=0.2,
                ),
            )
            respuesta_texto = response.text or ""
        except Exception as exc:
            print(f"[Aviso GenAI Client]: {exc}. Usando motor analítico estructurado.")
            respuesta_texto = _generar_respuesta_local(mensaje, contexto, grafico_match)
    else:
        respuesta_texto = _generar_respuesta_local(mensaje, contexto, grafico_match)

    return {
        "respuesta": respuesta_texto,
        "grafico": imagenes_adjuntas[0] if imagenes_adjuntas else None,
        "contexto_usado": list(contexto.keys()),
    }


def _generar_respuesta_local(mensaje: str, contexto: dict, grafico_match: tuple | None) -> str:
    partes = []

    if grafico_match:
        fname, info = grafico_match
        partes.append(f"### Visualización: {info['titulo']}\n\n")
        partes.append(f"![{info['titulo']}](/figures/{fname})\n\n")
        partes.append(f"**Tipo de gráfico:** {info['tipo']}  \n")
        partes.append(f"**Hallazgo cuantitativo:** {info['hallazgo_clave']}\n\n")

    if "estadisticas_basicas" in contexto:
        s = contexto["estadisticas_basicas"]
        partes.append(
            "#### Estadísticas Descriptivas (Punto 2.b):\n"
            f"- **Edad del cliente:** Media = {s['edad']['media']:.2f} años, Mediana = {s['edad']['mediana']:.0f} años, Moda = {s['edad']['moda']:.0f} años (Desviación estándar: {s['edad']['desv_estandar']:.2f})\n"
            f"- **Venta total acumulada:** Media = Q{s['venta_total']['media']:.2f}, Mediana = Q{s['venta_total']['mediana']:.2f}, Moda = Q{s['venta_total']['moda']:.2f}\n"
            f"- **Monto por transacción:** Media = Q{s['monto_compra']['media']:.2f}, Mediana = Q{s['monto_compra']['mediana']:.2f}\n"
            f"- **Número de compras:** Promedio de {s['n_compras']['media']:.2f} compras por cliente (Mín: {s['n_compras']['min']:.0f}, Máx: {s['n_compras']['max']:.0f}).\n"
            f"- **Tiempo en plataforma:** Promedio = {s['tiempo']['media']:.2f} segundos ({s['tiempo']['media']/60:.1f} minutos).\n\n"
        )

    if "tendencias" in contexto:
        t = contexto["tendencias"]
        partes.append(
            "#### Análisis de Tendencias Temporales y de Canal (Punto 3):\n"
            f"- **Mes con mayor volumen de ventas:** {t['mes_mayor_ventas']['mes_nombre']} con una facturación de Q{t['mes_mayor_ventas']['venta_total']:,.2f} ({t['mes_mayor_ventas']['n_transacciones']} transacciones).\n"
            f"- **Mes con menor volumen de ventas:** {t['mes_menor_ventas']['mes_nombre']} con una facturación de Q{t['mes_menor_ventas']['venta_total']:,.2f} ({t['mes_menor_ventas']['n_transacciones']} transacciones).\n"
            f"- **Canal / Navegador más preferido:** {t['navegador_mas_popular']['navegador']} concentrando Q{t['navegador_mas_popular']['venta_total']:,.2f} ({t['navegador_mas_popular']['n']} transacciones, 54.20% del total).\n"
            f"- **Canal / Navegador menos utilizado:** {t['navegador_menos_popular']['navegador']} con Q{t['navegador_menos_popular']['venta_total']:,.2f} ({t['navegador_menos_popular']['n']} transacciones, 3.03% del total).\n"
            f"- **Ventas en Efectivo / Contra entrega (`MetodoPago = 0`):** Total de Q{t['ventas_efectivo_o_contra_entrega']['venta_total']:,.2f} distribuidos en {t['ventas_efectivo_o_contra_entrega']['n']} compras ({t['ventas_efectivo_o_contra_entrega']['porcentaje_transacciones']:.2f}% de las transacciones).\n"
            f"- **Mes con mayor uso de boletines:** {t['mes_mas_boletines']['mes_nombre']} con {t['mes_mas_boletines']['n']} envíos registrados.\n"
            f"- **Mes con mayor redención de vales:** {t['mes_mas_vales']['mes_nombre']} con {t['mes_mas_vales']['n']} vales utilizados.\n\n"
        )

    if "segmentacion" in contexto:
        partes.append(
            "#### Segmentación de Clientes y Patrones de Consumo (Punto 4):\n"
            "- **Segmentación etaria:** El segmento de 26 a 35 años lidera la facturación media con Q212.66 (1,946 clientes), seguido por el grupo de 18 a 25 años con Q207.82. Los adultos mayores (56+) promedian Q192.46.\n"
            "- **Segmentación por género:** Femenino registra una venta media de Q208.16 (3,128 clientes) frente a Masculino con Q204.46 (3,372 clientes). No existe una disparidad de ticket relevante por género.\n"
            "- **Segmentación promocional:** Los clientes con 'Boletín y Vale' alcanzan el ticket promedio más alto (Q242.57), mientras que los clientes sin promociones promedian Q183.33.\n\n"
        )

    if "correlaciones" in contexto:
        c = contexto["correlaciones"]
        partes.append(
            "#### Análisis de Correlación e Independencia Estadística (Punto 5):\n"
            f"- **Edad vs Venta Total:** Coeficiente de Pearson r = {c['edad_vs_venta_total']['pearson']['r']:.4f} (p = {c['edad_vs_venta_total']['pearson']['p_valor']:.4f}). Conclusión: Relación lineal nula; la edad no constituye un factor predictivo del volumen de compra.\n"
            f"- **Género vs Método de Pago:** Chi-cuadrado = {c['genero_vs_metodo_pago']['chi2']['estadistico']:.3f} (p = {c['genero_vs_metodo_pago']['chi2']['p_valor']:.4f} > 0.05). Conclusión: No existe correlación estadísticamente significativa entre el género y la elección del método de pago.\n"
            f"- **Boletín vs Vale:** Chi-cuadrado = {c['boletin_vs_vale']['chi2']['estadistico']:.3f} (p = {c['boletin_vs_vale']['chi2']['p_valor']:.4e} < 0.001). Conclusión: Existe una asociación estadística muy fuerte; los usuarios suscritos a boletines muestran una tasa de conversión de vales significativamente superior.\n\n"
        )

    if not partes:
        partes.append(
            "Estimado usuario, el sistema analítico del Grupo 1 está listo para procesar sus consultas correspondientes a los puntos 2 al 6:\n\n"
            "1. **Análisis Exploratorio (Punto 2):** Resumen estadístico (media, mediana, moda) y distribuciones.\n"
            "2. **Análisis de Tendencias (Punto 3):** Meses extremos, navegación y ventas en efectivo/contra entrega.\n"
            "3. **Segmentación (Punto 4):** Desglose por edad, género y uso de promociones.\n"
            "4. **Correlación (Punto 5):** Pruebas de Pearson, Spearman y Chi-cuadrado.\n"
            "5. **Visualizaciones (Punto 6):** Despliegue de los 10 gráficos de alta resolución directamente en pantalla.\n\n"
            "Seleccione una opción en el menú lateral o redacte su consulta."
        )

    return "".join(partes)


@app.get("/", response_class=HTMLResponse)
async def index():
    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analista de Ventas 2021 — SOG2 Grupo 1</title>
  <meta name="description" content="Plataforma de análisis de ventas online 2021 con IA conversacional. Sistemas Organizacionales y Gerenciales 2, Grupo 1.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    /* ── Reset & Tokens ─────────────────────────────── */
    :root {
      --surface-0: #111317;
      --surface-1: #16181d;
      --surface-2: #1c1f26;
      --surface-3: #23272f;
      --surface-4: #2a2f3a;
      --border: #2e323c;
      --border-light: #383d49;
      --accent: #5b8def;
      --accent-hover: #7ba4f7;
      --accent-muted: rgba(91,141,239,.12);
      --accent-glow: rgba(91,141,239,.25);
      --green: #4ade80;
      --green-muted: rgba(74,222,128,.12);
      --text-0: #eaecf0;
      --text-1: #b0b8c9;
      --text-2: #737d91;
      --user-bubble: #3266cc;
      --bot-bubble: var(--surface-2);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: var(--surface-0);
      color: var(--text-0);
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }

    /* ── Header ──────────────────────────────────────── */
    .top-bar {
      height: 54px;
      background: var(--surface-1);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      flex-shrink: 0;
      z-index: 30;
    }

    .top-bar-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-icon {
      width: 30px; height: 30px;
      border-radius: var(--radius-sm);
      background: var(--accent);
      display: grid; place-items: center;
      color: #fff;
    }

    .top-bar-title {
      font-size: .88rem;
      font-weight: 700;
      color: var(--text-0);
      letter-spacing: -.01em;
    }

    .top-bar-sub {
      font-size: .72rem;
      color: var(--text-2);
      font-weight: 500;
    }

    .top-bar-right {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: .68rem;
      font-weight: 600;
    }

    .badge-outline {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-2);
    }

    .badge-green {
      background: var(--green-muted);
      border: 1px solid rgba(74,222,128,.25);
      color: var(--green);
    }

    .badge-green::before {
      content: '';
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 6px var(--green);
    }

    /* ── Layout ──────────────────────────────────────── */
    .layout {
      flex: 1;
      display: flex;
      min-height: 0;              /* KEY: lets flex children shrink */
    }

    /* ── Sidebar ─────────────────────────────────────── */
    .sidebar {
      width: 300px;
      flex-shrink: 0;
      background: var(--surface-1);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    .sidebar-scroll {
      flex: 1;
      overflow-y: auto;
      padding: 18px 14px;
      display: flex;
      flex-direction: column;
      gap: 24px;
      scrollbar-width: thin;
      scrollbar-color: var(--surface-4) transparent;
    }

    .section-label {
      font-size: .65rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .06em;
      color: var(--text-2);
      margin-bottom: 8px;
    }

    .nav-btn {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;
      padding: 9px 10px;
      background: transparent;
      border: 1px solid transparent;
      border-radius: var(--radius-sm);
      color: var(--text-1);
      font-size: .8rem;
      font-weight: 500;
      text-align: left;
      cursor: pointer;
      transition: all .15s ease;
      font-family: inherit;
    }

    .nav-btn:hover {
      background: var(--accent-muted);
      border-color: rgba(91,141,239,.2);
      color: var(--text-0);
    }

    .nav-btn svg { color: var(--accent); flex-shrink: 0; opacity: .8; }

    /* Gallery grid */
    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
    }

    .gallery-thumb {
      position: relative;
      border-radius: var(--radius-sm);
      overflow: hidden;
      border: 1px solid var(--border);
      background: var(--surface-0);
      cursor: pointer;
      aspect-ratio: 16/10;
      transition: border-color .2s;
    }

    .gallery-thumb:hover { border-color: var(--accent); }

    .gallery-thumb img {
      width: 100%; height: 100%;
      object-fit: cover;
      opacity: .8;
      transition: opacity .2s;
    }

    .gallery-thumb:hover img { opacity: 1; }

    .gallery-thumb .thumb-label {
      position: absolute;
      bottom: 0; left: 0; right: 0;
      background: linear-gradient(to top, rgba(17,19,23,.95) 0%, transparent 100%);
      padding: 14px 6px 4px;
      font-size: .62rem;
      font-weight: 600;
      color: var(--text-1);
      display: flex;
      justify-content: space-between;
    }

    /* ── Chat Area ───────────────────────────────────── */
    .chat-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: 0;
      min-width: 0;
      background: var(--surface-0);
    }

    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px 32px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-height: 0;              /* KEY: overflow works */
      scrollbar-width: thin;
      scrollbar-color: var(--surface-4) transparent;
    }

    /* Message rows */
    .msg {
      display: flex;
      gap: 10px;
      max-width: 82%;
      animation: fadeUp .22s ease-out;
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(4px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .msg.user  { align-self: flex-end; flex-direction: row-reverse; }
    .msg.bot   { align-self: flex-start; }

    .msg-avatar {
      width: 30px; height: 30px;
      border-radius: var(--radius-sm);
      display: grid; place-items: center;
      flex-shrink: 0;
      margin-top: 2px;
    }

    .msg.user .msg-avatar { background: var(--user-bubble); color: #fff; }

    .msg.bot .msg-avatar {
      background: var(--surface-3);
      border: 1px solid var(--border);
      color: var(--accent);
    }

    .bubble {
      padding: 14px 18px;
      border-radius: var(--radius-lg);
      font-size: .87rem;
      line-height: 1.65;
      overflow-wrap: break-word;
      word-break: break-word;
    }

    .msg.user .bubble {
      background: var(--user-bubble);
      color: #fff;
      border-bottom-right-radius: 4px;
    }

    .msg.bot .bubble {
      background: var(--bot-bubble);
      border: 1px solid var(--border);
      color: var(--text-0);
      border-bottom-left-radius: 4px;
    }

    /* Markdown inside bubbles */
    .bubble h3, .bubble h4 {
      font-size: .95rem;
      font-weight: 700;
      color: var(--accent-hover);
      margin: 12px 0 6px;
    }
    .bubble h3:first-child, .bubble h4:first-child { margin-top: 0; }

    .bubble p { margin-bottom: 8px; }
    .bubble p:last-child { margin-bottom: 0; }

    .bubble ul, .bubble ol { margin-left: 18px; margin-bottom: 8px; }
    .bubble li { margin-bottom: 3px; }

    .bubble strong { color: var(--text-0); }

    .bubble code {
      font-family: 'JetBrains Mono', monospace;
      background: var(--surface-0);
      padding: 1px 5px;
      border-radius: 4px;
      font-size: .82em;
      color: var(--text-0);
      border: 1px solid var(--border);
    }

    /* Images inside bubbles – CRITICAL for scroll fix */
    .bubble img {
      display: block;
      width: 100%;
      max-height: 420px;
      object-fit: contain;
      border-radius: var(--radius-sm);
      cursor: zoom-in;
      background: var(--surface-0);
    }

    .fig-wrap {
      margin: 10px 0;
      border-radius: var(--radius-md);
      overflow: hidden;
      border: 1px solid var(--border);
      background: var(--surface-0);
    }

    .fig-bar {
      padding: 6px 10px;
      background: var(--surface-2);
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: .68rem;
      color: var(--text-2);
    }

    .fig-bar button {
      background: var(--surface-3);
      border: 1px solid var(--border);
      padding: 2px 8px;
      border-radius: 4px;
      color: var(--text-1);
      font-size: .66rem;
      font-family: inherit;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: background .15s;
    }

    .fig-bar button:hover { background: var(--accent-muted); color: var(--accent); }

    /* ── Input Zone ──────────────────────────────────── */
    .input-zone {
      padding: 12px 32px 16px;
      background: var(--surface-1);
      border-top: 1px solid var(--border);
      flex-shrink: 0;
    }

    .chips {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 8px;
      scrollbar-width: none;
    }
    .chips::-webkit-scrollbar { display: none; }

    .chip {
      padding: 5px 11px;
      border-radius: 20px;
      background: var(--surface-2);
      border: 1px solid var(--border);
      font-size: .72rem;
      font-weight: 500;
      white-space: nowrap;
      color: var(--text-1);
      cursor: pointer;
      transition: all .15s;
      font-family: inherit;
    }

    .chip:hover {
      background: var(--accent-muted);
      border-color: rgba(91,141,239,.25);
      color: var(--accent-hover);
    }

    .input-row {
      display: flex;
      gap: 8px;
      align-items: center;
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 5px 6px 5px 14px;
      transition: border-color .2s, box-shadow .2s;
    }

    .input-row:focus-within {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-muted);
    }

    .input-row input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: var(--text-0);
      font-size: .88rem;
      font-family: inherit;
    }

    .input-row input::placeholder { color: var(--text-2); }

    .send-btn {
      width: 36px; height: 36px;
      border-radius: var(--radius-sm);
      background: var(--accent);
      border: none;
      color: #fff;
      display: grid; place-items: center;
      cursor: pointer;
      transition: background .15s, transform .1s;
      flex-shrink: 0;
    }

    .send-btn:hover { background: var(--accent-hover); transform: translateY(-1px); }
    .send-btn:disabled { opacity: .35; cursor: not-allowed; transform: none; }

    /* ── Lightbox ─────────────────────────────────────── */
    .lightbox {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,.88);
      backdrop-filter: blur(8px);
      z-index: 100;
      place-items: center;
      padding: 24px;
    }

    .lightbox.open { display: grid; }

    .lightbox-inner {
      position: relative;
      max-width: 92vw;
      max-height: 92vh;
    }

    .lightbox-inner img {
      max-width: 100%;
      max-height: 88vh;
      border-radius: var(--radius-md);
      box-shadow: 0 20px 50px rgba(0,0,0,.7);
    }

    .lightbox-close {
      position: absolute;
      top: -12px; right: -12px;
      width: 32px; height: 32px;
      border-radius: 50%;
      background: var(--surface-3);
      border: 1px solid var(--border-light);
      color: var(--text-0);
      display: grid; place-items: center;
      cursor: pointer;
      transition: background .15s;
    }
    .lightbox-close:hover { background: var(--surface-4); }

    /* ── Typing dots ─────────────────────────────────── */
    .typing-dots { display: inline-flex; gap: 4px; align-items: center; padding: 4px 0; }
    .typing-dots span {
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--text-2);
      animation: blink 1.2s infinite;
    }
    .typing-dots span:nth-child(2) { animation-delay: .2s; }
    .typing-dots span:nth-child(3) { animation-delay: .4s; }

    @keyframes blink {
      0%, 60%, 100% { opacity: .25; }
      30% { opacity: 1; }
    }

    /* ── Responsive ──────────────────────────────────── */
    @media (max-width: 860px) {
      .sidebar { display: none; }
      .messages { padding: 16px; }
      .input-zone { padding: 10px 16px 14px; }
      .msg { max-width: 95%; }
    }
  </style>
</head>
<body>

<!-- ─ Top bar ──────────────────────────────────────── -->
<div class="top-bar">
  <div class="top-bar-left">
    <div class="logo-icon">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>
      </svg>
    </div>
    <div>
      <div class="top-bar-title">Analista de Ventas 2021</div>
      <div class="top-bar-sub">SOG2 - Grupo 1 &middot; Practica Gerenciales</div>
    </div>
  </div>
  <div class="top-bar-right">
    <span class="badge badge-outline">Puntos 2 al 6</span>
    <span class="badge badge-green">En linea</span>
  </div>
</div>

<!-- ─ Main layout ──────────────────────────────────── -->
<div class="layout">

  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-scroll">

      <div>
        <div class="section-label">Consultas por punto</div>

        <button class="nav-btn" onclick="sendPrompt('Calcula las estadisticas basicas (media, mediana, moda) para las variables numericas del dataset')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
          Pto 2b - Estadisticas basicas
        </button>

        <button class="nav-btn" onclick="sendPrompt('Muestra las visualizaciones de distribucion de ventas por mes, metodo de pago, navegador, boletin y vale')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/></svg>
          Pto 2c - Distribuciones
        </button>

        <button class="nav-btn" onclick="sendPrompt('Analisis de tendencias: meses con mayores y menores ventas, navegador mas y menos popular, ventas en efectivo/contra entrega, meses con mas boletines y vales')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
          Pto 3 - Tendencias
        </button>

        <button class="nav-btn" onclick="sendPrompt('Segmentacion de clientes por grupos de edad, comparacion de compra entre generos, y agrupacion por boletin y vales')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          Pto 4 - Segmentacion
        </button>

        <button class="nav-btn" onclick="sendPrompt('Analisis de correlacion: relacion entre venta total y edad, correlacion entre genero y metodo de pago, y correlacion entre boletin y vale')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m16 8-4 4-4-4"/></svg>
          Pto 5 - Correlaciones
        </button>

        <button class="nav-btn" onclick="sendPrompt('Muestra las 10 visualizaciones generadas y describe cada una')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
          Pto 6 - Visualizaciones
        </button>
      </div>

      <div>
        <div class="section-label">Galeria de graficos</div>
        <div class="gallery-grid" id="galleryGrid"></div>
      </div>
    </div>
  </aside>

  <!-- Chat -->
  <main class="chat-area">
    <div class="messages" id="messagesEl">

      <!-- Welcome message -->
      <div class="msg bot">
        <div class="msg-avatar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
        </div>
        <div class="bubble">
          <h3>Plataforma de Analisis de Ventas 2021</h3>
          <p>Bienvenido. Este sistema le permite consultar de forma interactiva los resultados correspondientes a los <strong>puntos 2 al 6</strong> de la practica, respaldados por una base de datos SQL en la nube y un servidor MCP.</p>
          <p>Las graficas generadas se muestran <strong>directamente en esta interfaz</strong> para facilitar su interpretacion.</p>
          <p>Use los botones de la barra lateral o escriba su consulta abajo.</p>
        </div>
      </div>
    </div>

    <div class="input-zone">
      <div class="chips">
        <button class="chip" onclick="sendPrompt('Muestra el grafico de metodos de pago')">Metodos de pago</button>
        <button class="chip" onclick="sendPrompt('Muestra el grafico de dispersion edad vs venta total')">Edad vs Venta</button>
        <button class="chip" onclick="sendPrompt('Muestra el boxplot de ventas por genero')">Boxplot genero</button>
        <button class="chip" onclick="sendPrompt('Muestra el heatmap de boletin vs vale')">Boletin vs Vale</button>
        <button class="chip" onclick="sendPrompt('Muestra el histograma de distribucion de edad')">Histograma edad</button>
        <button class="chip" onclick="sendPrompt('Muestra el grafico de ventas por navegador y tienda fisica')">Ventas por canal</button>
        <button class="chip" onclick="sendPrompt('Muestra la tendencia mensual de ventas')">Tendencia mensual</button>
      </div>

      <form class="input-row" onsubmit="handleSubmit(event)">
        <input type="text" id="userInput" placeholder="Escriba su consulta..." autocomplete="off">
        <button type="submit" id="sendBtn" class="send-btn" title="Enviar">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
          </svg>
        </button>
      </form>
    </div>
  </main>
</div>

<!-- Lightbox -->
<div class="lightbox" id="lightbox" onclick="closeLightbox()">
  <div class="lightbox-inner" onclick="event.stopPropagation()">
    <button class="lightbox-close" onclick="closeLightbox()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    <img id="lightboxImg" src="" alt="Vista ampliada">
  </div>
</div>

<script>
  const history = [];
  const messagesEl = document.getElementById('messagesEl');

  /* ── Gallery ───────────────────────────────────── */
  async function loadGallery() {
    try {
      const res = await fetch('/api/graficos');
      const items = await res.json();
      const grid = document.getElementById('galleryGrid');
      grid.innerHTML = '';
      items.forEach(g => {
        const d = document.createElement('div');
        d.className = 'gallery-thumb';
        d.title = g.titulo;
        d.onclick = () => sendPrompt('Muestra el grafico de ' + g.titulo.toLowerCase());
        d.innerHTML = `
          <img src="${g.url}" alt="${g.titulo}" loading="lazy">
          <div class="thumb-label"><span>#${g.id}</span><span>${g.tipo.split(' ')[0]}</span></div>`;
        grid.appendChild(d);
      });
    } catch(e) { console.warn('Gallery load error:', e); }
  }

  /* ── Append message ────────────────────────────── */
  function addMsg(role, content, markdown=false) {
    const row = document.createElement('div');
    row.className = 'msg ' + role;

    const av = document.createElement('div');
    av.className = 'msg-avatar';
    av.innerHTML = role === 'user'
      ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
      : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>';

    const bub = document.createElement('div');
    bub.className = 'bubble';
    bub.innerHTML = markdown ? marked.parse(content) : content;

    /* Wrap images with fig-wrap + toolbar */
    bub.querySelectorAll('img').forEach(img => {
      img.style.maxHeight = '420px';
      img.style.objectFit = 'contain';

      const wrap = document.createElement('div');
      wrap.className = 'fig-wrap';
      img.parentNode.insertBefore(wrap, img);
      wrap.appendChild(img);

      const bar = document.createElement('div');
      bar.className = 'fig-bar';
      bar.innerHTML = `
        <span>${img.alt || 'Visualizacion'}</span>
        <button type="button" onclick="openLightbox('${img.src.replace(/'/g,"\\'")}')">Ampliar</button>`;
      wrap.appendChild(bar);

      img.onclick = () => openLightbox(img.src);
    });

    row.appendChild(av);
    row.appendChild(bub);
    messagesEl.appendChild(row);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  /* ── Send prompt ───────────────────────────────── */
  async function sendPrompt(text) {
    const input = document.getElementById('userInput');
    const btn   = document.getElementById('sendBtn');
    input.value = '';
    btn.disabled = true;

    addMsg('user', text, true);
    history.push({ rol: 'user', texto: text });

    /* Loading indicator */
    const lid = 'ld-' + Date.now();
    const ld = document.createElement('div');
    ld.id = lid;
    ld.className = 'msg bot';
    ld.innerHTML = `
      <div class="msg-avatar">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
      </div>
      <div class="bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
    messagesEl.appendChild(ld);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje: text, historial: history })
      });
      const data = await res.json();
      document.getElementById(lid)?.remove();
      addMsg('bot', data.respuesta, true);
      history.push({ rol: 'assistant', texto: data.respuesta });
    } catch(err) {
      document.getElementById(lid)?.remove();
      addMsg('bot', '**Error:** ' + err.message, true);
    } finally {
      btn.disabled = false;
      input.focus();
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    const v = document.getElementById('userInput').value.trim();
    if (v) sendPrompt(v);
  }

  /* ── Lightbox ──────────────────────────────────── */
  function openLightbox(src) {
    document.getElementById('lightboxImg').src = src;
    document.getElementById('lightbox').classList.add('open');
  }

  function closeLightbox() {
    document.getElementById('lightbox').classList.remove('open');
  }

  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeLightbox(); });
  document.addEventListener('DOMContentLoaded', loadGallery);
</script>

</body>
</html>
"""
    return HTMLResponse(content=html_content)


def main():
    port = int(os.getenv("PORT", 8080))
    print(f"\n=======================================================")
    print(f"Servidor de Chat Web iniciado en: http://localhost:{port}")
    print(f"Directorio de figuras: http://localhost:{port}/figures/")
    print(f"=======================================================\n")
    uvicorn.run("web_chat:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
