from pydantic import BaseModel, Field

class OficioCreate(BaseModel):
    lema_anio: str | None = None
    lugar_fecha: str | None = None
    nro_oficio: str = Field(..., min_length=1)
    destinatario_titulo: str | None = None
    destinatario_nombre: str | None = None
    destinatario_cargo: str | None = None
    destinatario_dependencia: str | None = None
    asunto: str = Field(..., min_length=1)
    referencia: str | None = None
    cuerpo_mensaje: str = Field(..., min_length=1)
    remitente_nombre: str = Field(..., min_length=1)
    nt: str | None = None
    folios: str | None = None
    copia: str | None = None
    usuario_id: int | None = None

class ResolucionCreate(BaseModel):
    nro_resolucion: str = Field(..., min_length=1)
    lema_anio: str | None = None
    lugar_fecha: str | None = None
    vistos_texto: str | None = None
    considerandos: str = Field(..., min_length=1)
    parrafo_previo_resuelve: str | None = None
    articulos: str = Field(..., min_length=1)
    texto_cierre: str | None = None
    secretario_nombre: str | None = None
    rectora_nombre: str | None = None

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class RoleResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    role_id: int

class UserResponse(BaseModel):
    id: int
    username: str
    role_id: int

    class Config:
        from_attributes = True

class UserChangePassword(BaseModel):
    username: str
    old_password: str
    new_password: str = Field(..., min_length=1)
