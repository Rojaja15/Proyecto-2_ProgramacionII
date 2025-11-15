from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px

# ================================
# Cargar datos
# ================================

df = pd.read_csv("Datos.csv")
df["Date"] = pd.to_datetime(df["Date"]).dt.date

industrias = {
    "Tecnología": ["AAPL", "MSFT", "NVDA", "INTC", "CSCO"],
    "Servicios de Comunicación": ["META", "GOOG", "NFLX", "DIS", "CMCSA"],
    "Consumo Cíclico": ["AMZN", "ADS", "NKE", "COLM", "SBUX"],
    "Consumo Defensivo": ["KO", "PEP", "PG", "MDLZ", "BF-B"],
    "Servicios Financieros": ["JPM", "V", "MA", "GS", "AXP"],
    "Energía": ["XOM", "CVX", "BP", "TTE", "COP"],
    "Automotriz": ["TSLA", "F", "TM", "HMC", "RACE"]
}

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
    "ADS": "#004B87",
    "NKE": "#111111",
    "COLM": "#005F73",
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
    "COP": "#FF8000",

    # Automotriz
    "TSLA": "#CC0000",
    "F": "#003399",
    "TM": "#079213",    
    "HMC": "#DAC71C",  
    "RACE": "#FF2800"
}

# ================================
# UI
# ================================
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h2("Panel de Control", class_="my-3"),

        # Nuevo filtro por industria
        ui.input_select(
            "industria",
            "Seleccione industria:",
            choices=list(industrias.keys()),
            selected="Tecnología"
        ),

        ui.input_selectize(
            "empresas",
            "Seleccione empresas:",
            choices=sorted(df["Ticker"].unique()),
            selected=[],
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

    ui.navset_tab(
        ui.nav_panel( 
            "Historial de acciones de empresas en USD",
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("Historia Precio de Cierre por/entre Empresas en USD"),
                    output_widget("plot_acciones", width="100%", height="420px")
                ),
                column_size="100%"
            ),
        ),

        ui.nav_panel(
            "Tabla de Precios",
            ui.card(
                ui.card_header("Tabla de precios"),
                ui.output_data_frame("tabla_precios")
            )
        )
    ),
)

# ================================
# Server
# ================================
def server(input, output, session):

    # Actualiza empresas al cambiar industria
    @reactive.effect
    def _():
        ind = input.industria()
        if ind in industrias:
            ui.update_selectize(
                "empresas",
                choices=industrias[ind],
                selected=[industrias[ind][0]]
            )

    @reactive.calc
    def datos_filtrados():
        sel = input.empresas() or []
        data = df[df["Ticker"].isin(sel)].copy()

        fi, ff = input.fecha_rango()
        data = data[(data["Date"] >= fi) & (data["Date"] <= ff)]

        data.sort_values(by="Date", inplace=True)
        return data

    # -------- Plot ----------
    @output
    @render_widget
    def plot_acciones():
        data = datos_filtrados().copy()

        if input.modo_rend():
            data["Close"] = data.groupby("Ticker")["Close"].transform(
                lambda x: (x / x.iloc[0] - 1) * 100
            )
            y_label = "Rendimiento acumulado (%)"
            title = "Rendimiento Acumulado desde el Inicio del Rango"
        else:
            y_label = "Precio de Cierre (USD)"
            title = "Evolución Histórica del Precio de Cierre"

        fig = px.line(
            data,
            x="Date",
            y="Close",
            color="Ticker",
            color_discrete_map=colores_empresas,
            labels={"Close": y_label, "Date": "Fecha"},
            title=title
        )

        fig.update_layout(
            template="plotly_white",
            legend_title_text="Empresas",
            font=dict(color="black"),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=40, r=30, t=50, b=40),
            height=420
        )

        return fig

    # -------- Tabla ----------
    @output
    @render.data_frame
    def tabla_precios():
        data = datos_filtrados()
        columnas = ["Date", "Open", "High", "Low", "Close", "Volume", "Ticker"]
        data[columnas[1:5]] = data[columnas[1:5]].round(2)
        return data[columnas].sort_values(by=["Ticker", "Date"])

# ================================
# Run app
# ================================
app = App(app_ui, server)
