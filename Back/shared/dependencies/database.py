from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from shared.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # reconecta si MySQL cierra la conexión
    pool_recycle=3600,    # recicla conexiones cada 1 hora
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
