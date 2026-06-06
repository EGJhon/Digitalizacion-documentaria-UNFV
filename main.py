from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from database import engine, Base
import models
import router_generacion
import router_extraccion
import router_auth

# Crear las tablas del DB
Base.metadata.create_all(bind=engine)

# Asegurar los directorios
os.makedirs("documentos_generados", exist_ok=True)
os.makedirs("static", exist_ok=True)

app = FastAPI(title="API Módulo de Digitalización UNFV")

# Integrar los Routers
app.include_router(router_auth.router)
app.include_router(router_generacion.router)
app.include_router(router_extraccion.router)

# Montar frontend
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/documentos", StaticFiles(directory="documentos_generados"), name="documentos")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
