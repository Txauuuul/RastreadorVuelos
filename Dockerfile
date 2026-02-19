FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear carpetas necesarias
RUN mkdir -p data logs

# Ejecutar aplicación
CMD ["python", "main.py"]
