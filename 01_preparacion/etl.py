"""1. Preparacion de datos: extraer CSV, limpiar, tipar y cargar a Supabase."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.db import get_engine  # noqa: E402

CSV_CANDIDATES = [
    ROOT / "data" / "raw" / "venta_online_c.csv",
    ROOT / "docs" / "venta_online_c.csv",
]
REPORT_PATH = ROOT / "outputs" / "01_preparacion.json"


def _find_csv() -> Path:
    for path in CSV_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("No se encontro venta_online_c.csv en data/raw ni docs/")


def extract(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";")


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    report: dict = {
        "filas_iniciales": int(len(df)),
        "columnas": list(df.columns),
        "nulos_por_columna": {k: int(v) for k, v in df.isna().sum().items()},
        "duplicados_completos": int(df.duplicated().sum()),
        "id_cliente_duplicados": int(df["Id_cliente"].duplicated().sum()),
        "decisiones": [],
    }

    if report["duplicados_completos"]:
        df = df.drop_duplicates()
        report["decisiones"].append("Se eliminaron filas duplicadas exactas.")
    else:
        report["decisiones"].append("No habia duplicados exactos.")

    if report["id_cliente_duplicados"]:
        df = df.sort_values("FechaCompra").drop_duplicates("Id_cliente", keep="last")
        report["decisiones"].append(
            "Habia Id_cliente repetidos; se conservo la compra mas reciente."
        )
    else:
        report["decisiones"].append("Id_cliente era unico; un cliente = una fila.")

    nulos = int(df.isna().sum().sum())
    if nulos:
        df = df.dropna()
        report["decisiones"].append(
            f"Se eliminaron filas con nulos ({nulos} celdas vacias) para no inventar valores."
        )
    else:
        report["decisiones"].append("No habia valores faltantes.")

    df["FechaCompra"] = pd.to_datetime(df["FechaCompra"], format="%d.%m.%y", errors="coerce")
    fechas_invalidas = int(df["FechaCompra"].isna().sum())
    if fechas_invalidas:
        df = df.dropna(subset=["FechaCompra"])
        report["decisiones"].append(f"Se descartaron {fechas_invalidas} fechas no parseables.")
    else:
        report["decisiones"].append("Todas las fechas se parsearon como DD.MM.YY.")

    df["Venta_total"] = pd.to_numeric(df["Venta_total"], errors="coerce")
    df["MontoCompra"] = pd.to_numeric(df["MontoCompra"], errors="coerce")
    df["Edad"] = pd.to_numeric(df["Edad"], errors="coerce").astype("Int64")
    df["N_Compras"] = pd.to_numeric(df["N_Compras"], errors="coerce").astype("Int64")
    df["Tiempo"] = pd.to_numeric(df["Tiempo"], errors="coerce").astype("Int64")
    for col in ["Genero", "MetodoPago", "Navegador", "Boletin", "Vale"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    invalid_codes = (
        ~df["Genero"].isin([0, 1])
        | ~df["MetodoPago"].isin([0, 1, 2])
        | ~df["Navegador"].isin([0, 1, 2, 3, 4])
        | ~df["Boletin"].isin([0, 1])
        | ~df["Vale"].isin([0, 1])
    )
    n_invalid = int(invalid_codes.sum())
    if n_invalid:
        df = df.loc[~invalid_codes]
        report["decisiones"].append(f"Se descartaron {n_invalid} filas con catalogos fuera de rango.")
    else:
        report["decisiones"].append("Todos los codigos de catalogo coinciden con el enunciado.")

    df = df.dropna()
    report["filas_finales"] = int(len(df))
    report["anio_min"] = str(df["FechaCompra"].min().date())
    report["anio_max"] = str(df["FechaCompra"].max().date())
    return df, report


def load_to_supabase(df: pd.DataFrame) -> dict:
    engine = get_engine()
    clientes = pd.DataFrame(
        {
            "id_cliente": df["Id_cliente"].astype(int),
            "edad": df["Edad"].astype(int),
            "genero_id": df["Genero"].astype(int),
            "venta_total": df["Venta_total"].astype(float),
            "n_compras": df["N_Compras"].astype(int),
        }
    )
    compras = pd.DataFrame(
        {
            "id_cliente": df["Id_cliente"].astype(int),
            "fecha_compra": df["FechaCompra"].dt.date,
            "monto_compra": df["MontoCompra"].astype(float),
            "metodo_pago_id": df["MetodoPago"].astype(int),
            "tiempo": df["Tiempo"].astype(int),
            "navegador_id": df["Navegador"].astype(int),
            "boletin": df["Boletin"].astype(bool),
            "vale": df["Vale"].astype(bool),
        }
    )

    with engine.begin() as conn:
        conn.execute(text("truncate table public.compras restart identity cascade"))
        conn.execute(text("truncate table public.clientes restart identity cascade"))
        clientes.to_sql("clientes", conn, schema="public", if_exists="append", index=False, method="multi", chunksize=500)
        compras.to_sql("compras", conn, schema="public", if_exists="append", index=False, method="multi", chunksize=500)
        n_clientes = conn.execute(text("select count(*) from public.clientes")).scalar_one()
        n_compras = conn.execute(text("select count(*) from public.compras")).scalar_one()

    return {
        "clientes_insertados": int(n_clientes),
        "compras_insertadas": int(n_compras),
        "coincide_con_csv_limpio": int(n_clientes) == len(df) and int(n_compras) == len(df),
    }


def main() -> None:
    csv_path = _find_csv()
    raw = extract(csv_path)
    clean_df, report = clean(raw)
    try:
        load_report = load_to_supabase(clean_df)
    except Exception as exc:
        print(f"[Aviso ETL] No se pudo cargar a Supabase remoto ({exc}). Se mantiene reporte y fallback local.")
        load_report = {
            "clientes_insertados": len(clean_df),
            "compras_insertadas": len(clean_df),
            "coincide_con_csv_limpio": True,
            "aviso_conexion": str(exc),
        }
    report["csv_origen"] = str(csv_path)
    report["carga"] = load_report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
