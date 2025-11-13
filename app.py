from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
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
# UI
# ================================
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h2("Panel de Control", class_="my-3"),
        # filtro por industria
        ui.input_select(
            "sector",
            "Seleccione industria:",
            choices=list(sectores.keys()),
            selected="Tecnología"
        ),
        ui.br(),
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
        ui.br(),
        ui.input_switch(
            "modo_rend",
            "Mostrar rendimiento acumulado (%)",
            value=False
        ),
    ),

    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Comparación Interactiva de Acciones"),
            output_widget("plot_acciones", width="100%", height="420px")
        ),
        column_size="100%"
    )
)

# ================================
# Server
# ================================
def server(input, output, session):

    #Actualizar empresas según sector
    @reactive.effect
    @reactive.event(input.sector)
    def _():
        opciones = sectores[input.sector()]
        ui.update_selectize("empresas", choices=opciones, selected=[opciones[0]])

    @reactive.calc
    def datos_filtrados():
        sel = input.empresas() or []
        data = df[df["Ticker"].isin(sel)].copy()

        fi, ff = input.fecha_rango()
        data = data[(data["Date"] >= fi) & (data["Date"] <= ff)]
        data.sort_values(by="Date", inplace=True)
        return data

    @output
    @render_widget
    def plot_acciones():
        data = datos_filtrados().copy()

        # Si el modo rendimiento está activado, calcular %
        if input.modo_rend():
            data["Close"] = data.groupby("Ticker")["Close"].transform(lambda x: (x / x.iloc[0] - 1) * 100)
            y_label = "Rendimiento acumulado (%)"
            title = "Rendimiento Acumulado desde el Inicio del Rango"
        else:
            y_label = "Precio de Cierre (USD)"
            title = "Evolución Histórica del Precio de Cierre"

        # Crear gráfico interactivo (modo claro)
        fig = px.line(
            data,
            x="Date",
            y="Close",
            color="Ticker",
            color_discrete_map=colores_empresas,
            labels={"Close": y_label, "Date": "Fecha"},
            title=title
        )

        # Ajustes visuales
        fig.update_layout(
            template="plotly_white",
            legend_title_text="Empresas",
            font=dict(color="black"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=40, r=30, t=50, b=40)
        )

        return fig

# ================================
# Run app
# ================================
app = App(app_ui, server)