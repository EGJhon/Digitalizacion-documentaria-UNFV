from fastapi import APIRouter, HTTPException, status
import schemas
import os

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)

# Definir credenciales de administrador usando variables de entorno
ADMIN_USERNAME = os.getenv("APP_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("APP_ADMIN_PASSWORD", "admin123")

@router.post("/login")
def login(user_in: schemas.UserLogin):
    # Lógica básica temporal. En producción usar Hashing e integración con DB.
    if user_in.username == ADMIN_USERNAME and user_in.password == ADMIN_PASSWORD:
        return {"mensaje": "Login exitoso", "token": "mock-jwt-token"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
