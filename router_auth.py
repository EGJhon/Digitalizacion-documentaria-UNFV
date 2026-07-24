from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
import schemas, models
from database import get_db
import bcrypt
import os
from security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/login")
def login(request: Request, user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    client_ip = request.client.host if request.client else "Desconocida"
    
    if not user or not verify_password(user_in.password, user.password_hash):
        log = models.LogAuditoria(
            usuario_id=user.id if user else None,
            accion="LOGIN_FALLIDO",
            modulo="AUTH",
            detalles=f"Intento de inicio de sesión fallido para el usuario: {user_in.username} desde la IP: {client_ip}"
        )
        db.add(log)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
        
    log = models.LogAuditoria(
        usuario_id=user.id,
        accion="LOGIN",
        modulo="AUTH",
        detalles=f"El usuario {user.username} inició sesión en el sistema desde la IP: {client_ip}"
    )
    db.add(log)
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role_id": user.role_id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return {"mensaje": "Login exitoso", "token": access_token, "role_id": user.role_id, "username": user.username, "user_id": user.id}
