from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
       env_file=".env",
       extra="ignore"
    )
    APP_NAME: str = "Virtual Pet API"
    DEBUG: bool = True

    # MySQL
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/virtualpet"

    # JWT
    SECRET_KEY: str = "cambiar_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24hs

    # CORS
    # IMPORTANTE: Cambia List[str] por Union[List[str], str] para que el .env sea más flexible
    ALLOWED_ORIGINS: Union[List[str], str] =  ["http://localhost:5173","http://localhost:5174","http://localhost:3000"]
   
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
   
    # AWS S3 (imágenes)
        AWS_REGION: str = "sa-east-1"
        AWS_ACCESS_KEY: str = ""
        AWS_SECRET_KEY: str = ""
        S3_BUCKET_NAME: str = "virtual-pet-productos"
        CLOUDFRONT_DOMAIN: str = ""
    
    # Cloudflare R2 (Imagenes)
    R2_ENDPOINT_URL: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET_NAME: str = "virtual-pet-backup"
    R2_PUBLIC_URL: str = ""
   

settings = Settings()
