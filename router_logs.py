from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_admin_user
import models

router = APIRouter(
    prefix="/api/v1/auditoria",
    tags=["Auditoría"]
)

from typing import Optional
from datetime import datetime

@router.get("/logs")
def obtener_logs(
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_admin_user)
):
    try:
        query = db.query(models.LogAuditoria, models.User).outerjoin(
            models.User, models.LogAuditoria.usuario_id == models.User.id
        )
        
        if fecha_inicio:
            try:
                dt_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                query = query.filter(models.LogAuditoria.fecha_accion >= dt_inicio)
            except ValueError:
                pass
                
        if fecha_fin:
            try:
                dt_fin = datetime.strptime(fecha_fin + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                query = query.filter(models.LogAuditoria.fecha_accion <= dt_fin)
            except ValueError:
                pass
            
        logs = query.order_by(models.LogAuditoria.fecha_accion.desc()).all()
        
        resultados = []
        for log, user in logs:
            resultados.append({
                "id": log.id,
                "fecha_accion": log.fecha_accion.strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": user.username if user else "Sistema/Desconocido",
                "accion": log.accion,
                "modulo": log.modulo,
                "detalles": log.detalles
            })
            
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener logs: {str(e)}")
