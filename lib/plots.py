from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from lib import ROOT
from lib.analysis import load_analytics_frame

sns.set_theme(style="whitegrid", context="talk")
FIG_DIR = ROOT / "outputs" / "figures"


def _save(fig: plt.Figure, name: str) -> str:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def generate_all_figures(df: pd.DataFrame | None = None) -> list[str]:
    df = df if df is not None else load_analytics_frame()
    paths: list[str] = []

    monthly = (
        df.groupby(["mes", "mes_nombre"], as_index=False)["monto_compra"]
        .sum()
        .sort_values("mes")
    )
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(data=monthly, x="mes_nombre", y="monto_compra", ax=ax, color="#1f4e79")
    ax.set_title("Ventas por mes (2021)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Monto de compra")
    ax.tick_params(axis="x", rotation=35)
    paths.append(_save(fig, "01_barras_ventas_mes.png"))

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly["mes_nombre"], monthly["monto_compra"], marker="o", color="#c45911")
    ax.set_title("Tendencia mensual de ventas")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Monto de compra")
    ax.tick_params(axis="x", rotation=35)
    paths.append(_save(fig, "02_lineas_tendencia_mes.png"))

    pago = df.groupby("metodo_pago", as_index=False)["monto_compra"].sum()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(pago["monto_compra"], labels=pago["metodo_pago"], autopct="%1.1f%%", startangle=90)
    ax.set_title("Participacion de ventas por metodo de pago")
    paths.append(_save(fig, "03_pastel_metodo_pago.png"))

    fig, ax = plt.subplots(figsize=(8, 6))
    sample = df.sample(n=min(len(df), 2000), random_state=42)
    sns.scatterplot(data=sample, x="edad", y="venta_total", hue="genero", ax=ax, alpha=0.55)
    ax.set_title("Edad vs venta total del cliente")
    paths.append(_save(fig, "04_dispersion_edad_venta.png"))

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x="genero", y="venta_total", ax=ax)
    ax.set_title("Distribucion de venta total por genero")
    paths.append(_save(fig, "05_boxplot_venta_genero.png"))

    tabla = pd.crosstab(df["boletin"], df["vale"], normalize="all") * 100
    tabla.index = tabla.index.map(lambda v: "Boletin si" if v else "Boletin no")
    tabla.columns = tabla.columns.map(lambda v: "Vale si" if v else "Vale no")
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(tabla, annot=True, fmt=".1f", cmap="Blues", ax=ax)
    ax.set_title("Cruce porcentual boletin vs vale")
    paths.append(_save(fig, "06_heatmap_boletin_vale.png"))

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data=df, x="edad", bins=20, kde=True, ax=ax, color="#548235")
    ax.set_title("Histograma de edad de clientes")
    paths.append(_save(fig, "07_histograma_edad.png"))

    nav = df.groupby("navegador", as_index=False)["monto_compra"].sum()
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=nav, x="navegador", y="monto_compra", ax=ax, color="#7030a0")
    ax.set_title("Ventas por navegador / canal")
    ax.tick_params(axis="x", rotation=20)
    paths.append(_save(fig, "08_barras_navegador.png"))

    return paths
