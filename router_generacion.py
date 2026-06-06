from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import models
import schemas
from database import get_db
from services import pdf_service

router = APIRouter(
    prefix="/api/v1/generar",
    tags=["Generación de Documentos"]
)

@router.post("/oficio", status_code=status.HTTP_201_CREATED)
def generar_oficio(oficio_in: schemas.OficioCreate, db: Session = Depends(get_db)):
    try:
        # 1 & 2. Iniciar transacción (manejado por session de sqlalchemy) e insertar Documento Maestro
        codigo_unico = str(uuid.uuid4())
        nuevo_maestro = models.DocumentoMaestro(
            codigo_unico=codigo_unico,
            tipo_documento=models.TipoDocumento.oficio
        )
        db.add(nuevo_maestro)
        db.flush() # Para obtener el ID generado sin hacer commit aún

        # 3. Insertar datos en Campos_Oficio
        nuevo_oficio = models.CamposOficio(
            maestro_id=nuevo_maestro.id,
            lema_anio=oficio_in.lema_anio,
            lugar_fecha=oficio_in.lugar_fecha,
            nro_oficio=oficio_in.nro_oficio,
            destinatario_titulo=oficio_in.destinatario_titulo,
            destinatario_nombre=oficio_in.destinatario_nombre,
            destinatario_cargo=oficio_in.destinatario_cargo,
            destinatario_dependencia=oficio_in.destinatario_dependencia,
            asunto=oficio_in.asunto,
            referencia=oficio_in.referencia,
            cuerpo_mensaje=oficio_in.cuerpo_mensaje,
            remitente_nombre=oficio_in.remitente_nombre,
            nt=oficio_in.nt,
            folios=oficio_in.folios,
            copia=oficio_in.copia
        )
        db.add(nuevo_oficio)
        db.flush() # flush para tener el registro completo antes del PDF

        # 4. Generar el PDF físico delegando al dispatcher
        datos_dict = oficio_in.model_dump()
        ruta_pdf = pdf_service.generar_pdf("oficio", datos_dict, nuevo_maestro.id)
        nuevo_maestro.ruta_pdf_final = ruta_pdf

        # 4. Hacer commit
        db.commit()
        db.refresh(nuevo_maestro)

        # 5. Retornar JSON
        return {
            "mensaje": "Oficio generado correctamente",
            "id_maestro": nuevo_maestro.id,
            "codigo_unico": nuevo_maestro.codigo_unico,
            "pdf_url": f"/documentos/{nuevo_maestro.id}" # Ruta mock para descargar
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al generar documento: {str(e)}")

@router.get("/oficios")
def obtener_oficios(db: Session = Depends(get_db)):
    try:
        # Obtener todos los oficios mediante un JOIN con el DocumentoMaestro
        oficios = db.query(models.CamposOficio, models.DocumentoMaestro).join(
            models.DocumentoMaestro, 
            models.CamposOficio.maestro_id == models.DocumentoMaestro.id
        ).all()
        
        resultados = []
        for campos, maestro in oficios:
            resultados.append({
                "id_maestro": maestro.id,
                "codigo_unico": maestro.codigo_unico,
                "nro_oficio": campos.nro_oficio,
                "fecha_registro": maestro.fecha_registro.strftime("%Y-%m-%d %H:%M:%S"),
                "destinatario": campos.destinatario_nombre,
                "asunto": campos.asunto,
                "estado": maestro.estado,
                "pdf_url": f"/documentos/oficio_{maestro.id}.pdf"
            })
            
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")
