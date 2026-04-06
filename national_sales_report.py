import os
import io
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# ─────────────────────────────────────────────
# 1. CARGA DE DATOS
# ─────────────────────────────────────────────

def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df.columns = ["index", "sku", "design", "stock", "category", "size", "color"]
    return df


# ─────────────────────────────────────────────
# 2. LIMPIEZA DE DATOS
# ─────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Eliminar filas sin SKU o con valores inválidos
    df = df[df["sku"].notna()]
    df = df[df["sku"] != "#REF!"]

    # Limpiar columna category
    df["category"] = df["category"].str.replace("AN : ", "", regex=False)
    df["category"] = df["category"].replace("SET", "KURTA SET")

    # Aplicar Title Case a todas las columnas de texto
    string_cols = df.select_dtypes(include="object").columns
    df[string_cols] = df[string_cols].apply(lambda col: col.str.title())

    return df


# ─────────────────────────────────────────────
# 3. ANÁLISIS / AGRUPACIONES
# ─────────────────────────────────────────────

def group_by_category(df: pd.DataFrame) -> pd.Series:
    return df.groupby("category").size().sort_values(ascending=False)

def group_by_size(df: pd.DataFrame) -> pd.Series:
    return df.groupby("size").size().sort_values(ascending=False)

def group_by_color(df: pd.DataFrame, min_count: int = 35) -> pd.DataFrame:
    result = df.groupby("color").size().reset_index()
    result.columns = ["color", "cantidad"]
    return result[result["cantidad"] > min_count].sort_values("cantidad", ascending=False)

def group_by_category_color(df: pd.DataFrame) -> pd.DataFrame:
    result = df.groupby(["category", "color"]).size().reset_index()
    result.columns = ["category", "color", "quantity"]
    return result


# ─────────────────────────────────────────────
# 4. VISUALIZACIONES (matplotlib)
# ─────────────────────────────────────────────

def plot_by_category(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))
    group_by_category(df).plot(kind="bar", ax=ax, color="steelblue")
    ax.set_title("Ventas por categoría de producto")
    ax.set_xlabel("Categoría")
    ax.set_ylabel("Cantidad")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig

def plot_by_size(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8, 5))
    group_by_size(df).plot(kind="bar", ax=ax, color="coral")
    ax.set_title("Ventas por talla de prenda")
    ax.set_xlabel("Talla")
    ax.set_ylabel("Cantidad")
    plt.xticks(rotation=0)
    plt.tight_layout()
    return fig

def plot_by_color(df: pd.DataFrame) -> plt.Figure:
    data = group_by_color(df)
    fig, ax = plt.subplots(figsize=(10, 5))
    data.plot(kind="bar", x="color", y="cantidad", ax=ax, color="mediumpurple", legend=False)
    ax.set_title("Ventas por color de prenda (colores con más de 35 unidades)")
    ax.set_xlabel("Color")
    ax.set_ylabel("Cantidad")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────
# 5. TABLA INTERACTIVA (plotly)
# ─────────────────────────────────────────────

def show_table_category_color(df: pd.DataFrame):
    data = group_by_category_color(df)
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Categoría", "Color", "Cantidad"],
            fill_color="steelblue",
            font=dict(color="white", size=13)
        ),
        cells=dict(
            values=[data["category"], data["color"], data["quantity"]],
            fill_color="lavender"
        )
    )])
    fig.update_layout(title="Cantidad de prendas por categoría y color")
    fig.show()


# ─────────────────────────────────────────────
# 6. EXPORTAR INFORME PDF
# ─────────────────────────────────────────────

def fig_to_image(fig: plt.Figure, width: float = 16*cm, height: float = 9*cm) -> Image:
    """Convierte una figura matplotlib a imagen embebible en reportlab."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return Image(buf, width=width, height=height)


def export_pdf(
    figures_with_comments: list[tuple[plt.Figure, str, str]],
    output_path: str = "informe_ventas.pdf"
):
    """
    Genera un informe PDF con páginas A4, gráficos y comentarios de análisis.

    figures_with_comments: lista de tuplas (figura, titulo, comentario)
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    section_title_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=10,
        spaceAfter=6
    )
    comment_style = ParagraphStyle(
        "Comment",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        leading=16,
        alignment=TA_JUSTIFY,
        spaceBefore=8,
        spaceAfter=6
    )

    story = []

    # ── Portada / encabezado del informe ──
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Informe de Ventas E-commerce", title_style))
    story.append(Paragraph("Análisis exploratorio de datos de productos por categoría, talla y color", subtitle_style))
    story.append(Spacer(1, 0.5*cm))

    # Línea decorativa
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4a90d9")))
    story.append(Spacer(1, 1*cm))

    # ── Sección por gráfico ──
    for fig, section_title, comment in figures_with_comments:
        story.append(Paragraph(section_title, section_title_style))
        story.append(fig_to_image(fig))
        story.append(Paragraph(comment, comment_style))
        story.append(PageBreak())

    doc.build(story)
    print(f"Informe guardado en: {output_path}")

# ─────────────────────────────────────────────
# 7. MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Carga y limpieza
    salesDf = load_data("data/National_Sale_Report.csv")
    salesDf = clean_data(salesDf)

    # Generar gráficos
    fig_category = plot_by_category(salesDf)
    fig_size     = plot_by_size(salesDf)
    fig_color    = plot_by_color(salesDf)

    # Mostrar gráficos en pantalla
    plt.show()

    # Tabla interactiva con plotly (no va al PDF, es interactiva)
    show_table_category_color(salesDf)

    # Exportar informe PDF con gráficos y comentarios de análisis
    export_pdf(
        figures_with_comments=[
            (
                fig_category,
                "1. Ventas por Categoría de Producto",
                "El gráfico muestra la distribución de prendas según su categoría. "
                "Se puede observar que las categorías con mayor volumen son Kurta y Leggings, "
                "lo que sugiere que estos productos representan el core del negocio. "
                "Se recomienda priorizar el stock de estas categorías para evitar quiebres."
            ),
            (
                fig_size,
                "2. Ventas por Talla de Prenda",
                "La distribución por tallas indica que las tallas M y L concentran la mayor "
                "demanda. Las tallas extremas (XXS, XXL) tienen una participación marginal. "
                "Esto es relevante para optimizar la curva de compra y reducir inventario ocioso."
            ),
            (
                fig_color,
                "3. Ventas por Color de Prenda (colores con más de 35 unidades)",
                "Entre los colores más demandados destacan Black, Navy Blue y White, "
                "lo que es coherente con tendencias de moda básica y atemporal. "
                "Los colores neutros dominan el catálogo y son los de mayor rotación, "
                "mientras que los colores estacionales tienen menor participación relativa."
            ),
        ],
        output_path="/output/informe_ventas_nacionales.pdf"
    )