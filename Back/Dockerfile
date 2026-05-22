# Usamos una imagen de Python oficial
    FROM python:3.12-slim-bookworm
    
    # Instalamos uv
    COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
    
    # Directorio de trabajo
    WORKDIR /app
    
   # Copiamos archivos de dependencias
   COPY pyproject.toml uv.lock ./
   
   # Instalamos las dependencias
   # Esto creará una carpeta .venv dentro de /app
   RUN uv sync --frozen --no-dev
   
   # Copiamos el resto del código
   COPY . .
   
   # Añadimos el entorno virtual al PATH para que el sistema encuentre uvicorn
   ENV PATH="/app/.venv/bin:$PATH"
  
   # Exponemos el puerto
   EXPOSE 8000
   
   # Ejecutamos directamente con uvicorn (ya está en el PATH gracias a .venv)
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]