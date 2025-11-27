# 1. Carga de Datos

El proyecto utiliza un archivo CSV (Datos.csv) que contiene información histórica de acciones.

Los datos se cargan con pandas:

```python
import pandas as pd

df = pd.read_csv("Datos.csv")
df["Date"] = pd.to_datetime(df["Date"]).dt.date
```

Columnas requeridas en el archivo:
+ Date
+ Ticker
+ Open
+ High
+ Low
+ Close
+ Volume
  
El sistema convierte la columna Date a formato fecha para permitir filtrado por rango usando la interfaz.

# 2. Diccionario de Industrias

El código define un diccionario llamado industrias, que agrupa los tickers de distintas compañías según su sector económico:

```python
industrias = {
    "Tecnología": [...],
    "Servicios de Comunicación": [...],
}
```

¿Para qué se usa?

+ Para actualizar la lista de empresas según la industria seleccionada.

+ Para mejorar la navegación del usuario dentro del panel lateral.

# 3. Paleta de Colores Corporativa

El diccionario colores_empresas asigna un color específico a cada empresa.
Este mapa de colores se utiliza en los gráficos de Plotly para mantener consistencia visual.

```python
colores_empresas = {

    "AAPL": "#1f77b4",
    
    "MSFT": "#BE8C00",
    
    ...
}
```

Esto asegura que cada empresa mantenga el mismo color sin importar el análisis o el rango de fechas seleccionado.

# 4. Interfaz de Usuario (UI)

La interfaz se construye con `ui.page_sidebar()`, que crea una página con panel lateral y contenido principal.

Componentes principales del panel lateral:

+ Selector de Industria
+ Selector múltiple de Empresas
+ Slider de rango de fechas
+ Switch para mostrar rendimiento acumulado

Pestañas de navegación para:

+ Gráfico histórico
+ Tabla de precios

## Panel de Gráfico

Incluye un gráfico interactivo en un card:

```python
output_widget("plot_acciones")`
```

## Panel de Tabla

Incluye:

+ Selector de frecuencia:

 - Datos diarios

 - Promedio mensual

+ Tabla interactiva usando `ui.output_data_frame`

## 5. Lógica del Servidor

La lógica de backend se implementa en la función:

```python
def server(input, output, session):
```

Contiene funciones reactivas, efectos, cálculos y renderizados.

# 6. Funciones Reactivas
## 6.1. Actualización automática de empresas:

Cuando se selecciona una industria, se actualiza la lista de empresas disponibles:

```python
@reactive.effect
def _():
    ui.update_selectize(...)`
```

Permite que el usuario siempre vea solo los tickers pertenecientes al sector elegido.

## 6.2. Filtrado de datos según entradas del usuario

```python
@reactive.calc
def datos_filtrados():`
```

Esta función:

+ Filtra por empresas seleccionadas
+ Filtra por rango de fechas
+ Ordena los datos cronológicamente
+ Este es el dataset base para el gráfico.

## 6.3. Resumen de datos para tabla

```python
@reactive.calc
def datos_resumen():`
```
Dependiendo de la frecuencia seleccionada:

+ Diaria: solo redondea valores
+ Mensual: calcula el promedio mensual (resample("M").mean())

Devuelve un dataframe limpio listo para la tabla.

# 7. Generación del Gráfico

El gráfico se genera en:

```python
@output
@render_widget
def plot_acciones():`
```

Esta función:

- Decide qué mostrar:

Si el usuario activa `Rendimiento Acumulado`, normaliza el precio:

```python
data["Close"] = (x / x.iloc[0] - 1) * 100
```

Si no, muestra precios originales.

- Construye un gráfico de líneas con Plotly:

+ Eje X: Fecha

+ Eje Y: Precio o rendimiento

+ Líneas por compañía

+ Colores según colores_empresas

El resultado es un gráfico interactivo, claro y totalmente dinámico.

# 8. Tabla de Precios

La tabla se genera con:

```python
@output
@render.data_frame
def tabla_precios():`
```

Muestra las columnas:

+ Date
+ Open
+ High
+ Low
+ Close
+ Volume
+ Ticker

Los datos están ordenados por empresa y fecha.

# 9. Ejecución de la App

La aplicación se ejecuta con:

`app = App(app_ui, server)`

# Resumen del Flujo Lógico

1. El usuario selecciona industria, empresas y rango de fechas.

2. Las funciones reactivas filtran y organizan la data.

3. El servidor decide si mostrar precios originales o rendimiento acumulado.

4. Plotly genera un gráfico interactivo.

5. La tabla presenta los datos diarios o agregados por mes.

6. La UI presenta todo de forma dinámica y limpia.
