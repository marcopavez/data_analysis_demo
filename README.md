# Data Analysis Demo

Proyecto demo de análisis de datos de ventas e-commerce con Python.

## Funcionalidades

- Carga y limpieza de datos desde CSV
- Análisis exploratorio: ventas por categoría, talla y color
- Visualizaciones con matplotlib (gráficos de barras)
- Tabla interactiva con plotly
- Exportación automática de informe PDF con ReportLab

## Requisitos

- Python 3.13+
- Dependencias: `pip install -r requirements.txt`

## Uso

```bash
# Ejecución local
python national_sales_report.py

# Ejecución con Docker (genera PDF en ./output)
docker build -t datos .
docker run -v ./output:/output datos
```

## Estructura

```
data/                         # Datasets CSV
output/                       # Informes PDF generados
national_sales_report.py      # Análisis de ventas nacionales
international_sales_report.py # Análisis de ventas internacionales (WIP)
dockerfile                    # Imagen Docker para ejecución headless
```
