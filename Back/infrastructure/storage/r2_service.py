import boto3
from shared.config.settings import settings

class R2Service:
    """
    Servicio para Cloudflare R2.
    Utiliza la API compatible con S3 de boto3.
    """
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY,
            aws_secret_access_key=settings.R2_SECRET_KEY,
            region_name="auto",  # R2 no usa regiones tradicionales
        )

    def subir_imagen(self, archivo: bytes, nombre: str) -> str:
        """
        Sube una imagen a Cloudflare R2 y devuelve su URL pública.
        """
        self.client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=nombre,
            Body=archivo,
            ContentType="image/jpeg",
        )
        # R2 suele usarse con un dominio personalizado o el dominio de worker
        return f"{settings.R2_PUBLIC_URL}/{nombre}"
