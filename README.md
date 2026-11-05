# AgentePractica1_G1

Practica SOG2: analista junior, base relacional en Supabase (nube), Python, Google ADK + MCP Server, modelo Gemini configurable mediante `GEMINI_MODEL`.

Nombre del repositorio publico (indicacion del auxiliar): `AgentePractica1_G1`. El PDF debe incluir el link de GitHub.

Repositorio: [AgentePractica1_G1](https://github.com/DavidVelasquez77/AgentePractica1_G1)

## Integrantes - Grupo 1

| Integrantes | Carnet |
| :--- | :--- |
| JOSUÉ DAVID VELÁSQUEZ IXCHOP | 202307705 |
| ENNER ESAÍ MENDIZABAL CASTRO | 202302220 |
| GAHEL ALEJANDRO HERRERA JUMÉNEZ | 202307629 |
| JOSÉ EMILIO MORALES CASTILLO | 202300636 |
| BRANDON ANTONIO MARROQUIN PÉREZ | 202300813 |

## Requisitos

- Python 3.10+
- Cuenta Supabase (proyecto cloud: sog2-ventas-2021)
- GOOGLE_API_KEY de Google AI Studio

## Setup (compañeros)

Clonar el repositorio y entrar en su raíz antes de instalar:

```bash
git clone https://github.com/DavidVelasquez77/AgentePractica1_G1.git
cd AgentePractica1_G1
python -m venv .venv
```

En PowerShell se puede usar el intérprete del entorno sin activar scripts:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

En Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Completar `.env` con un proyecto de pruebas. En PowerShell, sustituir `python` por `.\.venv\Scripts\python.exe` en los comandos posteriores si el entorno no está activado.

Pide las keys reales por un canal privado, nunca por GitHub.

Variables: DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, GOOGLE_API_KEY, GEMINI_MODEL.

La plantilla y el código incluyen un identificador predeterminado en `GEMINI_MODEL`. Confirmar que el modelo elegido esté habilitado en la cuenta del proveedor y ajustar la variable si hace falta; este README no garantiza su disponibilidad.

## Preparar la base de datos

Revisar [el esquema](db/schema.dbml) y la migración SQL en `supabase/migrations/` antes de ejecutarla en el proyecto Supabase de pruebas. Configurar `DATABASE_URL` y las claves de `.env` para ese mismo proyecto. El ETL carga datos en la base y los chats pueden hacer llamadas a Google: no son verificaciones sin efectos externos.

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

## Chat de IA (Puntos 2 al 6)

El enunciado y las aclaraciones del auxiliar en el foro solicitan que el Chat pueda entregar los resultados de los puntos 2 al 6 y **mostrar directamente las imágenes en la interfaz**:

### Opción A: Interfaz Web Interactiva con Renderizado de Gráficos (Recomendada)

```bash
python web_chat.py
```
Abre http://localhost:8080 en tu navegador. Incluye:
- Renderizado directo de imágenes con lightbox/zoom.
- Botones de acceso rápido para los puntos 2 al 6 (Estadísticas, Tendencias, Segmentación, Correlación, Gráficos).
- Conexión al motor de Gemini y MCP Server.

### Opción B: Google ADK Web (Interfaz Estándar)

```bash
adk web --port 8000
```
Abre http://localhost:8000 y solicita lo que deseas

## Diagrama ER

Pega db/schema.dbml en https://dbdiagram.io y exporta PNG/PDF para el informe.

## Seguridad

- No subas .env (esta en .gitignore).
- service_role y DATABASE_URL solo en scripts de servidor.
- Las tablas tienen RLS; el analisis usa la conexion Postgres.
