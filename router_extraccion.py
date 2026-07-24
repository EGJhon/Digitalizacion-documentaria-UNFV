from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from services.ocr_service import extraer_datos_oficio, extraer_datos_resolucion
import models
from database import get_db
from dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/extraer",
    tags=["Extracción OCR"]
)

@router.post("/oficio")
async def extraer_oficio(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Validar que sea imagen o PDF
    if not (archivo.content_type.startswith("image/") or archivo.content_type == "application/pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (PNG/JPG) o un documento PDF")
    
    try:
        contenido = await archivo.read()
        datos = extraer_datos_oficio(contenido, archivo.filename)
        
        # Log Auditoría
        log = models.LogAuditoria(
            usuario_id=current_user.id,
            accion="EXTRAER",
            modulo="OCR",
            detalles=f"Se extrajo información del archivo: {archivo.filename}"
        )
        db.add(log)
        db.commit()
            
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en OCR: {str(e)}")


@router.post("/resolucion")
async def extraer_resolucion(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not (archivo.content_type.startswith("image/") or archivo.content_type == "application/pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (PNG/JPG) o un documento PDF")
    
    try:
        contenido = await archivo.read()
        datos = extraer_datos_resolucion(contenido, archivo.filename)
        
        log = models.LogAuditoria(
            usuario_id=current_user.id,
            accion="EXTRAER",
            modulo="OCR",
            detalles=f"Se extrajo información (resolucion) del archivo: {archivo.filename}"
        )
        db.add(log)
        db.commit()
            
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en OCR: {str(e)}")
