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

## Arquitectura de Base de Datos
El sistema utiliza un enfoque de **Desacoplamiento Referencial** (Preparado para Microservicios):
- **Relaciones Inter-Módulo:** (Ej: Orders -> Users, Items -> Products) Se manejan mediante **identificadores lógicos** sin Foreign Keys físicas. La integridad se garantiza en la capa de servicios (Hidratación manual).
- **Relaciones Intra-Módulo:** (Ej: Order -> OrderItem, Product -> Category) Mantienen **Foreign Keys físicas** para integridad referencial local.
- **Snapshots:** Los `order_items` guardan una copia (nombre, precio, imagen) del producto al momento de la venta para garantizar la inmutabilidad del historial.

## Configuración Local
...
   ```bash
   uv run uvicorn main:app --reload
   ```

## Mantenimiento y Conexión a Producción

### Acceso a Base de Datos (MySQL Workbench)
Para gestionar la base de datos de AWS de forma segura:
1. Crear nueva conexión en Workbench.
2. **Method:** `Standard TCP/IP over SSH`.
3. **SSH Hostname:** `3.133.84.16:22` (User: `ubuntu`).
4. **SSH Key:** Seleccionar tu archivo `.pem`.
5. **MySQL Hostname:** `127.0.0.1` (Port: `3306`).
6. **User:** `root` / **Password:** `VirtualPetRoot`.

### Aplicar Cambios en AWS
Cada vez que se suban nuevas migraciones de Alembic:
```bash
# Entrar al servidor y ejecutar dentro de la carpeta Back:
docker compose exec backend alembic upgrade head
```

## Estructura del Proyecto
- `modules/`: Lógica de negocio dividida en dominios (auth, catalog, orders, sales).
- `backoffice/`: Controladores y lógica específica para la administración.
- `infrastructure/`: Configuración de base de datos, migraciones y servicios externos.
- `shared/`: Utilidades, excepciones, middleware y dependencias comunes.
- `tests/`: Suite de pruebas unitarias e integración.
