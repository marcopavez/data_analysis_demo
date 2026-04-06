# CLAUDE.md

## Project Overview

E-commerce sales data analysis project (demo). Loads CSV datasets, cleans data, generates matplotlib/plotly visualizations, and exports PDF reports using ReportLab.

**Language:** Python 3.13  
**Repo:** marcopavez/data_analysis_demo  
**User language:** Spanish (code comments, PDF content, commit messages)

## Project Structure

```
data/                        # CSV source files (National + International)
data/.complete/datasets/     # Original/raw datasets backup
output/                      # Generated PDF reports
national_sales_report.py     # Main analysis script (national sales)
international_sales_report.py # International sales analysis (empty/WIP)
dockerfile                   # Docker build for headless PDF generation
requirements.txt             # pip dependencies
```

## Key Commands

```bash
# Run national sales analysis
python national_sales_report.py

# Docker build & run (headless, outputs PDF to ./output)
docker build -t datos .
docker run -v ./output:/output datos
```

## Dependencies

matplotlib, pandas, plotly, reportlab — pinned in `requirements.txt`.

## Architecture

`national_sales_report.py` follows a pipeline pattern:
1. `load_data()` — read CSV, assign column names
2. `clean_data()` — drop invalid rows, normalize categories, title-case text
3. `group_by_*()` — aggregation functions returning Series/DataFrames
4. `plot_by_*()` — matplotlib charts returning Figure objects
5. `show_table_category_color()` — interactive plotly table (not in PDF)
6. `export_pdf()` — ReportLab PDF generation with charts + commentary

## Conventions

- Commit messages in Spanish
- CSV column names are hardcoded in `load_data()` — update if source schema changes
- PDF output path is absolute `/output/` for Docker compatibility
- `MPLBACKEND=Agg` is set in Dockerfile for headless rendering
