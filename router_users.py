from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import bcrypt
import models, schemas
from database import get_db

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Usuarios y Roles"]
)

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

@router.get("/roles", response_model=List[schemas.RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Role).all()
    return roles

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    db_role = db.query(models.Role).filter(models.Role.id == user_in.role_id).first()
    if not db_role:
        raise HTTPException(status_code=400, detail="El rol especificado no existe")

    hashed_password = get_password_hash(user_in.password)
    new_user = models.User(
        username=user_in.username,
        password_hash=hashed_password,
        role_id=user_in.role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.put("/password")
def change_password(data: schemas.UserChangePassword, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if not bcrypt.checkpw(data.old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
        
    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"mensaje": "Contraseña actualizada exitosamente"}
