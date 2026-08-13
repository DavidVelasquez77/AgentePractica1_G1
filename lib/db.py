from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Falta DATABASE_URL en .env. Copia .env.example y pide las keys al compañero."
        )
    return url


def get_engine() -> Engine:
    url = get_database_url()
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(url, pool_pre_ping=True)


ANALYTICS_SQL = """
SELECT
    c.id_cliente,
    c.edad,
    g.nombre AS genero,
    c.venta_total,
    c.n_compras,
    p.fecha_compra,
    p.monto_compra,
    m.nombre AS metodo_pago,
    p.tiempo,
    n.nombre AS navegador,
    p.boletin,
    p.vale,
    EXTRACT(MONTH FROM p.fecha_compra)::int AS mes,
    TO_CHAR(p.fecha_compra, 'YYYY-MM') AS anio_mes
FROM compras p
JOIN clientes c ON c.id_cliente = p.id_cliente
JOIN catalogo_genero g ON g.codigo = c.genero_id
JOIN catalogo_metodo_pago m ON m.codigo = p.metodo_pago_id
JOIN catalogo_navegador n ON n.codigo = p.navegador_id
"""
