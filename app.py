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
    "AMZN": "#4DB6AC",   # Teal elegante
    "KO":   "#EF5350",   # Rojo corporativo suave
    "UBER": "#FAFAFA",   # Blanco humo
    "PEP":  "#42A5F5",   # Azul ejecutivo
    "TSLA": "#FF7043",   # Naranja rojizo
    "AAPL": "#90CAF9",   # Azul pastel
    "MSFT": "#FFD54F",   # Amarillo dorado
    "NVDA": "#66BB6A",   # Verde profesional
    "NFLX": "#E53935",   # Rojo Netflix
    "DIS":  "#5C6BC0",   # Azul púrpura
    "NKE":  "#ECECEC",   # Gris claro
    "F":    "#29B6F6",   # Azul cyan
    "WMT": "#81D4FA",    # Azul retail
    "PFE": "#64B5F6",    # Azul farmacéutico
    "META": "#4A90E2",   # Meta Blue
    "GOOG": "#8EACBB",   # Azul gris
    "MA":   "#FFB74D",   # Orange gold
    "V":    "#4FC3F7"    # Azul Visa
}

# ================================
# CSS modo oscuro
# ================================

dark_theme = ui.tags.style(
"""
body { background-color: #0f0f0f; color: #e6e6e6; }
.sidebar, .card, .form-control, .selectize-input, .selectize-dropdown {
  background-color: #141414 !important;
  color: #e6e6e6 !important;
  border-color: #2b2b2b !important;
}
.card-header { background-color: #191919 !important; color: #fff !important; }
.selectize-control .item {
  background-color: #262626 !important;
  color: #e6e6e6 !important;
  border: 1px solid #303030 !important;
  padding: 2px 6px;
  margin-right: 4px;
}
.selectize-input { min-height: 38px; width: 100% !important; }
.card { padding: 12px !important; }
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
            output_widget("plot_acciones", width="100%", height="420px")  # 👈 aquí corregido
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

        # Crear gráfico interactivo
        fig = px.line(
            data,
            x="Date",
            y="Close",
            color="Ticker",
            color_discrete_map=colores_empresas,
            labels={"Close": y_label, "Date": "Fecha"},
            title=title
        )

        # Ajustes visuales (tema oscuro)
        fig.update_layout(
            template="plotly_dark",
            legend_title_text="Empresas",
            font=dict(color="white"),
            plot_bgcolor="#0f0f0f",
            paper_bgcolor="#0f0f0f",
            margin=dict(l=40, r=30, t=50, b=40)
        )

        fig.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor="#333333")
        fig.update_yaxes(showgrid=True, gridwidth=0.2, gridcolor="#333333")

        return fig

# ================================
# Run app
# ================================
app = App(app_ui, server)