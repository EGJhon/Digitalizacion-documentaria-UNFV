FROM python:3.10-slim-bullseye

# Instalar dependencias del SO: Tesseract (OCR), español, wkhtmltopdf (PDF)
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    poppler-utils \
    curl \
    gnupg2 \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Agregar repositorio de Microsoft e instalar msodbcsql17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
