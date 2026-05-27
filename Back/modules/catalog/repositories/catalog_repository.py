"""
Repositorio del catálogo de productos.

Centraliza todas las queries a las tablas 'products', 'categories' y 'stock'.
Al ser un módulo de solo lectura desde la API, todas las operaciones aquí
son SELECT — el ERP escribe directamente en MySQL.

La única excepción es descontar_stock(), que es llamada internamente
por el módulo de orders al confirmar una compra, nunca por un endpoint HTTP.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_, text
from typing import Optional

from modules.catalog.models.product import Product
from modules.catalog.models.category import Category
from modules.catalog.models.stock import Stock


class CatalogRepository:
    """Acceso a datos para productos, categorías y stock."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión activa de SQLAlchemy inyectada por FastAPI.
        """
        self.db = db

    # ── Productos ──────────────────────────────────────────────────────────────

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por ID incluyendo su categoría y stock en una sola query.
        Usa joinedload para evitar el problema N+1 al acceder a las relaciones.

        Args:
            product_id: ID del producto a buscar.

        Returns:
            El producto con category y stock cargados, o None si no existe.
        """
        stmt = (
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.stock),
            )
            .where(Product.id == product_id, Product.activo == True)
        )
        return self.db.scalar(stmt)

    def list_products(
        self,
        busqueda: Optional[str] = None,
        categoria_id: Optional[int] = None,
        solo_con_stock: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Product], int]:
        """
        Lista productos activos con filtros opcionales y paginación optimizada.

        Optimizaciones aplicadas:
        1. Query de conteo directa: Evita subqueries pesadas.
        2. Carga selectiva (Joinedload): Resuelve N+1 para stock en una sola query.
        3. Index-friendly filtering: Uso de joins eficientes.
        """
        # Base de la query
        stmt = select(Product).where(Product.activo == True)

        # Filtro de búsqueda por texto (Optimizado con Full-Text Index en MySQL y modo booleano para prefijos)
        if busqueda:
            # Transformamos la búsqueda para que cada palabra sea obligatoria (+) y permita prefijos (*)
            # Ej: "alimen perr" -> "+alimen* +perr*"
            terminos_booleanos = " ".join([f"+{word}*" for word in busqueda.split() if len(word) > 0])
            
            # Usamos el operador AGAINST nativo de MySQL con modo booleano
            match_clause = func.match(Product.nombre, Product.descripcion).op("AGAINST")(
                text(f"('{terminos_booleanos}' IN BOOLEAN MODE)")
            )
            
            stmt = stmt.where(match_clause)

        # Filtro por categoría con expansión de hijos
        if categoria_id:
            # Obtenemos IDs de categorías hijas para búsqueda jerárquica
            # Nota: Para 2000 productos, este enfoque es rápido. 
            # Si creciera a millones, se usaría un índice de 'path' o CTE.
            child_ids = self.db.scalars(
                select(Category.id).where(Category.parent_id == categoria_id)
            ).all()
            all_category_ids = [categoria_id] + list(child_ids)
            stmt = stmt.where(Product.category_id.in_(all_category_ids))

        # Filtro de stock: Join eficiente
        if solo_con_stock:
            stmt = stmt.join(Product.stock).where(Stock.cantidad > 0)

        # 1. Conteo total (Query independiente para evitar colisiones de joins/aliases)
        count_stmt = select(func.count(Product.id)).where(Product.activo == True)
        if busqueda:
            match_clause_count = func.match(Product.nombre, Product.descripcion).op("AGAINST")(
                text(f"('{terminos_booleanos}' IN BOOLEAN MODE)")
            )
            count_stmt = count_stmt.where(match_clause_count)
        if categoria_id:
            count_stmt = count_stmt.where(Product.category_id.in_(all_category_ids))
        if solo_con_stock:
            count_stmt = count_stmt.join(Product.stock).where(Stock.cantidad > 0)

        total = self.db.scalar(count_stmt) or 0

        # 2. Paginación y Carga de Relaciones
        offset = (page - 1) * page_size
        stmt = (
            stmt.options(joinedload(Product.stock))
            .order_by(Product.nombre.asc())
            .offset(offset)
            .limit(page_size)
        )

        products = list(self.db.scalars(stmt).unique())
        return products, total

    # ── Categorías ────────────────────────────────────────────────────────────

    def list_categories(self) -> list[Category]:
        """
        Retorna todas las categorías ordenadas por nombre.
        Usado para poblar el filtro de categorías en el frontend.

        Returns:
            Lista de todas las categorías disponibles.
        """
        stmt = select(Category).order_by(Category.nombre)
        return list(self.db.scalars(stmt))

    # ── Stock ─────────────────────────────────────────────────────────────────

    def get_stock(self, product_id: int) -> Optional[Stock]:
        """
        Obtiene el registro de stock de un producto específico.

        Args:
            product_id: ID del producto a consultar.

        Returns:
            El objeto Stock, o None si el producto no tiene registro de stock.
        """
        stmt = select(Stock).where(Stock.product_id == product_id)
        return self.db.scalar(stmt)

    def get_stock_for_update(self, product_id: int) -> Optional[Stock]:
        """
        Obtiene el registro de stock con un bloqueo pesimista (SELECT FOR UPDATE).
        Esto evita que otros procesos modifiquen el stock hasta que la
        transacción actual termine (commit o rollback).

        Args:
            product_id: ID del producto a bloquear.

        Returns:
            El objeto Stock bloqueado, o None si no existe.
        """
        stmt = (
            select(Stock)
            .where(Stock.product_id == product_id)
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def hay_stock_suficiente(self, product_id: int, cantidad: int) -> bool:
        """
        Verifica si hay suficiente stock para satisfacer una cantidad pedida.
        No usa bloqueo ya que es solo para verificación previa al checkout.
        """
        stock = self.get_stock(product_id)
        if stock is None:
            return False
        return stock.cantidad >= cantidad

    def descontar_stock(self, product_id: int, cantidad: int) -> Stock:
        """
        Descuenta unidades del stock al confirmar una compra.

        IMPORTANTE: Ya no hace commit(). La transacción debe ser gestionada
        externamente (ej: en OrderService).

        Args:
            product_id: ID del producto a descontar.
            cantidad: Unidades a restar del stock.

        Returns:
            El objeto Stock actualizado.

        Raises:
            ValueError: Si no existe registro de stock para el producto.
        """
        # Obtenemos el stock con bloqueo para asegurar integridad
        stock = self.get_stock_for_update(product_id)
        if stock is None:
            raise ValueError(
                f"No existe registro de stock para el producto {product_id}."
            )

        if stock.cantidad < cantidad:
            from modules.catalog.services.catalog_service import StockInsuficienteError
            raise StockInsuficienteError(
                product_id=product_id,
                disponible=stock.cantidad,
                solicitado=cantidad
            )

        stock.cantidad -= cantidad
        self.db.flush()
        return stock
