from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from scipy import stats

from lib import ROOT
from lib.analysis import AGE_BINS, AGE_LABELS, load_analytics_frame

FIG_DIR = ROOT / "outputs" / "figures"
PALETTE = ["#4F81BD", "#F79646", "#9BBB59", "#8064A2", "#4BACC6", "#C0504D"]
FUENTE = (
    "Fuente: Elaboración propia con base en los datos de ventas online 2021 "
    "cargados en Supabase (N = {n})."
)


def _fmt_int(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", " ")


def _fmt_money(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")


def _fmt_pct(part: float, total: float) -> str:
    if total == 0:
        return "0,0%"
    return f"{part / total * 100:.1f}%".replace(".", ",")


def _fmt_r(value: float) -> str:
    return f"{value:.3f}".replace(".", ",")


def _decorate(fig: plt.Figure, ax, title: str, subtitle: str, lectura: str, fuente: str) -> None:
    ax.set_title(title, fontweight="bold", fontsize=14, pad=22)
    fig.text(0.5, 0.955, subtitle, ha="center", va="top", style="italic", fontsize=9.5)
    ax.yaxis.grid(True, linestyle="--", color="#b0b0b0", alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.text(
        0.5,
        0.055,
        f"Lectura: {lectura}",
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        color="#1f4e79",
        wrap=True,
    )
    fig.text(0.07, 0.012, fuente, ha="left", fontsize=8)
    fig.subplots_adjust(top=0.84, bottom=0.20)


def _save(fig: plt.Figure, name: str) -> str:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


def _label_bars(ax, bars, labels: list[str], headroom: float = 1.28) -> None:
    ymax = max(bar.get_height() for bar in bars) if bars else 1
    current_ymin, current_ymax = ax.get_ylim()
    new_ymax = max(current_ymax, ymax * headroom) if current_ymax > 1.0 else ymax * headroom
    ax.set_ylim(0, new_ymax)
    for bar, label in zip(bars, labels):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            label,
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
        )


def _tabla_si_no(df: pd.DataFrame, col: str, no_label: str, yes_label: str) -> pd.DataFrame:
    tabla = (
        df.groupby(col, as_index=False)
        .agg(n=("id_cliente", "count"), monto=("monto_compra", "sum"))
    )
    tabla["etiqueta"] = tabla[col].map({False: no_label, True: yes_label})
    tabla["_ord"] = tabla[col].map({False: 0, True: 1})
    return tabla.sort_values("_ord")


def _dibujar_barras_si_no(
    ax,
    tabla: pd.DataFrame,
    flag_col: str,
    total_monto: float,
    xlabel: str,
) -> None:
    colors = ["#B4C7E7" if not bool(v) else "#4F81BD" for v in tabla[flag_col]]
    bars = ax.bar(tabla["etiqueta"], tabla["monto"], color=colors, width=0.55)
    labels = [
        f"{_fmt_money(row.monto)}\n{_fmt_int(row.n)} compras\n{_fmt_pct(row.monto, total_monto)}"
        for row in tabla.itertuples()
    ]
    _label_bars(ax, bars, labels, headroom=1.34)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Monto de compra (suma del grupo)")
    ax.legend(
        handles=[
            Patch(color="#4F81BD", label="Sí (código 1)"),
            Patch(color="#B4C7E7", label="No (código 0)"),
        ],
        loc="upper right",
        frameon=False,
        fontsize=8,
    )
    ax.yaxis.grid(True, linestyle="--", color="#b0b0b0", alpha=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _lectura_si_no(tabla: pd.DataFrame, flag_col: str, total_monto: float, nombre: str) -> str:
    con = tabla.loc[tabla[flag_col] == True].iloc[0]
    sin = tabla.loc[tabla[flag_col] == False].iloc[0]
    return (
        f"Con {nombre}: {_fmt_int(con.n)} compras y {_fmt_pct(con.monto, total_monto)} del monto. "
        f"Sin {nombre}: {_fmt_int(sin.n)} compras y {_fmt_pct(sin.monto, total_monto)}."
    )


def generate_all_figures(df: pd.DataFrame | None = None) -> list[str]:
    df = df if df is not None else load_analytics_frame()
    n = len(df)
    fuente = FUENTE.format(n=n)
    paths: list[str] = []

    monthly = (
        df.groupby(["mes", "mes_nombre"], as_index=False)["monto_compra"]
        .sum()
        .sort_values("mes")
    )
    total_monto = float(monthly["monto_compra"].sum())
    max_i = int(monthly["monto_compra"].idxmax())
    min_i = int(monthly["monto_compra"].idxmin())
    colors = []
    for idx in monthly.index:
        if idx == max_i:
            colors.append("#9BBB59")
        elif idx == min_i:
            colors.append("#C0504D")
        else:
            colors.append("#4F81BD")
    fig, ax = plt.subplots(figsize=(13.5, 6.8))
    bars = ax.bar(monthly["mes_nombre"], monthly["monto_compra"], color=colors, width=0.72)
    labels = [
        f"{_fmt_money(v)}\n({_fmt_pct(v, total_monto)})"
        for v in monthly["monto_compra"]
    ]
    _label_bars(ax, bars, labels, headroom=1.32)
    ax.set_xlabel("Mes de la compra")
    ax.set_ylabel("Monto de compra (suma del mes)")
    ax.tick_params(axis="x", rotation=28)
    ax.legend(
        handles=[
            Patch(color="#9BBB59", label=f"Mayor: {monthly.loc[max_i, 'mes_nombre']}"),
            Patch(color="#C0504D", label=f"Menor: {monthly.loc[min_i, 'mes_nombre']}"),
            Patch(color="#4F81BD", label="Resto de meses"),
        ],
        loc="upper right",
        frameon=False,
        fontsize=8,
    )
    _decorate(
        fig,
        ax,
        "Ventas por mes (2021)",
        f"Cada barra muestra el monto exacto y su porcentaje del año (N = {n})",
        f"Marzo es el mes más alto ({_fmt_money(monthly.loc[max_i, 'monto_compra'])}) y "
        f"noviembre el más bajo ({_fmt_money(monthly.loc[min_i, 'monto_compra'])}).",
        fuente,
    )
    paths.append(_save(fig, "01_barras_ventas_mes.png"))

    fig, ax = plt.subplots(figsize=(13.5, 6.8))
    xs = list(range(len(monthly)))
    ys = monthly["monto_compra"].to_numpy()
    max_pos = int(np.argmax(ys))
    min_pos = int(np.argmin(ys))
    ax.plot(xs, ys, color="#4F81BD", linewidth=2.2, zorder=2)
    ax.scatter(xs, ys, s=55, color="#4F81BD", zorder=3, label="Monto del mes")
    ax.scatter([max_pos], [ys[max_pos]], s=90, color="#9BBB59", zorder=4, label="Máximo")
    ax.scatter([min_pos], [ys[min_pos]], s=90, color="#C0504D", zorder=4, label="Mínimo")
    ax.set_xticks(xs, monthly["mes_nombre"], rotation=28)
    ax.set_ylim(float(ys.min()) * 0.90, float(ys.max()) * 1.14)
    for x, y in zip(xs, ys):
        ax.annotate(
            _fmt_money(y),
            (x, y),
            textcoords="offset points",
            xytext=(0, 9),
            ha="center",
            fontsize=7.5,
            fontweight="bold",
        )
    ax.set_xlabel("Mes de la compra")
    ax.set_ylabel("Monto de compra (suma del mes)")
    ax.legend(loc="upper right", frameon=False, fontsize=8)
    _decorate(
        fig,
        ax,
        "Tendencia mensual de ventas",
        f"Línea de tiempo con el valor exacto sobre cada mes (N = {n})",
        "El año no es plano: sube hacia marzo, baja en noviembre y se recupera en diciembre.",
        fuente,
    )
    paths.append(_save(fig, "02_lineas_tendencia_mes.png"))

    pago = (
        df.groupby("metodo_pago", as_index=False)
        .agg(n=("id_cliente", "count"), monto=("monto_compra", "sum"))
        .sort_values("monto", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(9.4, 7.2))
    wedges, _, autotexts = ax.pie(
        pago["monto"],
        colors=PALETTE[: len(pago)],
        startangle=90,
        autopct=lambda p: f"{p:.1f}%".replace(".", ","),
        pctdistance=0.62,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    legend = ax.legend(
        wedges,
        [
            f"{row.metodo_pago}\n{_fmt_money(row.monto)} ({_fmt_int(row.n)} tx)"
            for row in pago.itertuples()
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.02),
        frameon=False,
        fontsize=8.5,
        ncol=3,
        columnspacing=1.6,
        handletextpad=0.5,
    )
    legend.set_alignment("center")
    fig.suptitle("Participación de ventas por método de pago", fontweight="bold", fontsize=13, y=0.97)
    fig.text(
        0.5,
        0.915,
        f"Monto, transacciones y porcentaje. Efectivo = contra entrega (código 0). N = {n}",
        ha="center",
        style="italic",
        fontsize=9,
    )
    fig.text(0.5, 0.02, fuente, ha="center", fontsize=8)
    fig.subplots_adjust(top=0.86, bottom=0.20, left=0.12, right=0.88)
    paths.append(_save(fig, "03_pastel_metodo_pago.png"))

    pearson = stats.pearsonr(df["edad"], df["venta_total"])
    y_cut = float(df["venta_total"].quantile(0.98))
    fig, axes = plt.subplots(1, 2, figsize=(13.8, 6.6), gridspec_kw={"width_ratios": [1.25, 1]})
    hb = axes[0].hexbin(
        df["edad"],
        df["venta_total"].clip(upper=y_cut),
        gridsize=22,
        cmap="Blues",
        mincnt=1,
    )
    slope, intercept, r_val, p_val, _ = stats.linregress(df["edad"], df["venta_total"])
    x_line = np.array([df["edad"].min(), df["edad"].max()])
    axes[0].plot(x_line, intercept + slope * x_line, color="#C0504D", linewidth=2.4, label="Recta de tendencia")
    axes[0].set_ylim(0, y_cut * 1.05)
    axes[0].set_xlabel("Edad del cliente (años)")
    axes[0].set_ylabel("Venta total del cliente (eje recortado al 98 %)")
    axes[0].legend(loc="upper right", frameon=False, fontsize=8)
    fig.colorbar(hb, ax=axes[0], fraction=0.046, label="Cantidad de clientes en esa zona")
    axes[0].set_title("Dónde se concentran los clientes", fontsize=11, fontweight="bold")
    axes[0].yaxis.grid(True, linestyle="--", color="#b0b0b0", alpha=0.65)
    axes[0].spines["top"].set_visible(False)
    axes[0].spines["right"].set_visible(False)

    por_edad = (
        df.assign(rango=pd.cut(df["edad"], bins=AGE_BINS, labels=AGE_LABELS, right=True))
        .groupby("rango", observed=True)["venta_total"]
        .agg(media="mean", n="size")
        .reset_index()
    )
    bars = axes[1].bar(por_edad["rango"].astype(str), por_edad["media"], color=PALETTE[0], width=0.7)
    _label_bars(
        axes[1],
        bars,
        [f"{_fmt_money(m)}\nn={_fmt_int(c)}" for m, c in zip(por_edad["media"], por_edad["n"])],
        headroom=1.28,
    )
    axes[1].set_xlabel("Rango de edad")
    axes[1].set_ylabel("Venta total promedio")
    axes[1].set_title("Promedio por grupo de edad", fontsize=11, fontweight="bold")
    axes[1].yaxis.grid(True, linestyle="--", color="#b0b0b0", alpha=0.65)
    axes[1].spines["top"].set_visible(False)
    axes[1].spines["right"].set_visible(False)

    fig.suptitle("¿La edad explica la venta total? No.", fontweight="bold", fontsize=15, y=0.98)
    fig.text(
        0.5,
        0.915,
        f"Correlación de Pearson r = {_fmt_r(pearson.statistic)} (casi 0). p = {_fmt_r(pearson.pvalue)}. N = {n}",
        ha="center",
        style="italic",
        fontsize=9.5,
    )
    fig.text(
        0.5,
        0.045,
        "Lectura: la nube no sube ni baja con la edad (la raya roja es casi plana). "
        "Los promedios por grupo también son parecidos (192 a 213). La edad no sirve para predecir cuánto compra alguien.",
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="#1f4e79",
    )
    fig.text(0.07, 0.012, fuente, ha="left", fontsize=8)
    fig.subplots_adjust(top=0.84, bottom=0.18, wspace=0.28)
    paths.append(_save(fig, "04_dispersion_edad_venta.png"))

    order = ["Femenino", "Masculino"]
    fig, ax = plt.subplots(figsize=(10.2, 7.0))
    y_box = float(df["venta_total"].quantile(0.92))
    data_box = [df.loc[df["genero"] == g, "venta_total"].to_numpy() for g in order]
    bp = ax.boxplot(
        data_box,
        tick_labels=order,
        patch_artist=True,
        showfliers=False,
        widths=0.55,
        medianprops={"color": "black", "linewidth": 2},
        whiskerprops={"linewidth": 1.3},
    )
    for patch, color in zip(bp["boxes"], PALETTE[:2]):
        patch.set_facecolor(color)
        patch.set_alpha(0.9)
    ax.set_ylim(0, y_box * 1.08)
    rows = []
    for i, g in enumerate(order):
        serie = df.loc[df["genero"] == g, "venta_total"]
        q1, med, q3 = [float(serie.quantile(q)) for q in (0.25, 0.5, 0.75)]
        media = float(serie.mean())
        rows.append(
            f"{g}: n={_fmt_int(len(serie))}   mediana={_fmt_money(med)}   "
            f"media={_fmt_money(media)}   Q1={_fmt_money(q1)}   Q3={_fmt_money(q3)}"
        )
        ax.annotate(
            f"Mediana\n{_fmt_money(med)}",
            xy=(i + 1, med),
            xytext=(i + 1 + 0.38, med),
            fontsize=8,
            fontweight="bold",
            va="center",
            arrowprops={"arrowstyle": "->", "color": "#333", "lw": 0.8},
        )
    ax.set_xlabel("Género del cliente")
    ax.set_ylabel("Venta total (sin atípicos; eje hasta el percentil 92)")
    ax.legend(
        handles=[Patch(color=PALETTE[0], label="Femenino"), Patch(color=PALETTE[1], label="Masculino")],
        loc="upper right",
        frameon=False,
        fontsize=8,
    )
    fig.text(0.5, 0.14, "  |  ".join(rows), ha="center", fontsize=8)
    _decorate(
        fig,
        ax,
        "¿Compran distinto mujeres y hombres?",
        f"Cajas comparables (se ocultaron atípicos para ver el centro). N = {n}",
        "No: las medianas son casi iguales (137,60 vs 137,30). El género no cambia el ticket típico.",
        fuente,
    )
    fig.subplots_adjust(top=0.84, bottom=0.24)
    paths.append(_save(fig, "05_boxplot_venta_genero.png"))

    counts = pd.crosstab(df["boletin"], df["vale"])
    pct = pd.crosstab(df["boletin"], df["vale"], normalize="all") * 100
    titles = [
        ["Sin boletín y sin vale", "Sin boletín, con vale"],
        ["Con boletín, sin vale", "Con boletín y con vale"],
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.2))
    cell_colors = ["#4F81BD", "#B4C7E7", "#8FAADC", "#2E75B6"]
    coords = [(False, False), (False, True), (True, False), (True, True)]
    for ax, (i, j), (bi, vj), color in zip(axes.ravel(), [(0, 0), (0, 1), (1, 0), (1, 1)], coords, cell_colors):
        c = int(counts.loc[bi, vj])
        p = float(pct.loc[bi, vj])
        ax.set_facecolor(color)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("white")
            spine.set_linewidth(6)
        ax.text(0.5, 0.70, titles[i][j], ha="center", va="center", fontsize=11, fontweight="bold", color="white")
        ax.text(0.5, 0.42, _fmt_int(c), ha="center", va="center", fontsize=28, fontweight="bold", color="white")
        ax.text(0.5, 0.18, f"{p:.1f}% del total".replace(".", ","), ha="center", va="center", fontsize=12, color="white")
    fig.suptitle("¿Cuántos clientes usan boletín, vale, ambos o ninguno?", fontweight="bold", fontsize=15, y=0.98)
    fig.text(
        0.5,
        0.915,
        f"Cada recuadro es un grupo. El número grande es la cantidad de clientes. N = {n}",
        ha="center",
        style="italic",
        fontsize=9.5,
    )
    fig.text(
        0.5,
        0.045,
        "Lectura: casi la mitad (48,2 %) no usa promoción. El grupo de mayor valor de compra es el de boletín + vale (811 clientes, 12,5 %).",
        ha="center",
        fontsize=9,
        fontweight="bold",
        color="#1f4e79",
    )
    fig.text(0.07, 0.012, fuente, ha="left", fontsize=8)
    fig.subplots_adjust(top=0.86, bottom=0.12, hspace=0.08, wspace=0.08)
    paths.append(_save(fig, "06_heatmap_boletin_vale.png"))

    fig, ax = plt.subplots(figsize=(12.2, 6.8))
    bins = list(range(18, 82, 4))
    counts_h, edges, patches = ax.hist(df["edad"], bins=bins, color="#4BACC6", edgecolor="white")
    for patch, c, left, right in zip(patches, counts_h, edges[:-1], edges[1:]):
        if c <= 0:
            continue
        ax.text(
            (left + right) / 2,
            c,
            _fmt_int(c),
            ha="center",
            va="bottom",
            fontsize=7,
            fontweight="bold",
        )
    media = float(df["edad"].mean())
    mediana = float(df["edad"].median())
    moda = float(df["edad"].mode().iloc[0])
    ax.axvline(moda, color="#9BBB59", linestyle="--", linewidth=2, label=f"Moda = {moda:.0f} años (la más repetida)")
    ax.axvline(mediana, color="#F79646", linestyle="-.", linewidth=2, label=f"Mediana = {mediana:.0f} años (la del centro)")
    ax.axvline(media, color="#C0504D", linestyle=":", linewidth=2.2, label=f"Media = {media:.2f} años (promedio)")
    ax.set_xlabel("Edad del cliente (años), en intervalos de 4 años")
    ax.set_ylabel("Cantidad de clientes en ese intervalo")
    ax.legend(loc="upper right", frameon=False, fontsize=8)
    _decorate(
        fig,
        ax,
        "¿De qué edad son los clientes?",
        f"Cada barra dice cuántos clientes hay en ese rango de edad (N = {n})",
        f"Hay muchos clientes jóvenes: la edad que más se repite es 18. El cliente típico tiene {mediana:.0f} años.",
        fuente,
    )
    paths.append(_save(fig, "07_histograma_edad.png"))

    nav = (
        df.groupby("navegador", as_index=False)
        .agg(n=("id_cliente", "count"), monto=("monto_compra", "sum"))
        .sort_values("monto", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(12.2, 6.8))
    nav_colors = ["#4F81BD" if i == 0 else "#C0504D" if i == len(nav) - 1 else "#8FAADC" for i in range(len(nav))]
    bars = ax.bar(nav["navegador"], nav["monto"], color=nav_colors, width=0.62)
    labels = [
        f"{_fmt_money(row.monto)}\n{_fmt_int(row.n)} compras\n{_fmt_pct(row.monto, total_monto)}"
        for row in nav.itertuples()
    ]
    _label_bars(ax, bars, labels, headroom=1.36)
    ax.set_xlabel("Canal por el que se registró la compra")
    ax.set_ylabel("Monto de compra (suma del canal)")
    ax.legend(
        handles=[
            Patch(color="#4F81BD", label="Canal más usado"),
            Patch(color="#8FAADC", label="Canales intermedios"),
            Patch(color="#C0504D", label="Canal menos usado"),
        ],
        loc="upper right",
        frameon=False,
        fontsize=8,
    )
    _decorate(
        fig,
        ax,
        "¿Por qué canal compraron?",
        f"Monto, número de compras y porcentaje del año (N = {n})",
        f"Tienda física ya es el canal #1 ({_fmt_int(nav.iloc[0].n)} compras, {_fmt_pct(nav.iloc[0].monto, total_monto)}). "
        f"Navegador 4 es residual ({_fmt_int(nav.iloc[-1].n)} compras).",
        fuente,
    )
    paths.append(_save(fig, "08_barras_navegador.png"))

    boletin = _tabla_si_no(df, "boletin", "Sin boletín", "Con boletín")
    fig, ax = plt.subplots(figsize=(8.6, 6.4))
    _dibujar_barras_si_no(ax, boletin, "boletin", total_monto, "¿El cliente recibió boletín?")
    _decorate(
        fig,
        ax,
        "Ventas según uso de boletín",
        f"Distribución del monto de compra: con boletín frente a sin boletín (N = {n})",
        _lectura_si_no(boletin, "boletin", total_monto, "boletín"),
        fuente,
    )
    paths.append(_save(fig, "09_ventas_boletin.png"))

    vale = _tabla_si_no(df, "vale", "Sin vale", "Con vale")
    fig, ax = plt.subplots(figsize=(8.6, 6.4))
    _dibujar_barras_si_no(ax, vale, "vale", total_monto, "¿El cliente usó vale?")
    _decorate(
        fig,
        ax,
        "Ventas según uso de vale",
        f"Distribución del monto de compra: con vale frente a sin vale (N = {n})",
        _lectura_si_no(vale, "vale", total_monto, "vale"),
        fuente,
    )
    paths.append(_save(fig, "10_ventas_vale.png"))

    # 11. Tendencia mensual de boletines y vales (Punto 3.d)
    b_df = (
        df[df["boletin"]]
        .groupby(["mes", "mes_nombre"], as_index=False)
        .size()
        .rename(columns={"size": "n_boletin"})
    )
    v_df = (
        df[df["vale"]]
        .groupby(["mes", "mes_nombre"], as_index=False)
        .size()
        .rename(columns={"size": "n_vale"})
    )
    promo_mes = pd.merge(b_df, v_df, on=["mes", "mes_nombre"], how="outer").fillna(0).sort_values("mes")

    fig, ax = plt.subplots(figsize=(13.5, 7.0))
    x = np.arange(len(promo_mes))
    width = 0.38

    bars1 = ax.bar(x - width / 2, promo_mes["n_boletin"], width, label="Boletín (Suscritos)", color="#4F81BD")
    bars2 = ax.bar(x + width / 2, promo_mes["n_vale"], width, label="Vale (Redimidos)", color="#F79646")

    labels_b = [f"{_fmt_int(v)}" for v in promo_mes["n_boletin"]]
    labels_v = [f"{_fmt_int(v)}" for v in promo_mes["n_vale"]]

    _label_bars(ax, bars1, labels_b, headroom=1.28)
    _label_bars(ax, bars2, labels_v, headroom=1.28)

    max_b_row = promo_mes.loc[promo_mes["n_boletin"].idxmax()]
    max_v_row = promo_mes.loc[promo_mes["n_vale"].idxmax()]

    ax.set_xticks(x)
    ax.set_xticklabels(promo_mes["mes_nombre"], rotation=28)
    ax.set_xlabel("Mes del año (2021)")
    ax.set_ylabel("Cantidad de transacciones / clientes")
    ax.legend(
        handles=[
            Patch(color="#4F81BD", label=f"Boletín (Pico: {max_b_row['mes_nombre']} con {_fmt_int(max_b_row['n_boletin'])})"),
            Patch(color="#F79646", label=f"Vale (Pico: {max_v_row['mes_nombre']} con {_fmt_int(max_v_row['n_vale'])})"),
        ],
        loc="upper right",
        frameon=False,
        fontsize=8.5,
    )
    _decorate(
        fig,
        ax,
        "Uso mensual de boletines y vales (Punto 3.d — Tendencias)",
        f"Evolución comparativa mensual de recepción de boletines vs redención de vales (N = {n})",
        f"Mes con más boletines: {max_b_row['mes_nombre']} ({_fmt_int(max_b_row['n_boletin'])}) y Marzo (261). "
        f"Mes con más vales: {max_v_row['mes_nombre']} ({_fmt_int(max_v_row['n_vale'])}) y Diciembre (128). "
        "Los picos promocionales coinciden con los meses de mayor facturación global.",
        fuente,
    )
    paths.append(_save(fig, "11_tendencia_boletines_vales_mes.png"))

    return paths

