import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from modules.catalog.models.product import Product
from modules.catalog.models.category import Category
from modules.catalog.models.stock import Stock
from infrastructure.storage.s3_service import S3Service
from shared.config.settings import settings

def upload_and_sync():
    engine = create_engine(settings.DATABASE_URL)
    s3 = S3Service()
    
    assets_path = os.path.join(os.getcwd(), "assets", "products")
    if not os.path.exists(assets_path):
        print(f"Error: No se encontro la carpeta {assets_path}")
        return

    files = os.listdir(assets_path)
    image_map = {} # nombre_sin_extension -> filename
    
    for f in files:
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            name_key = os.path.splitext(f)[0].lower().strip()
            image_map[name_key] = f

    with Session(engine) as session:
        products = session.scalars(select(Product)).all()
        
        print(f"\nSincronizando {len(products)} productos con S3...\n")
        
        for p in products:
            prod_name_key = p.nombre.lower().strip()
            filename = None
            
            # Intentar match exacto
            if prod_name_key in image_map:
                filename = image_map[prod_name_key]
            else:
                # Intentar match parcial
                for img_key, fname in image_map.items():
                    if img_key in prod_name_key or prod_name_key in img_key:
                        filename = fname
                        break
            
            if filename:
                full_path = os.path.join(assets_path, filename)
                with open(full_path, "rb") as f:
                    file_data = f.read()
                
                # Subir a S3
                # Usar settings.CLOUDFRONT_DOMAIN si existe, sino URL de S3 directa
                try:
                    import urllib.parse
                    safe_filename = urllib.parse.quote(filename)
                    
                    # En el s3_service.py ya concatena con CLOUDFRONT_DOMAIN
                    # Si CLOUDFRONT_DOMAIN esta vacio, fallaria la URL final del service
                    # Vamos a asegurarnos de que la URL sea valida
                    if not settings.CLOUDFRONT_DOMAIN:
                        # URL directa de S3 como fallback
                        s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/products/{safe_filename}"
                        # Sobreescribir el put_object manual para usar el prefijo products/
                        s3.client.put_object(
                            Bucket=settings.S3_BUCKET_NAME,
                            Key=f"products/{filename}",
                            Body=file_data,
                            ContentType="image/jpeg"
                        )
                        p.imagen_url = s3_url
                    else:
                        # Si hay cloudfront, el service lo hace
                        url = s3.subir_imagen(file_data, f"products/{filename}")
                        # Asegurar que la URL de salida tambien este encodeada si viene de un service que no lo hace
                        if settings.CLOUDFRONT_DOMAIN in url and filename in url:
                             url = url.replace(filename, safe_filename)
                        p.imagen_url = url
                    
                    print(f"[OK] {p.nombre} -> {p.imagen_url}")
                except Exception as e:
                    print(f"[ERROR] Subiendo {filename}: {str(e)}")
            else:
                print(f"[SKIP] {p.nombre} (No se encontro imagen)")
        
        session.commit()
        print("\nSincronizacion completada.")

if __name__ == "__main__":
    upload_and_sync()
