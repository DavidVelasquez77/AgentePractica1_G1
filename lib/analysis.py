from __future__ import annotations

from pathlib import Path

import pandas as pd

from lib.db import ANALYTICS_SQL, get_engine

AGE_BINS = [0, 25, 35, 45, 55, 200]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-55", "56+"]
MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def _load_from_csv_fallback() -> pd.DataFrame:
    from lib import ROOT
    csv_candidates = [
        ROOT / "data" / "raw" / "venta_online_c.csv",
        ROOT / "docs" / "venta_online_c.csv",
    ]
    csv_path = next((p for p in csv_candidates if p.exists()), None)
    if not csv_path:
        raise FileNotFoundError("No se encontró venta_online_c.csv para el fallback")

    raw = pd.read_csv(csv_path, sep=";")
    raw["FechaCompra"] = pd.to_datetime(raw["FechaCompra"], format="%d.%m.%y")
    genero_map = {0: "Masculino", 1: "Femenino"}
    pago_map = {0: "Efectivo", 1: "Tarjeta de Credito", 2: "Tarjeta de Debito"}
    nav_map = {
        0: "Tienda Fisica",
        1: "Navegador 1",
        2: "Navegador 2",
        3: "Navegador 3",
        4: "Navegador 4",
    }
    return pd.DataFrame(
        {
            "id_cliente": raw["Id_cliente"].astype(int),
            "edad": raw["Edad"].astype(int),
            "genero": raw["Genero"].map(genero_map),
            "venta_total": raw["Venta_total"].astype(float),
            "n_compras": raw["N_Compras"].astype(int),
            "fecha_compra": raw["FechaCompra"],
            "monto_compra": raw["MontoCompra"].astype(float),
            "metodo_pago": raw["MetodoPago"].map(pago_map),
            "tiempo": raw["Tiempo"].astype(int),
            "navegador": raw["Navegador"].map(nav_map),
            "boletin": raw["Boletin"].astype(bool),
            "vale": raw["Vale"].astype(bool),
            "mes": raw["FechaCompra"].dt.month,
            "anio_mes": raw["FechaCompra"].dt.strftime("%Y-%m"),
        }
    )


def load_analytics_frame() -> pd.DataFrame:
    try:
        engine = get_engine()
        df = pd.read_sql(ANALYTICS_SQL, engine)
    except Exception as exc:
        print(f"[Aviso] Conexión directa a Supabase no disponible ({exc}). Usando réplica local verificada.")
        df = _load_from_csv_fallback()

    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes_nombre"] = df["mes"].map(MESES)
    df["rango_edad"] = pd.cut(
        df["edad"], bins=AGE_BINS, labels=AGE_LABELS, right=True
    )
    df["boletin"] = df["boletin"].astype(bool)
    df["vale"] = df["vale"].astype(bool)
    return df


def _central(series: pd.Series) -> dict:
    mode = series.mode(dropna=True)
    return {
        "media": float(series.mean()),
        "mediana": float(series.median()),
        "moda": None if mode.empty else (float(mode.iloc[0]) if pd.api.types.is_numeric_dtype(series) else str(mode.iloc[0])),
        "desv_estandar": float(series.std(ddof=1)) if len(series) > 1 else 0.0,
        "min": float(series.min()) if pd.api.types.is_numeric_dtype(series) else None,
        "max": float(series.max()) if pd.api.types.is_numeric_dtype(series) else None,
        "n": int(series.dropna().shape[0]),
    }


def estadisticas_basicas(df: pd.DataFrame | None = None) -> dict:
    df = df if df is not None else load_analytics_frame()
    numericas = ["edad", "venta_total", "n_compras", "monto_compra", "tiempo"]
    return {col: _central(df[col]) for col in numericas}


def ventas_por_mes(df: pd.DataFrame | None = None) -> dict:
    df = df if df is not None else load_analytics_frame()
    g = (
        df.groupby(["mes", "mes_nombre"], as_index=False)
        .agg(
            venta_total=("monto_compra", "sum"),
            n_transacciones=("id_cliente", "count"),
            ticket_promedio=("monto_compra", "mean"),
        )
        .sort_values("mes")
    )
    records = g.to_dict(orient="records")
    for row in records:
        row["venta_total"] = float(row["venta_total"])
        row["ticket_promedio"] = float(row["ticket_promedio"])
        row["n_transacciones"] = int(row["n_transacciones"])
        row["mes"] = int(row["mes"])
    max_row = max(records, key=lambda r: r["venta_total"])
    min_row = min(records, key=lambda r: r["venta_total"])
    return {"por_mes": records, "mes_mayor": max_row, "mes_menor": min_row}


def distribucion_categorica(df: pd.DataFrame, col: str, value_col: str = "monto_compra") -> list[dict]:
    g = df.groupby(col, as_index=False).agg(
        n=("id_cliente", "count"),
        venta_total=(value_col, "sum"),
        ticket_promedio=(value_col, "mean"),
    )
    out = []
    for row in g.to_dict(orient="records"):
        out.append(
            {
                col: str(row[col]),
                "n": int(row["n"]),
                "venta_total": float(row["venta_total"]),
                "ticket_promedio": float(row["ticket_promedio"]),
            }
        )
    return sorted(out, key=lambda r: r["venta_total"], reverse=True)


def tendencias(df: pd.DataFrame | None = None) -> dict:
    df = df if df is not None else load_analytics_frame()
    meses = ventas_por_mes(df)
    nav = distribucion_categorica(df, "navegador")
    efectivo = df[df["metodo_pago"] == "Efectivo"]
    boletin_mes = (
        df[df["boletin"]]
        .groupby(["mes", "mes_nombre"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
        .sort_values("n", ascending=False)
    )
    vale_mes = (
        df[df["vale"]]
        .groupby(["mes", "mes_nombre"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
        .sort_values("n", ascending=False)
    )
    return {
        "mes_mayor_ventas": meses["mes_mayor"],
        "mes_menor_ventas": meses["mes_menor"],
        "navegador_mas_popular": nav[0] if nav else None,
        "navegador_menos_popular": nav[-1] if nav else None,
        "navegadores": nav,
        "ventas_efectivo_o_contra_entrega": {
            "nota": (
                "Auxiliar (13-ago-2026): MetodoPago=0 cuenta como Efectivo y como "
                "contra entrega. Tarjeta de credito o debito NO es contra entrega."
            ),
            "n": int(len(efectivo)),
            "venta_total": float(efectivo["monto_compra"].sum()),
            "porcentaje_transacciones": float(len(efectivo) / len(df) * 100) if len(df) else 0,
        },
        "mes_mas_boletines": boletin_mes.iloc[0].to_dict() if not boletin_mes.empty else None,
        "mes_mas_vales": vale_mes.iloc[0].to_dict() if not vale_mes.empty else None,
        "boletines_por_mes": boletin_mes.to_dict(orient="records"),
        "vales_por_mes": vale_mes.to_dict(orient="records"),
    }


def segmentacion(df: pd.DataFrame | None = None) -> dict:
    df = df if df is not None else load_analytics_frame()
    edad = (
        df.groupby("rango_edad", observed=True)
        .agg(
            n=("id_cliente", "count"),
            venta_promedio=("venta_total", "mean"),
            monto_promedio=("monto_compra", "mean"),
            compras_promedio=("n_compras", "mean"),
        )
        .reset_index()
    )
    genero = (
        df.groupby("genero")
        .agg(
            n=("id_cliente", "count"),
            venta_promedio=("venta_total", "mean"),
            monto_promedio=("monto_compra", "mean"),
            compras_promedio=("n_compras", "mean"),
            pct_boletin=("boletin", "mean"),
            pct_vale=("vale", "mean"),
        )
        .reset_index()
    )
    promo = (
        df.assign(
            segmento_promo=df.apply(
                lambda r: (
                    "Boletin y vale"
                    if r["boletin"] and r["vale"]
                    else "Solo boletin"
                    if r["boletin"]
                    else "Solo vale"
                    if r["vale"]
                    else "Sin promocion"
                ),
                axis=1,
            )
        )
        .groupby("segmento_promo")
        .agg(
            n=("id_cliente", "count"),
            venta_promedio=("venta_total", "mean"),
            monto_promedio=("monto_compra", "mean"),
        )
        .reset_index()
    )

    def _clean(frame: pd.DataFrame) -> list[dict]:
        rows = []
        for row in frame.to_dict(orient="records"):
            clean = {}
            for k, v in row.items():
                if pd.isna(v):
                    clean[k] = None
                elif hasattr(v, "item"):
                    clean[k] = v.item()
                else:
                    clean[k] = v if not isinstance(v, float) else float(v)
            rows.append(clean)
        return rows

    return {
        "por_edad": _clean(edad),
        "por_genero": _clean(genero),
        "por_boletin_vale": _clean(promo),
    }


def correlaciones(df: pd.DataFrame | None = None) -> dict:
    from scipy import stats

    df = df if df is not None else load_analytics_frame()
    pearson = stats.pearsonr(df["edad"], df["venta_total"])
    spearman = stats.spearmanr(df["edad"], df["venta_total"])
    tabla_genero_pago = pd.crosstab(df["genero"], df["metodo_pago"])
    chi_pago = stats.chi2_contingency(tabla_genero_pago)
    tabla_bv = pd.crosstab(df["boletin"], df["vale"])
    chi_bv = stats.chi2_contingency(tabla_bv)

    def _corr(result) -> dict:
        stat, p = result.statistic, result.pvalue
        return {"estadistico": float(stat), "p_valor": float(p)}

    return {
        "edad_vs_venta_total": {
            "pearson": {"r": float(pearson.statistic), "p_valor": float(pearson.pvalue)},
            "spearman": {"rho": float(spearman.statistic), "p_valor": float(spearman.pvalue)},
            "interpretacion": (
                "Relacion lineal debil o nula"
                if abs(pearson.statistic) < 0.3
                else "Relacion lineal moderada"
                if abs(pearson.statistic) < 0.7
                else "Relacion lineal fuerte"
            ),
        },
        "genero_vs_metodo_pago": {
            "chi2": _corr(chi_pago),
            "tabla": tabla_genero_pago.to_dict(),
            "significativo_0_05": bool(chi_pago.pvalue < 0.05),
        },
        "boletin_vs_vale": {
            "chi2": _corr(chi_bv),
            "tabla": {
                "boletin_false_vale_false": int(tabla_bv.loc[False, False]) if False in tabla_bv.index and False in tabla_bv.columns else 0,
                "boletin_false_vale_true": int(tabla_bv.loc[False, True]) if False in tabla_bv.index and True in tabla_bv.columns else 0,
                "boletin_true_vale_false": int(tabla_bv.loc[True, False]) if True in tabla_bv.index and False in tabla_bv.columns else 0,
                "boletin_true_vale_true": int(tabla_bv.loc[True, True]) if True in tabla_bv.index and True in tabla_bv.columns else 0,
            },
            "significativo_0_05": bool(chi_bv.pvalue < 0.05),
        },
    }


def save_json(payload: dict, path: Path) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
