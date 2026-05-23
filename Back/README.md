# Virtual Pet API

Ecommerce de productos para mascotas - Mar del Plata.

## Características
- Gestión de productos y categorías (Sincronizado desde ERP externo).
- Autenticación de usuarios con JWT y roles (Cliente, Depósito, Admin).
- Carrito de compras y proceso de Checkout.
- Historial de pedidos para clientes.
- Panel de Backoffice para gestión de estados de pedidos.
- Notificaciones en tiempo real vía WebSockets.

## Documentación de la API
Para una lista detallada de todos los endpoints disponibles, consulta:
👉 **[API.md](./api.md)**

También puedes acceder a la documentación interactiva (Swagger) en:
`http://localhost:8000/docs`

## Tecnologías
- **Framework:** FastAPI
- **Base de Datos:** PostgreSQL / MySQL (Alembic para migraciones)
- **ORM:** SQLAlchemy
- **Autenticación:** JWT (PyJWT)
- **Validación:** Pydantic v2
- **Gestor de paquetes:** `uv`

## Configuración Local

1. Instalar dependencias:
   ```bash
   uv sync
   ```

2. Configurar variables de entorno:
   Copiar `.env.example` a `.env` y completar los valores.

3. Correr migraciones:
   ```bash
   alembic upgrade head
   ```

4. Ejecutar servidor:
   ```bash
   uv run uvicorn main:app --reload
   ```

## Estructura del Proyecto
- `modules/`: Lógica de negocio dividida en dominios (auth, catalog, orders, sales).
- `backoffice/`: Controladores y lógica específica para la administración.
- `infrastructure/`: Configuración de base de datos, migraciones y servicios externos.
- `shared/`: Utilidades, excepciones, middleware y dependencias comunes.
- `tests/`: Suite de pruebas unitarias e integración.
