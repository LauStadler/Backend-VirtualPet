# Infraestructura de Tests - Virtual Pet Backend

Esta carpeta contiene la suite de pruebas automatizadas para el backend de Virtual Pet. Se utiliza **pytest** como framework principal y **FastAPI TestClient** para las pruebas de integración.

## Arquitectura de Pruebas

Para garantizar que los tests sean rápidos, deterministas y no afecten los datos de desarrollo, hemos implementado la siguiente estrategia:

1.  **Base de Datos en Memoria**: Los tests utilizan una base de datos **SQLite en memoria** (`sqlite:///:memory:`). Cada vez que ejecutas los tests, la DB se crea de cero y se destruye al finalizar.
2.  **Transaccionalidad**: Cada test se ejecuta dentro de una transacción de base de datos que se revierte (*rollback*) al terminar. Esto asegura que un test no deje "basura" para el siguiente.
3.  **Aislamiento**: Se sobreescriben las dependencias de FastAPI (vía `app.dependency_overrides`) para inyectar la sesión de base de datos de prueba en los controladores.

## Estructura de Archivos

-   **`conftest.py`**: Configuración global. Define las fixtures principales:
    -   `db_session`: Provee una sesión de DB limpia.
    -   `client`: Cliente HTTP para probar endpoints públicos.
    -   `auth_client`: Cliente autenticado como usuario **CLIENTE**.
    -   `admin_client`: Cliente autenticado como usuario **ADMIN**.
-   **`test_main.py`**: Verificaciones de integridad básica (Health Check).
-   **`test_auth_*`**: Pruebas de registro, login y seguridad de tokens.
-   **`test_catalog_*`**: Pruebas de productos, categorías y stock.
-   **`test_sales_*`**: Pruebas del proceso de checkout y validación de carrito.
-   **`test_orders_*`**: Pruebas del historial de pedidos y detalle para clientes.
-   **`test_backoffice_*`**: Pruebas de gestión administrativa y flujo de estados.
-   **`test_payments_*`**: Pruebas de la lógica de procesamiento de pagos.

## Cómo ejecutar los tests

Asegúrate de estar en la carpeta `Back/` y tener instaladas las dependencias de desarrollo.

### Ejecutar todos los tests
```powershell
pytest
```

### Ejecutar un archivo específico
```powershell
pytest tests/test_auth_controller.py
```

### Ejecutar y ver la salida detallada (verbose)
```powershell
pytest -v
```

### Ejecutar tests que fallaron en la última sesión
```powershell
pytest --lf
```

## Guía para agregar nuevos tests

1.  **Nombre**: El archivo debe empezar con `test_` (ej: `test_mi_modulo.py`).
2.  **Funciones**: Las funciones de test deben empezar con `test_`.
3.  **Fixtures**: Solicita `client`, `auth_client` o `db_session` como argumentos de tu función según lo necesites.
4.  **Asserts**: Usa `assert` de Python para verificar los resultados.

Ejemplo rápido:
```python
def test_mi_nuevo_endpoint(auth_client):
    client, user = auth_client
    response = client.get("/mi-ruta")
    assert response.status_code == 200
```
