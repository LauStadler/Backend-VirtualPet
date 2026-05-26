import logging
from infrastructure.storage.s3_service import S3Service
from infrastructure.storage.r2_service import R2Service

   # Configuramos un logger para avisar si algo falla
logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
       self.s3 = S3Service()
       self.r2 = R2Service()

    def subir_imagen(self, archivo: bytes, nombre: str) -> str:
       """          
       Intenta subir la imagen a S3. Si falla, intenta con R2.
       """
       try:
           # Intento 1: Amazon S3 (Principal)
            logger.info(f"Intentando subir {nombre} a AWS S3...")
            return self.s3.subir_imagen(archivo, nombre)
       except Exception as e:
            # Si Amazon falla, registramos el error y vamos al Plan B
            logger.error(f"Fallo en AWS S3: {str(e)}. Activando redundancia con Cloudflare R2...")
            
            try:
                # Intento 2: Cloudflare R2 (Backup)
                return self.r2.subir_imagen(archivo, nombre)
            except Exception as e_r2:
                # Si AMBOS fallan, ahí sí lanzamos un error total
                logger.critical(f"Fallo crítico: Ni S3 ni R2 están disponibles. Error: {str(e_r2)}")
                raise Exception("No se pudo subir la imagen a ningún proveedor de almacenamiento.")