import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

PRUEBAS = {
    "p1": ("prueba1-carga-sostenida_stats",     "Prueba 1 — Carga Sostenida"),
    "p2": ("prueba2-pico-carga_stats",           "Prueba 2 — Pico de Carga"),
    "p3": ("prueba3-cold-start_stats",           "Prueba 3 — Cold Start"),
    "p4": ("prueba4-procesamiento-eventos_stats","Prueba 4 — Pipeline de Eventos"),
    "p5": ("prueba5-resiliencia_stats",          "Prueba 5 — Resiliencia"),
    "p6": ("prueba6-escalado-horizontal_stats",  "Prueba 6 — Escalado Horizontal"),
}
POLITICAS = ["A","B","C","D"]
LABELS    = ["Política A\n(Baja latencia)","Política B\n(Eficiencia)",
             "Política C\n(Balanceada)","Política D\n(Alta disponib.)"]
COLORES   = ["#2E86AB","#E84855","#3BB273","#F4A261"]
BORDES    = ["#1a5f7a","#b5323d","#277a4e","#c47d3a"]
X_POS     = [1,2,3,4]
BOX_W     = 0.5
BG        = "#FAFAFA"
UPLOADS   = "/mnt/user-data/uploads"
OUTPUTS   = "/mnt/user-data/outputs"


def cargar(fname, pol):
    df  = pd.read_csv(f"{UPLOADS}/{fname}_{pol}.csv")
    row = df[df["Name"] == "Aggregated"].iloc[0]
    return {
        "min":  float(row["Min Response Time"]),
        "p50":  float(row["50%"]),
        "p75":  float(row["75%"]),
        "p99":  float(row["99%"]),
        "max":  float(row["100%"]),
    }


def separar_etiquetas(pares, ax, min_gap_pts=11):
    """Separa etiquetas que se solapan desplazándolas en píxeles de figura."""
    if not pares:
        return pares
    fig = ax.get_figure()
    h_fig = fig.get_size_inches()[1] * fig.dpi
    y0, y1 = ax.get_ylim()

    def to_px(v):
        log_v  = np.log10(max(v, 1e-6))
        log_y0 = np.log10(max(y0, 1e-6))
        log_y1 = np.log10(max(y1, 1e-6))
        frac = (log_v - log_y0) / (log_y1 - log_y0)
        return frac * h_fig

    def to_data(px):
        log_y0 = np.log10(max(y0, 1e-6))
        log_y1 = np.log10(max(y1, 1e-6))
        frac = px / h_fig
        return 10 ** (log_y0 + frac * (log_y1 - log_y0))

    pares = sorted(pares, key=lambda x: x[0])
    pos_px = [to_px(v) for v, *_ in pares]

    for _ in range(100):
        moved = False
        for i in range(1, len(pos_px)):
            gap = pos_px[i] - pos_px[i-1]
            if gap < min_gap_pts:
                push = (min_gap_pts - gap) / 2
                pos_px[i-1] -= push
                pos_px[i]   += push
                moved = True
        if not moved:
            break

    return [(pares[i][0], to_data(pos_px[i]), pares[i][1], pares[i][2], pares[i][3])
            for i in range(len(pares))]


def generar(key, fname, titulo):
    fig, ax = plt.subplots(figsize=(13, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    all_vals = []
    datos_pol = {}
    for pol in POLITICAS:
        datos_pol[pol] = cargar(fname, pol)
        all_vals += list(datos_pol[pol].values())

    # Escala log: fijar ylim antes de dibujar para que separar_etiquetas funcione
    ymin = min(all_vals) * 0.4
    ymax = max(all_vals) * 5
    ax.set_yscale("log")
    ax.set_ylim(max(0.5, ymin), ymax)

    for pol, pos, color, borde in zip(POLITICAS, X_POS, COLORES, BORDES):
        d  = datos_pol[pol]
        q1 = (d["min"] + d["p50"]) / 2

        # Garantizar altura mínima visible en log para la caja superior e inferior
        p75_draw = max(d["p75"], d["p50"] * 1.05)

        # --- Caja Q1 → p75 ---
        # Dibujar como dos rectángulos: mitad inferior (Q1→p50) y superior (p50→p75)
        # para que la línea de mediana siempre quede visible dentro
        for y_bot, y_top in [(q1, d["p50"]), (d["p50"], p75_draw)]:
            rect = mpatches.FancyBboxPatch(
                (pos - BOX_W/2, y_bot), BOX_W, y_top - y_bot,
                boxstyle="square,pad=0",
                linewidth=1.5, edgecolor=borde, facecolor=color, alpha=0.75, zorder=3,
            )
            ax.add_patch(rect)

        # Borde exterior único encima de los dos rectángulos
        ax.add_patch(mpatches.FancyBboxPatch(
            (pos - BOX_W/2, q1), BOX_W, p75_draw - q1,
            boxstyle="square,pad=0",
            linewidth=1.5, edgecolor=borde, facecolor="none", zorder=4,
        ))

        # Línea mediana (p50)
        ax.hlines(d["p50"], pos - BOX_W/2, pos + BOX_W/2,
                  colors="white", linewidth=2.5, zorder=5)

        # Bigote inferior: min → Q1
        ax.vlines(pos, d["min"], q1, colors=borde, linewidth=1.5, linestyle="--", zorder=2)
        ax.hlines(d["min"], pos - BOX_W/4, pos + BOX_W/4, colors=borde, linewidth=1.5, zorder=2)

        # Bigote superior: p75 → p99
        ax.vlines(pos, p75_draw, d["p99"], colors=borde, linewidth=1.5, linestyle="--", zorder=2)
        ax.hlines(d["p99"], pos - BOX_W/4, pos + BOX_W/4, colors=borde, linewidth=1.5, zorder=2)

        # Máximo como rombo outlier (solo si es diferente de p99)
        if d["max"] > d["p99"] * 1.05:
            ax.scatter(pos, d["max"], color=borde, s=60, zorder=6,
                       marker="D", edgecolors=borde)

        # Etiquetas con separación automática
        etqs = [
            (d["min"],  f"min: {d['min']:.1f} ms",  "#888888", 8.0),
            (d["p50"],  f"p50: {d['p50']:g} ms",    "#111111", 9.0),
            (d["p75"],  f"p75: {d['p75']:g} ms",    "#333333", 8.0),
            (d["p99"],  f"p99: {d['p99']:g} ms",    "#555555", 8.0),
        ]
        if d["max"] > d["p99"] * 1.05:
            etqs.append((d["max"], f"máx: {d['max']:g} ms", borde, 8.0))

        separadas = separar_etiquetas(etqs, ax, min_gap_pts=12)
        for val_real, y_label, txt, col, fs in separadas:
            fw = "bold" if "p50" in txt else "normal"
            # Línea guía solo si el desplazamiento es notable
            if abs(np.log10(max(y_label,0.1)) - np.log10(max(val_real,0.1))) > 0.05:
                ax.annotate("", xy=(pos + BOX_W/2 + 0.03, val_real),
                            xytext=(pos + BOX_W/2 + 0.07, y_label),
                            arrowprops=dict(arrowstyle="-", color="#CCCCCC", lw=0.7),
                            zorder=1)
            ax.text(pos + BOX_W/2 + 0.09, y_label, txt,
                    va="center", ha="left", fontsize=fs, color=col, fontweight=fw)

    ax.set_xticks(X_POS)
    ax.set_xticklabels(LABELS, fontsize=10.5, fontweight="bold", color="#222222")
    ax.set_xlim(0.4, 5.3)
    ax.set_ylabel("Latencia (ms) — escala logarítmica", fontsize=11, color="#444444", labelpad=10)
    ax.set_title(titulo + "\nDistribución de latencias por política",
                 fontsize=13, fontweight="bold", color="#1a1a1a", pad=16)
    ax.yaxis.grid(True, which="both", color="#DDDDDD", linewidth=0.8)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)

    leyenda = [
        mpatches.Patch(facecolor="#AAAAAA", alpha=0.75,
                       label="Caja: Q1* → p75  (* Q1 = (min+p50)/2, estimado)"),
        plt.Line2D([0],[0], color="white", linewidth=2.5, label="Línea blanca: mediana (p50)"),
        plt.Line2D([0],[0], color="#555555", linewidth=1.5, linestyle="--",
                   label="Bigotes: mín y p99"),
        plt.Line2D([0],[0], marker="D", color="w", markerfacecolor="#555555",
                   markersize=7, label="Rombo: máximo absoluto (cuando > p99)"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=8.5, framealpha=0.9,
              edgecolor="#CCCCCC")

    fig.text(0.5, 0.01,
             "Datos reales de Locust. Q1 estimado como (min+p50)/2 — Locust no exporta p25. "
             "p75, p99 y máximo son valores reales.",
             ha="center", fontsize=7.5, color="#777777", style="italic")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    ruta = f"{OUTPUTS}/boxplot_final_{key}.png"
    plt.savefig(ruta, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"OK {ruta}")


for key, (fname, titulo) in PRUEBAS.items():
    generar(key, fname, titulo)
print("Listo.")
