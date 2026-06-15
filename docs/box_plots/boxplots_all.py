import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

datos = {
    "p1": {
        "titulo": "Prueba 1 - Carga Sostenida",
        "A": [3,   2.5,  5,    15,    137],
        "B": [3,   5,    8,    2500,  3538],
        "C": [2,   5,    8,    12,    223],
        "D": [2,   5,    8,    10,    42],
    },
    "p2": {
        "titulo": "Prueba 2 - Pico de Carga",
        "A": [3,   5,    6,    18,    240],
        "B": [4,   6,    9,    200,   3504],
        "C": [4,   4,    8,    30,    456],
        "D": [4,   4,    7,    18,    567],
    },
    "p3": {
        "titulo": "Prueba 3 - Cold Start",
        "A": [16,  25,   270,  470,   750],
        "B": [94,  210,  710,  910,   3938],
        "C": [80,  100,  320,  410,   820],
        "D": [10,  19,   36,   200,   1100],
    },
    "p4": {
        "titulo": "Prueba 4 - Pipeline de Eventos",
        "A": [3,   5,    9,    26,    None],
        "B": [7,   7,    9,    16,    None],
        "C": [7,   7,    8,    25,    None],
        "D": [7,   7,    8,    20,    None],
    },
    "p5": {
        "titulo": "Prueba 5 - Resiliencia",
        "A": [3,   5,    8,    10,    82],
        "B": [5,   5,    8,    520,   2700],
        "C": [5,   5,    8,    11,    1700],
        "D": [5,   5,    8,    9,     79],
    },
    "p6": {
        "titulo": "Prueba 6 - Escalado Horizontal",
        "A": [3,   4,    5,    8,     130],
        "B": [4,   4,    7,    11,    380],
        "C": [4,   4,    7,    9,     272],
        "D": [4,   4,    7,    8,     160],
    },
}

archivos = {
    "p1": "boxplot_prueba1_carga_sostenida.png",
    "p2": "boxplot_prueba2_pico_carga.png",
    "p3": "boxplot_prueba3_cold_start.png",
    "p4": "boxplot_prueba4_pipeline_eventos.png",
    "p5": "boxplot_prueba5_resiliencia.png",
    "p6": "boxplot_prueba6_escalado_horizontal.png",
}

POLITICAS = ["A", "B", "C", "D"]
LABELS = [
    "Politica A\n(Baja latencia)",
    "Politica B\n(Eficiencia)",
    "Politica C\n(Balanceada)",
    "Politica D\n(Alta disponib.)",
]
COLORES = ["#2E86AB", "#E84855", "#3BB273", "#F4A261"]
BORDES  = ["#1a5f7a", "#b5323d", "#277a4e", "#c47d3a"]
BG      = "#FAFAFA"
X_POS   = [1, 2, 3, 4]
BOX_W   = 0.42

def generar_boxplot(key):
    d = datos[key]
    titulo = d["titulo"]
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    for pol, pos, color, borde in zip(POLITICAS, X_POS, COLORES, BORDES):
        vmin, p50, p95, p99, vmax = d[pol]

        box_bottom = min(p50, p95)
        box_top = max(p50, p95)

        caja = mpatches.FancyBboxPatch(
            (pos - BOX_W / 2, box_bottom), BOX_W, box_top - box_bottom,
            boxstyle="round,pad=0.01",
            linewidth=1.5, edgecolor=borde,
            facecolor=color, alpha=0.75, zorder=3,
        )
        ax.add_patch(caja)

        ax.hlines(p50, pos - BOX_W / 2, pos + BOX_W / 2,
                  colors="white", linewidth=2.5, zorder=4)

        whisker_bottom = min(vmin, box_bottom)
        whisker_top = max(p99, box_top)

        ax.vlines(pos, whisker_bottom, box_bottom, colors=borde, linewidth=1.5, linestyle="--", zorder=2)
        ax.hlines(vmin, pos - BOX_W / 4, pos + BOX_W / 4, colors=borde, linewidth=1.5, zorder=2)

        ax.vlines(pos, box_top, whisker_top, colors=borde, linewidth=1.5, linestyle="--", zorder=2)
        ax.hlines(p99, pos - BOX_W / 4, pos + BOX_W / 4, colors=borde, linewidth=1.5, zorder=2)

        if vmax is not None:
            ax.scatter(pos, vmax, color=borde, s=60, zorder=5,
                       marker="D", linewidths=1.2, edgecolors=borde)

        ox = 0.25
        ax.text(pos + ox, p50,  f"p50: {p50} ms",   va="center", ha="left", fontsize=8.5, color="#333333")
        ax.text(pos + ox, p95,  f"p95: {p95:g} ms", va="center", ha="left", fontsize=8.5, color="#333333")
        ax.text(pos + ox, p99,  f"p99: {p99:g} ms", va="center", ha="left", fontsize=8.5, color="#555555")
        if vmax is not None:
            ax.text(pos + ox, vmax, f"max: {vmax:g} ms", va="center", ha="left",
                    fontsize=8, color=borde, fontweight="bold")

    ax.set_yscale("log")
    ax.set_ylim(1, ax.get_ylim()[1] * 2)
    ax.set_xticks(X_POS)
    ax.set_xticklabels(LABELS, fontsize=10.5, fontweight="bold", color="#222222")
    ax.set_xlim(0.4, 4.9)
    ax.set_ylabel("Latencia (ms) - escala logaritmica", fontsize=11, color="#444444", labelpad=10)
    ax.set_title(titulo + "\nDistribucion de latencias por politica",
                 fontsize=13, fontweight="bold", color="#1a1a1a", pad=16)

    ax.yaxis.grid(True, which="both", color="#DDDDDD", linewidth=0.8, linestyle="-")
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)

    leyenda = [
        mpatches.Patch(facecolor="#AAAAAA", alpha=0.7, label="Caja: p50 -> p95"),
        plt.Line2D([0], [0], color="white", linewidth=2.5, markerfacecolor="#555", label="Linea blanca: p50 (mediana)"),
        plt.Line2D([0], [0], color="#555555", linewidth=1.5, linestyle="--", label="Bigotes: min -> p99"),
        plt.Line2D([0], [0], marker="D", color="w", markerfacecolor="#555555", markersize=7, label="Rombo: maximo absoluto"),
    ]
    ax.legend(handles=leyenda, loc="upper left", fontsize=8.5, framealpha=0.9, edgecolor="#CCCCCC")

    fig.text(0.5, 0.01,
             "Escala logaritmica. Fuente: metricas recogidas con Prometheus y Locust.",
             ha="center", fontsize=8, color="#777777", style="italic")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    ruta = f"/mnt/user-data/outputs/{archivos[key]}"
    plt.savefig(ruta, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  OK {ruta}")

print("Generando box plots...")
for key in datos:
    generar_boxplot(key)
print("Listo.")
