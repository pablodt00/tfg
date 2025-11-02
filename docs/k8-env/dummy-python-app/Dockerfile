# Imagen base
FROM python:3.10-slim

# Directorio de trabajo
WORKDIR /app

# Copiar archivos
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Exponer puerto Flask
EXPOSE 5000

# Comando de ejecución
CMD ["python", "app.py"]
