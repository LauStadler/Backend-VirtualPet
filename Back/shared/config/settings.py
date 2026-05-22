from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Virtual Pet API"
    DEBUG: bool = True

    # MySQL
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/virtualpet"

    # JWT
    SECRET_KEY: str = "cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24hs

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173","http://localhost:5174","http://localhost:3000"]

    # AWS S3 (imágenes — configurar cuando corresponda)
    AWS_REGION: str = "sa-east-1"
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = "virtual-pet-productos"
    CLOUDFRONT_DOMAIN: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
