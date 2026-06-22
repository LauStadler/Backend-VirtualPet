"""
Script de seed para poblar la base de datos de Virtual Pet con datos de prueba.

Simula los datos que el ERP externo cargaría en producción:
categorías, productos y stock inicial.

Uso:
    cd virtual-pet
    python -m infrastructure.db.seeds.seed

Requisitos:
    - La base de datos debe existir y estar vacía (o con tablas ya creadas).
    - Las variables de entorno deben estar configuradas en .env
    - Correr primero: alembic upgrade head
"""

import sys
import os

# Permite correr el script desde la raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from sqlalchemy.orm import Session
from shared.dependencies.database import SessionLocal
from modules.auth.models.user import User, UserRole
from modules.catalog.models.category import Category
from modules.catalog.models.product import Product
from modules.catalog.models.stock import Stock
from shared.utils.security import hash_password


# ── Datos de categorías ────────────────────────────────────────────────────────

CATEGORIAS = [
    {"nombre": "Alimentos",        "descripcion": "Alimentos secos, húmedos y snacks para todo tipo de mascotas"},
    {"nombre": "Juguetes",         "descripcion": "Juguetes interactivos y de entretenimiento"},
    {"nombre": "Accesorios",       "descripcion": "Collares, correas, ropa y complementos"},
    {"nombre": "Higiene",          "descripcion": "Shampoos, cepillos y productos de cuidado"},
    {"nombre": "Vivienda",         "descripcion": "Cuchas, camas, jaulas y transportines"},
    {"nombre": "Salud",            "descripcion": "Vitaminas, suplementos y antiparasitarios"},
]

SUBCATEGORIAS = [
    {"nombre": "Alimentos para perros", "descripcion": "Croquetas y húmedos para perros",          "parent": "Alimentos"},
    {"nombre": "Alimentos para gatos",  "descripcion": "Croquetas y húmedos para gatos",           "parent": "Alimentos"},
    {"nombre": "Alimentos para peces",  "descripcion": "Escamas, pellets y alimentos acuáticos",   "parent": "Alimentos"},
    {"nombre": "Alimentos para aves",   "descripcion": "Semillas y mezclas para pájaros",           "parent": "Alimentos"},
    {"nombre": "Cuchas y camas",        "descripcion": "Descanso cómodo para perros y gatos",      "parent": "Vivienda"},
    {"nombre": "Jaulas y acuarios",     "descripcion": "Hábitats para aves, roedores y peces",     "parent": "Vivienda"},
]


# ── Datos de productos ─────────────────────────────────────────────────────────

PRODUCTOS = [
    # Alimentos para perros
    {
        "nombre":      "Royal Canin Medium Adult 15kg",
        "descripcion": "Alimento completo para perros adultos de raza mediana. Formulado para mantener el peso ideal y la salud digestiva.",
        "precio":      28500.00,
        "categoria":   "Alimentos para perros",
        "erp_id":      "ERP-001",
        "stock":       45,
    },
    {
        "nombre":      "Eukanuba Adult Large Breed 14kg",
        "descripcion": "Croquetas para perros adultos de raza grande. Rica en proteínas de pollo para mantener la masa muscular.",
        "precio":      32000.00,
        "categoria":   "Alimentos para perros",
        "erp_id":      "ERP-002",
        "stock":       30,
    },
    {
        "nombre":      "Pedigree Adultos Carne y Verduras 21kg",
        "descripcion": "Alimento balanceado con carne y vegetales. Ideal para perros adultos de todas las razas.",
        "precio":      18900.00,
        "categoria":   "Alimentos para perros",
        "erp_id":      "ERP-003",
        "stock":       60,
    },
    {
        "nombre":      "Purina Pro Plan Cachorro 3kg",
        "descripcion": "Fórmula especial para cachorros con DHA para el desarrollo cerebral. Proteína de pollo como primer ingrediente.",
        "precio":      9800.00,
        "categoria":   "Alimentos para perros",
        "erp_id":      "ERP-004",
        "stock":       25,
    },

    # Alimentos para gatos
    {
        "nombre":      "Whiskas Adultos Pollo y Conejo 10kg",
        "descripcion": "Croquetas para gatos adultos con sabor a pollo y conejo. Enriquecidas con taurina para la salud cardiovascular.",
        "precio":      14500.00,
        "categoria":   "Alimentos para gatos",
        "erp_id":      "ERP-005",
        "stock":       40,
    },
    {
        "nombre":      "Royal Canin Indoor 7 4kg",
        "descripcion": "Especial para gatos de interior. Controla la formación de bolas de pelo y mantiene el peso ideal.",
        "precio":      16200.00,
        "categoria":   "Alimentos para gatos",
        "erp_id":      "ERP-006",
        "stock":       20,
    },
    {
        "nombre":      "Hills Science Diet Gatito 1.6kg",
        "descripcion": "Alimento premium para gatitos hasta 12 meses. Nutrición precisa para un desarrollo saludable.",
        "precio":      11400.00,
        "categoria":   "Alimentos para gatos",
        "erp_id":      "ERP-007",
        "stock":       15,
    },

    # Alimentos para peces
    {
        "nombre":      "Tetra Goldfish Granules 250ml",
        "descripcion": "Gránulos flotantes para peces dorados y carpas koi. Fórmula especial para reducir la contaminación del agua.",
        "precio":      2800.00,
        "categoria":   "Alimentos para peces",
        "erp_id":      "ERP-008",
        "stock":       80,
    },
    {
        "nombre":      "Sera Vipan Nature 1000ml",
        "descripcion": "Escamas naturales para peces tropicales. Sin colorantes artificiales, ingredientes 100% naturales.",
        "precio":      4200.00,
        "categoria":   "Alimentos para peces",
        "erp_id":      "ERP-009",
        "stock":       50,
    },

    # Alimentos para aves
    {
        "nombre":      "Vitakraft Menu Vital Canarios 1kg",
        "descripcion": "Mezcla de semillas seleccionadas para canarios. Enriquecida con vitaminas y minerales esenciales.",
        "precio":      3500.00,
        "categoria":   "Alimentos para aves",
        "erp_id":      "ERP-010",
        "stock":       35,
    },

    # Juguetes
    {
        "nombre":      "Kong Classic Rojo Talla M",
        "descripcion": "Juguete resistente de goma natural para perros. Se puede rellenar con premios para estimulación mental.",
        "precio":      6800.00,
        "categoria":   "Juguetes",
        "erp_id":      "ERP-011",
        "stock":       40,
    },
    {
        "nombre":      "Pluma interactiva para gatos con luz LED",
        "descripcion": "Varita con plumas naturales y puntero láser integrado. Estimula el instinto cazador del gato.",
        "precio":      1900.00,
        "categoria":   "Juguetes",
        "erp_id":      "ERP-012",
        "stock":       55,
    },
    {
        "nombre":      "Pelota tenis para perros pack x3",
        "descripcion": "Pelotas de tenis resistentes al mordido. Tamaño estándar, aptas para lanzadores automáticos.",
        "precio":      2400.00,
        "categoria":   "Juguetes",
        "erp_id":      "ERP-013",
        "stock":       70,
    },

    # Accesorios
    {
        "nombre":      "Correa retráctil Flexi Classic 5m Talla L",
        "descripcion": "Correa extensible hasta 5 metros para perros de hasta 50kg. Sistema de freno y bloqueo de seguridad.",
        "precio":      8900.00,
        "categoria":   "Accesorios",
        "erp_id":      "ERP-014",
        "stock":       22,
    },
    {
        "nombre":      "Collar antipulgas Seresto perros grandes",
        "descripcion": "Collar antiparasitario de larga duración (hasta 8 meses). Repele pulgas, garrapatas y mosquitos.",
        "precio":      12500.00,
        "categoria":   "Accesorios",
        "erp_id":      "ERP-015",
        "stock":       18,
    },

    # Higiene
    {
        "nombre":      "Shampoo Pelo de Oro Perros Pelaje Oscuro 500ml",
        "descripcion": "Shampoo específico para perros de pelaje oscuro. Realza el brillo y suaviza el pelo sin resecar.",
        "precio":      3200.00,
        "categoria":   "Higiene",
        "erp_id":      "ERP-016",
        "stock":       30,
    },
    {
        "nombre":      "Cepillo de cerdas dobles para gatos",
        "descripcion": "Doble cara: cerdas metálicas para desenredar y cerdas suaves para pulir el pelaje.",
        "precio":      2100.00,
        "categoria":   "Higiene",
        "erp_id":      "ERP-017",
        "stock":       45,
    },

    # Vivienda
    {
        "nombre":      "Cucha de madera para perros medianos",
        "descripcion": "Cucha de pino tratado para exterior e interior. Techo desmontable para fácil limpieza. 70x60x65cm.",
        "precio":      24000.00,
        "categoria":   "Cuchas y camas",
        "erp_id":      "ERP-018",
        "stock":       10,
    },
    {
        "nombre":      "Cama redonda antideslizante para mascotas",
        "descripcion": "Cama acolchada 60cm de diámetro. Relleno de espuma de alta densidad, base antideslizante. Lavable.",
        "precio":      7500.00,
        "categoria":   "Cuchas y camas",
        "erp_id":      "ERP-019",
        "stock":       28,
    },
    {
        "nombre":      "Acuario completo kit 60 litros",
        "descripcion": "Kit completo con filtro, iluminación LED y calefactor. Listo para usar. Incluye manual de inicio.",
        "precio":      35000.00,
        "categoria":   "Jaulas y acuarios",
        "erp_id":      "ERP-020",
        "stock":       5,
    },

    # Salud
    {
        "nombre":      "Frontline Combo perros 10-20kg x3 pipetas",
        "descripcion": "Antiparasitario externo spot-on. Elimina pulgas, garrapatas y piojos. Efecto residual 4 semanas.",
        "precio":      9200.00,
        "categoria":   "Salud",
        "erp_id":      "ERP-021",
        "stock":       33,
    },
    {
        "nombre":      "Suplemento articular Condro Plus para perros 60 comp",
        "descripcion": "Condroitina y glucosamina para la salud articular. Ideal para perros mayores o razas grandes.",
        "precio":      6700.00,
        "categoria":   "Salud",
        "erp_id":      "ERP-022",
        "stock":       20,
    },
]


# ── Usuarios de prueba ─────────────────────────────────────────────────────────

USUARIOS = [
    {
        "nombre":   "Admin",
        "apellido": "Virtual Pet",
        "email":    "admin@virtualpet.com.ar",
        "password": "Admin1234",
        "role":     UserRole.ADMIN,
    },
    {
        "nombre":   "Juan",
        "apellido": "Depósito",
        "email":    "deposito@virtualpet.com.ar",
        "password": "Deposito1234",
        "role":     UserRole.DEPOSITO,
    },
    {
        "nombre":   "María",
        "apellido": "González",
        "email":    "cliente@test.com",
        "password": "Cliente1234",
        "role":     UserRole.CLIENTE,
    },
    {
        "nombre":   "Juan",
        "apellido": "Delivery",
        "email":    "rider@virtualpet.com",
        "password": "rider123",
        "role":     UserRole.DELIVERY,
    },
]


# ── Funciones del seed ─────────────────────────────────────────────────────────

def seed_categorias(db: Session) -> dict[str, Category]:
    """
    Crea categorías padres y subcategorías.

    Returns:
        Diccionario {nombre: Category} para referenciar al crear productos.
    """
    print("\n📂 Creando categorías...")
    cat_map = {}

    # Primero las categorías raíz
    for data in CATEGORIAS:
        cat = Category(nombre=data["nombre"], descripcion=data["descripcion"])
        db.add(cat)
        db.flush()
        cat_map[data["nombre"]] = cat
        print(f"   ✓ {data['nombre']}")

    # Luego las subcategorías (necesitan el parent_id)
    for data in SUBCATEGORIAS:
        parent = cat_map.get(data["parent"])
        cat = Category(
            nombre=data["nombre"],
            descripcion=data["descripcion"],
            parent_id=parent.id if parent else None,
        )
        db.add(cat)
        db.flush()
        cat_map[data["nombre"]] = cat
        print(f"   ✓ {data['nombre']} (→ {data['parent']})")

    return cat_map


def seed_productos(db: Session, cat_map: dict[str, Category]) -> None:
    """Crea productos con su stock inicial."""
    print("\n🛍️  Creando productos y stock...")

    for data in PRODUCTOS:
        categoria = cat_map.get(data["categoria"])

        producto = Product(
            nombre=data["nombre"],
            descripcion=data["descripcion"],
            precio=data["precio"],
            category_id=categoria.id if categoria else None,
            erp_id=data["erp_id"],
            activo=True,
        )
        db.add(producto)
        db.flush()

        stock = Stock(product_id=producto.id, cantidad=data["stock"])
        db.add(stock)

        print(f"   ✓ {data['nombre'][:50]:<50} | ${data['precio']:>10,.0f} | stock: {data['stock']}")


def seed_usuarios(db: Session) -> None:
    """Crea usuarios de prueba para cada rol."""
    print("\n👤 Creando usuarios de prueba...")

    for data in USUARIOS:
        usuario = User(
            nombre=data["nombre"],
            apellido=data["apellido"],
            email=data["email"],
            password_hash=hash_password(data["password"]),
            role=data["role"],
        )
        db.add(usuario)
        print(f"   ✓ [{data['role'].value:>8}] {data['email']}  |  password: {data['password']}")


def run_seed() -> None:
    """Punto de entrada del seed. Verifica que la DB esté vacía antes de insertar."""
    db: Session = SessionLocal()

    try:
        # Verificar si ya hay datos para evitar duplicados
        if db.query(Product).count() > 0:
            print("⚠️  La base de datos ya tiene productos. Seed cancelado.")
            print("    Si querés reiniciar, borrá las tablas y corré: alembic upgrade head")
            return

        print("🌱 Iniciando seed de Virtual Pet...")

        cat_map = seed_categorias(db)
        seed_productos(db, cat_map)
        seed_usuarios(db)

        db.commit()

        print("\n✅ Seed completado exitosamente.")
        print(f"   • {len(CATEGORIAS) + len(SUBCATEGORIAS)} categorías")
        print(f"   • {len(PRODUCTOS)} productos")
        print(f"   • {len(USUARIOS)} usuarios")
        print("\n🔑 Credenciales de prueba:")
        for u in USUARIOS:
            print(f"   {u['email']}  /  {u['password']}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante el seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
