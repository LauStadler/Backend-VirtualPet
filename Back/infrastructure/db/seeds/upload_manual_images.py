
import os
import sys
import boto3
import mimetypes
from sqlalchemy.orm import Session

# Añadir el path para encontrar los módulos
sys.path.append(os.getcwd())
import infrastructure.db.base 

from shared.dependencies.database import SessionLocal
from modules.catalog.models.product import Product
from shared.config.settings import settings

def upload_local_images(images_folder: str = "assets/products"):
    """
    Sube imágenes de una carpeta local a S3 y actualiza la base de datos.
    Espera que las imágenes tengan el mismo nombre que el producto en la DB.
    Ejemplo: 'Royal Canin Medium Adult 15kg.jpg'
    """
    
    # 1. Verificar si la carpeta existe
    if not os.path.exists(images_folder):
        print(f"❌ Error: La carpeta '{images_folder}' no existe.")
        print("   Por favor, crea la carpeta y coloca allí tus imágenes.")
        return

    # 2. Inicializar DB y S3
    db: Session = SessionLocal()
    s3_client = boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
    )

    print(f"🚀 Iniciando carga manual desde '{images_folder}' hacia S3...")
    
    # Obtener todos los productos para hacer match fácilmente (ignorando mayúsculas)
    productos_db = db.query(Product).all()
    # Diccionario: {"royal canin medium adult 15kg": ProductoObj}
    productos_dict = {p.nombre.lower(): p for p in productos_db}

    archivos_procesados = 0
    archivos_ignorados = 0

    try:
        # 3. Iterar sobre las imágenes de la carpeta
        for filename in os.listdir(images_folder):
            filepath = os.path.join(images_folder, filename)
            
            # Ignorar si no es archivo (ej. subcarpetas)
            if not os.path.isfile(filepath):
                continue

            # Obtener el nombre del producto quitando la extensión (.jpg, .png, etc)
            nombre_sin_ext = os.path.splitext(filename)[0]
            nombre_limpio = nombre_sin_ext.lower().strip()

            # Buscar si el nombre de la imagen coincide con un producto
            producto = productos_dict.get(nombre_limpio)

            if producto:
                print(f"📸 Procesando: {filename} -> Match con ID: {producto.id}")
                
                # Adivinar el tipo de contenido (image/jpeg, image/png)
                content_type, _ = mimetypes.guess_type(filepath)
                if not content_type:
                    content_type = "image/jpeg" # fallback
                
                try:
                    # Subir a S3
                    s3_key = f"products/prod_{producto.id}_{filename.replace(' ', '_')}"
                    
                    with open(filepath, "rb") as data:
                        s3_client.put_object(
                            Bucket=settings.S3_BUCKET_NAME,
                            Key=s3_key,
                            Body=data,
                            ContentType=content_type,
                            ACL="public-read"
                        )
                    
                    # Generar URL pública y guardar en DB
                    s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
                    producto.imagen_url = s3_url
                    db.commit()
                    print(f"   ✅ Subido exitosamente: {s3_url}")
                    archivos_procesados += 1
                    
                except Exception as e:
                    print(f"   ❌ Error subiendo {filename}: {e}")
            else:
                print(f"   ⚠️ Ignorado: '{filename}' (No se encontró un producto con el nombre '{nombre_sin_ext}')")
                archivos_ignorados += 1

        print(f"\n✨ Proceso finalizado.")
        print(f"   - Imágenes subidas y vinculadas: {archivos_procesados}")
        print(f"   - Imágenes sin producto asociado: {archivos_ignorados}")

    finally:
        db.close()

if __name__ == "__main__":
    # La carpeta por defecto donde debes poner las fotos
    carpeta = "assets/products"
    upload_local_images(carpeta)
