import os
import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración Base de Datos
db_server = os.getenv("DB_SERVER")
if db_server:
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME")
    
    # Construir la URL escapando correctamente los caracteres especiales en la contraseña
    params = urllib.parse.quote_plus(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_password};TrustServerCertificate=yes;")
    SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"
else:
    # Fallback a SQLite si no hay DB_SERVER configurado
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./digitalizacion.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
