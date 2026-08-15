# AgentePractica1_G1

Practica SOG2: analista junior, base relacional en Supabase (nube), Python, Google ADK + MCP Server, modelo Gemini 3.5 Flash-Lite.

Nombre del repositorio publico (indicacion del auxiliar): `AgentePractica1_G1`. El PDF debe incluir el link de GitHub.

## Requisitos

- Python 3.10+
- Cuenta Supabase (proyecto cloud: sog2-ventas-2021)
- GOOGLE_API_KEY de Google AI Studio

## Setup (companeros)

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
```

Pide las keys reales por un canal privado, nunca por GitHub.

Variables: DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, GOOGLE_API_KEY, GEMINI_MODEL.

GEMINI_MODEL por defecto: gemini-3.5-flash-lite. Alternativa: gemini-3.5-flash.

## Pipeline

```bash
python 01_preparacion/etl.py
python 02_exploratorio/explorar.py
python 03_tendencias/tendencias.py
python 04_segmentacion/segmentar.py
python 05_correlacion/correlacion.py
python 06_visualizacion/visualizar.py
python run_all.py
```

CSV: docs/venta_online_c.csv (copia en data/raw/). Salidas: outputs/ y outputs/figures/.

## Chat de IA (puntos 2-6)

Desde la raiz del repo:

```bash
adk web --port 8000
```

Abre http://localhost:8000 y selecciona el agente `agent`.

## Diagrama ER

Pega db/schema.dbml en https://dbdiagram.io y exporta PNG/PDF para el informe.

## Seguridad

- No subas .env (esta en .gitignore).
- service_role y DATABASE_URL solo en scripts de servidor.
- Las tablas tienen RLS; el analisis usa la conexion Postgres.
