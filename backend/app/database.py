from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Construcción de la cadena de conexión para SQL Server
DATABASE_URL = (
    f"mssql+pyodbc://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_SERVER}/{settings.DB_NAME}"
    f"?driver={settings.DB_DRIVER.replace(' ', '+')}"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,           # True para ver SQL en consola (debug)
    pool_pre_ping=True,   # Verifica conexión antes de usarla
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para inyectar sesión en los routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()