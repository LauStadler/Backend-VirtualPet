# Usamos una imagen ligera de Python
FROM python:3.12-slim-bookworm

# Instalamos uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Establecemos el directorio de trabajo
WORKDIR /app

# Evitamos que uv cree un entorno virtual dentro del contenedor
# para simplificar la ejecución (ya estamos aislados por Docker)
ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Copiamos los archivos de dependencias primero para aprovechar el caché de capas
COPY pyproject.toml uv.lock ./

# Instalamos las dependencias
# --no-dev: No instala dependencias de desarrollo (pytest, etc.)
# --frozen: Asegura que el lockfile no cambie
RUN uv sync --no-dev --frozen

# Copiamos el resto del código del backend
COPY . .

# Exponemos el puerto que usa FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación
# Usamos uv run para asegurar que el path sea el correcto
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
