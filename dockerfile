FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY national_sales_report.py .
COPY international_sales_report.py .
COPY data/ ./data/

# Crear carpeta de salida
RUN mkdir /output

# Declarar /output como volumen — le indica a Docker que es una carpeta de intercambio
VOLUME /output

CMD ["python", "national_sales_report.py"]