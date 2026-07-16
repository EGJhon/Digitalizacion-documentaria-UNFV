from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
import schemas, models
from database import get_db
import bcrypt
import os

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/login")
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
        
    return {"mensaje": "Login exitoso", "token": "mock-jwt-token", "role_id": user.role_id, "username": user.username}
