from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt

# ================================
# Cargar datos
# ================================
df = pd.read_csv("Datos.csv")
df["Date"] = pd.to_datetime(df["Date"]).dt.date

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
        ui.h2("Panel de Control"),

        ui.input_selectize(
            "empresas",
            "Seleccione empresas:",
            choices=sorted(df["Ticker"].unique()),
            selected=["MA","V"],
            multiple=True
        ),

        ui.input_slider(
            "fecha_rango",
            "Rango de Fechas",
            min=df["Date"].min(),
            max=df["Date"].max(),
            value=(df["Date"].min(), df["Date"].max()),
            step=1
        )
    ),

    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Comparación del Precio de Cierre entre Empresas"),
            ui.output_plot("plot_acciones")
        )
    )
)

# ================================
# Server
# ================================
def server(input, output, session):

    @reactive.calc
    def datos_filtrados():
        data = df[df["Ticker"].isin(input.empresas())]

        fecha_ini, fecha_fin = input.fecha_rango()
        data = data[(data["Date"] >= fecha_ini) & (data["Date"] <= fecha_fin)]

        return data

    @output
    @render.plot
    def plot_acciones():
        data = datos_filtrados()

        plt.figure(figsize=(12,5))

        for ticker in input.empresas():
            df_ticker = data[data["Ticker"] == ticker]
            if df_ticker.empty:
                continue
            
            color = colores_empresas.get(ticker, "#7f7f7f")
            
            plt.plot(
                df_ticker["Date"],
                df_ticker["Close"],
                label=ticker,
                linewidth=2,
                color=color
            )

        plt.xlabel("Fecha")
        plt.ylabel("Precio de Cierre")
        plt.title("Evolución Histórica del Precio de Cierre")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()

# ================================
# Run app
# ================================
app = App(app_ui, server)
