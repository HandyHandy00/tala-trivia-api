from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos SQLite
# Usé SQLite porque es simple y no necesita servidor separado
SQLALCHEMY_DATABASE_URL = "sqlite:///./tala_trivia.db"

# Crear el engine para conectarse a la BD
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necesario para SQLite con FastAPI
)

# Crear la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Función para obtener la sesión de BD en cada request
# La encontré en la documentación de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  # Siempre cerrar la conexión

