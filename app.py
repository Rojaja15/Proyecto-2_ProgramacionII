from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px

# ================================
# Cargar datos
# ================================
df = pd.read_csv("Datos.csv")

# Convertir fechas correctamente (datetime, NO .dt.date)
df["Date"] = pd.to_datetime(df["Date"])  

# ================================
# Paleta de colores corporativa
# ================================
colores_empresas = {
    "AMZN": "#2ca02c",  
    "KO":   "#FF0000",   
    "UBER": "#000000",   
    "PEP":  "#005CB8",  
    "TSLA": "#CC0000",   
    "AAPL": "#1f77b4",   
    "MSFT": "#BE8C00",   
    "NVDA": "#76B900",   
    "NFLX": "#E50914",   
    "DIS":  "#113CCF",  
    "NKE":  "#111111",   
    "F":    "#003399",   
    "WMT": "#0071CE",   
    "PFE": "#0082D1",   
    "META": "#4267B2",  
    "GOOG": "#4285F4",  
    "MA":   "#FF5F00",  
    "V":    "#0057B8"  
}

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

        ui.br(),

        ui.input_switch(
            "modo_rend",
            "Mostrar rendimiento acumulado (%)",
            value=False
        ),
    ),

    ui.navset_tab(
        ui.nav_panel( 
            "Comparación del Precio de Cierre entre Empresas en USD",
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("Comparación del Precio de Cierre entre Empresas en USD"),
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
