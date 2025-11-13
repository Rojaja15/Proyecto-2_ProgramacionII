from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px

# ================================
# Cargar datos
# ================================
df = pd.read_csv("Datos.csv")
df["Date"] = pd.to_datetime(df["Date"]).dt.date  # fechas sin hora

# ================================
# Paleta de colores corporativa
# ================================

colores_empresas = {
    # Tecnología
    "AAPL": "#1f77b4",
    "MSFT": "#BE8C00",
    "NVDA": "#76B900",
    "INTC": "#0071C5",
    "CSCO": "#0096D6",

    # Servicios de Comunicación
    "META": "#4267B2",
    "GOOG": "#4285F4",
    "NFLX": "#E50914",
    "DIS": "#113CCF",
    "CMCSA": "#FFC300",

    # Consumo Cíclico
    "AMZN": "#2ca02c",
    "TSLA": "#CC0000",
    "NKE": "#111111",
    "F": "#003399",
    "SBUX": "#00704A",

    # Consumo Defensivo
    "KO": "#FF0000",
    "PEP": "#005CB8",
    "PG": "#01BFFF",
    "MDLZ": "#9B30FF",
    "BF-B": "#6B8E23",

    # Servicios Financieros
    "JPM": "#0070C0",
    "V": "#0057B8",
    "MA": "#FF5F00",
    "GS": "#B8860B",
    "AXP": "#2E77BB",

    # Energía
    "XOM": "#C70039",
    "CVX": "#900C3F",
    "BP": "#009639",
    "TTE": "#E6B422",
    "COP": "#FF8000"
}

# ================================
# CSS Modo Oscuro Mejorado
# ================================
dark_theme = ui.tags.style(
"""
/* Body */
body { background-color: #0f0f0f; color: #e6e6e6; }

/* Sidebar & Cards */
.sidebar, .card, .form-control, .selectize-input, .selectize-dropdown {
  background-color: #141414 !important;
  color: #e6e6e6 !important;
  border-color: #2b2b2b !important;
}

/* Card header */
.card-header { background-color: #191919 !important; color: #fff !important; }

/* Selectize (chips) */
.selectize-control .item {
  background-color: #262626 !important;
  color: #e6e6e6 !important;
  border: 1px solid #303030 !important;
  padding: 2px 6px;
  margin-right: 4px;
}

/* Make selectize full width and visible */
.selectize-input { min-height: 38px; width: 100% !important; }

/* Slider styling (visual) */
.input-range { width: 100% !important; }

/* Ensure card content has padding and the plot fits */
.card { padding: 12px !important; }

/* Adjust legend font size */
.legend { font-size: 9px !important; }
"""
)

# ================================
# UI
# ================================
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h2("Panel de Control", class_="my-3"),
        ui.input_selectize(
            "empresas",
            "Seleccione empresas:",
            choices=sorted(df["Ticker"].unique()),
            selected=["MA", "V"],
            multiple=True
        ),
        ui.br(),
        ui.input_slider(
            "fecha_rango",
            "Rango de Fechas:",
            min=df["Date"].min(),
            max=df["Date"].max(),
            value=(df["Date"].min(), df["Date"].max()),
            step=1
        ),
    ),

    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Comparación del Precio de Cierre entre Empresas en USD"),
            ui.output_plot("plot_acciones", width="100%", height=420)
        ),
        column_size="100%"
    ),

    dark_theme
)

# ================================
# Server
# ================================
def server(input, output, session):

    @reactive.calc
    def datos_filtrados():
        sel = input.empresas() or []
        data = df[df["Ticker"].isin(sel)]
        fi, ff = input.fecha_rango()
        # fi, ff son objeto date; filtrar directo
        data = data[(data["Date"] >= fi) & (data["Date"] <= ff)].copy()
        # ordenar por fecha para que las líneas se dibujen bien
        data.sort_values(by="Date", inplace=True)
        return data

    @output
    @render.plot
    def plot_acciones():
        data = datos_filtrados()

        plt.figure(figsize=(10,4))
        plt.style.use("dark_background")

        for ticker in input.empresas():
            df_ticker = data[data["Ticker"] == ticker]
            if df_ticker.empty:
                continue
            
            color = colores_empresas.get(ticker, "#aaaaaa")  # Color de seguridad
            
            plt.plot(
                df_ticker["Date"],
                df_ticker["Close"],
                label=ticker,
                linewidth=2,
                color=color
            )

        plt.xlabel("Fecha", fontsize=11, color="white")
        plt.ylabel("Precio de Cierre", fontsize=11, color="white")
        plt.title("Evolución Histórica del Precio de Cierre", fontsize=13, weight="bold")

        # ✅ Leyenda mejorada para fondo oscuro
        legend = plt.legend(
            title="Empresas",
            fontsize=9,
            title_fontsize=10,
            loc="upper left",
            frameon=True
        )

        legend.get_frame().set_facecolor("#1e1e1e")
        legend.get_frame().set_edgecolor("#444")

        plt.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
# ================================
# Run app
# ================================
app = App(app_ui, server)