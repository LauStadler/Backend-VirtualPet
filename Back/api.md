# Documentación de la API - Virtual Pet

Este documento describe los endpoints disponibles para la API de Virtual Pet.

## URL Base
La API está disponible en: `http://localhost:8000` (desarrollo)

## Autenticación
La mayoría de los endpoints requieren un JSON Web Token (JWT) enviado en el header `Authorization`.
Formato: `Authorization: Bearer <tu_token>`

Roles:
- `CLIENTE`: Puede navegar productos, gestionar su carrito (en el frontend) y ver sus propios pedidos.
- `DEPOSITO`: Puede ver todos los pedidos y avanzar su estado.
- `ADMIN`: Acceso total, incluyendo gestión de usuarios.

---

## Índice
- [Auth](#auth)
- [Catálogo](#catálogo)
- [Ventas](#ventas)
- [Pedidos](#pedidos)
- [Backoffice](#backoffice)
- [Salud (Health)](#salud-health)

---

## Auth
Prefijo: `/auth`

### Registrar nuevo cliente
- **URL:** `/auth/register`
- **Método:** `POST`
- **Acceso:** Público
- **Descripción:** Crea una cuenta de cliente y devuelve un JWT.

### Iniciar sesión
- **URL:** `/auth/login`
- **Método:** `POST`
- **Acceso:** Público
- **Descripción:** Autentica a un usuario existente y devuelve un JWT.

### Obtener perfil propio
- **URL:** `/auth/me`
- **Método:** `GET`
- **Acceso:** Autenticado (cualquier rol)
- **Descripción:** Retorna los datos de perfil del usuario autenticado.

### Crear usuario (Admin)
- **URL:** `/auth/users`
- **Método:** `POST`
- **Acceso:** `ADMIN`
- **Descripción:** Permite a un administrador crear usuarios con cualquier rol (CLIENTE, DEPOSITO, ADMIN).

---

## Catálogo
Prefijo: `/catalog`

### Listar productos
- **URL:** `/catalog/products`
- **Método:** `GET`
- **Acceso:** Público
- **Descripción:** Retorna una lista paginada de productos activos con filtros opcionales de categoría y stock.

### Detalle de un producto
- **URL:** `/catalog/products/{product_id}`
- **Método:** `GET`
- **Acceso:** Público
- **Descripción:** Retorna el detalle completo de un producto específico.

### Listar categorías
- **URL:** `/catalog/categories`
- **Método:** `GET`
- **Acceso:** Público
- **Descripción:** Retorna todas las categorías de productos disponibles.

---

## Ventas
Prefijo: `/cart`

### Confirmar compra
- **URL:** `/cart/checkout`
- **Método:** `POST`
- **Acceso:** `CLIENTE`
- **Descripción:** Procesa los items del carrito y crea un nuevo pedido.

---

## Pedidos
Prefijo: `/orders`

### Mis pedidos
- **URL:** `/orders`
- **Método:** `GET`
- **Acceso:** Autenticado
- **Descripción:** Retorna el historial de pedidos del cliente autenticado.

### Detalle de un pedido
- **URL:** `/orders/{order_id}`
- **Método:** `GET`
- **Acceso:** Autenticado (Solo el dueño)
- **Descripción:** Retorna los detalles completos de un pedido específico perteneciente al usuario.

---

## Backoffice
Prefijo: `/backoffice`

### Conexión WebSocket
- **URL:** `/backoffice/ws`
- **Protocolo:** `WS`
- **Acceso:** Interno (Usado para notificaciones en tiempo real)
- **Descripción:** Endpoint de WebSocket para recibir actualizaciones de pedidos en tiempo real.

### Listar todos los pedidos
- **URL:** `/backoffice/orders`
- **Método:** `GET`
- **Acceso:** `DEPOSITO`, `ADMIN`
- **Descripción:** Retorna todos los pedidos del sistema.

### Detalle de cualquier pedido
- **URL:** `/backoffice/orders/{order_id}`
- **Método:** `GET`
- **Acceso:** `DEPOSITO`, `ADMIN`
- **Descripción:** Retorna el detalle de cualquier pedido del sistema.

### Cambiar estado de un pedido
- **URL:** `/backoffice/orders/{order_id}/estado`
- **Método:** `PATCH`
- **Acceso:** `DEPOSITO`, `ADMIN`
- **Descripción:** Avanza el estado de un pedido a través del flujo de gestión.

---

## Salud (Health)
- **URL:** `/health`
- **Método:** `GET`
- **Acceso:** Público
- **Descripción:** Verificación del estado de la API.
