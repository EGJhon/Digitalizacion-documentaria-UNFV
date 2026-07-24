from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from database import engine, Base, SessionLocal
import models
import router_generacion
import router_extraccion
import router_auth
import router_users
import router_logs

# Crear las tablas del DB
Base.metadata.create_all(bind=engine)

# Asegurar los directorios
os.makedirs("documentos_generados", exist_ok=True)
os.makedirs("static", exist_ok=True)

app = FastAPI(title="API Módulo de Digitalización UNFV")

@app.on_event("startup")
def init_db():
    db = SessionLocal()
    try:
        admin_role = db.query(models.Role).filter(models.Role.nombre == "admin").first()
        if not admin_role:
            admin_role = models.Role(nombre="admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
        
        user_role = db.query(models.Role).filter(models.Role.nombre == "usuario").first()
        if not user_role:
            user_role = models.Role(nombre="usuario")
            db.add(user_role)
            db.commit()

        admin_username = os.getenv("APP_ADMIN_USERNAME", "admin")
        admin_user = db.query(models.User).filter(models.User.username == admin_username).first()
        if not admin_user:
            from router_users import get_password_hash
            pwd = os.getenv("APP_ADMIN_PASSWORD", "admin123")
            new_admin = models.User(
                username=admin_username,
                password_hash=get_password_hash(pwd),
                role_id=admin_role.id
            )
            db.add(new_admin)
            db.commit()
    finally:
        db.close()

# Integrar los Routers
app.include_router(router_auth.router)
app.include_router(router_users.router)
app.include_router(router_generacion.router)
app.include_router(router_extraccion.router)
app.include_router(router_logs.router)

# Montar frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
