import boto3
from shared.config.settings import settings

class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
        )

    def subir_imagen(self, archivo: bytes, nombre: str) -> str:
        self.client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=nombre,
            Body=archivo,
            ContentType="image/jpeg",
        )
        return f"https://{settings.CLOUDFRONT_DOMAIN}/{nombre}"
