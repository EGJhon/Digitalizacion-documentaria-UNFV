from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, Form, File
from fastapi.responses import HTMLResponse, FileResponse
import os
from typing import Optional
from sqlalchemy.orm import Session
import uuid
import models
import schemas
from database import get_db
from dependencies import get_current_user
from services import pdf_service

router = APIRouter(
    prefix="/api/v1/generar",
    tags=["Generación de Documentos"]
)

@router.post("/oficio/preview", response_class=HTMLResponse)
def previsualizar_oficio(oficio_in: schemas.OficioCreate, current_user: models.User = Depends(get_current_user)):
    try:
        datos_dict = oficio_in.model_dump()
        html_content = pdf_service.generar_html_preview("oficio", datos_dict)
        return html_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al previsualizar documento: {str(e)}")

@router.post("/oficio", status_code=status.HTTP_201_CREATED)
def generar_oficio(oficio_in: schemas.OficioCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        # 1 & 2. Iniciar transacción (manejado por session de sqlalchemy) e insertar Documento Maestro
        codigo_unico = str(uuid.uuid4())
        nuevo_maestro = models.DocumentoMaestro(
            codigo_unico=codigo_unico,
            tipo_documento=models.TipoDocumento.oficio,
            usuario_id=current_user.id
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
        
        # 5. Guardar log de auditoría
        log = models.LogAuditoria(
            usuario_id=current_user.id,
            accion="CREAR",
            modulo="OFICIOS",
            detalles=f"Se registró un nuevo documento (Cód: {nuevo_maestro.codigo_unico})"
        )
        db.add(log)

        # 6. Hacer commit
        db.commit()
        db.refresh(nuevo_maestro)

        # 5. Retornar JSON
        return {
            "mensaje": "Oficio generado correctamente",
            "id_maestro": nuevo_maestro.id,
            "codigo_unico": nuevo_maestro.codigo_unico,
            "pdf_url": f"/api/v1/generar/documentos/{nuevo_maestro.tipo_documento.value}_{nuevo_maestro.id}.pdf"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al generar documento: {str(e)}")


@router.post("/resolucion/preview", response_class=HTMLResponse)
def previsualizar_resolucion(resolucion_in: schemas.ResolucionCreate, current_user: models.User = Depends(get_current_user)):
    try:
        datos_dict = resolucion_in.model_dump()
        html_content = pdf_service.generar_html_preview("resolucion", datos_dict)
        return html_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al previsualizar resolución: {str(e)}")

@router.post("/resolucion", status_code=status.HTTP_201_CREATED)
async def generar_resolucion(
    datos: str = Form(...),
    adjuntoPdf: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        import json
        datos_dict = json.loads(datos)
        resolucion_in = schemas.ResolucionCreate(**datos_dict)

        # 1 & 2. Iniciar transacción e insertar Documento Maestro
        codigo_unico = str(uuid.uuid4())
        nuevo_maestro = models.DocumentoMaestro(
            codigo_unico=codigo_unico,
            tipo_documento=models.TipoDocumento.resolucion,
            usuario_id=current_user.id
        )
        db.add(nuevo_maestro)
        db.flush() 

        # 3. Insertar datos en Campos_Resolucion
        nuevo_resolucion = models.CamposResolucion(
            maestro_id=nuevo_maestro.id,
            nro_resolucion=resolucion_in.nro_resolucion,
            lema_anio=resolucion_in.lema_anio,
            lugar_fecha=resolucion_in.lugar_fecha,
            vistos_texto=resolucion_in.vistos_texto,
            considerandos=resolucion_in.considerandos,
            parrafo_previo_resuelve=resolucion_in.parrafo_previo_resuelve,
            articulos=resolucion_in.articulos,
            texto_cierre=resolucion_in.texto_cierre,
            secretario_nombre=resolucion_in.secretario_nombre,
            rectora_nombre=resolucion_in.rectora_nombre
        )
        db.add(nuevo_resolucion)
        db.flush()

        # 4. Generar el PDF físico
        datos_dict_final = resolucion_in.model_dump()
        
        # Save attachment if provided
        adjunto_path = None
        if adjuntoPdf and adjuntoPdf.filename:
            adjunto_dir = "documentos_generados/adjuntos"
            import os
            os.makedirs(adjunto_dir, exist_ok=True)
            adjunto_path = os.path.join(adjunto_dir, f"adjunto_{nuevo_maestro.id}_{adjuntoPdf.filename}")
            content = await adjuntoPdf.read()
            with open(adjunto_path, "wb") as f_adj:
                f_adj.write(content)

        # The pdf_service will handle combining if adjunto_path is provided
        ruta_pdf = pdf_service.generar_pdf("resolucion", datos_dict_final, nuevo_maestro.id, adjunto_path=adjunto_path)
        nuevo_maestro.ruta_pdf_final = ruta_pdf
        
        # 5. Guardar log de auditoría
        log = models.LogAuditoria(
            usuario_id=current_user.id,
            accion="CREAR",
            modulo="RESOLUCIONES",
            detalles=f"Se registró una nueva resolución (Cód: {nuevo_maestro.codigo_unico})"
        )
        db.add(log)

        # 6. Hacer commit
        db.commit()
        db.refresh(nuevo_maestro)

        return {
            "mensaje": "Resolución generada correctamente",
            "id_maestro": nuevo_maestro.id,
            "codigo_unico": nuevo_maestro.codigo_unico,
            "pdf_url": f"/api/v1/generar/documentos/{nuevo_maestro.tipo_documento.value}_{nuevo_maestro.id}.pdf"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al generar resolución: {str(e)}")

@router.get("/oficios")
def obtener_oficios(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
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
                "pdf_url": f"/api/v1/generar/documentos/{maestro.tipo_documento.value}_{maestro.id}.pdf"
            })
            
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")

@router.get("/documentos")
def obtener_documentos(
    q: Optional[str] = Query(None, description="Texto a buscar"),
    tipo: Optional[str] = Query(None, description="Tipo de documento (oficio, resolucion)"),
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        from sqlalchemy import or_, and_, cast, Date
        
        # Base query joining Maestro with CamposOficio and CamposResolucion
        query = db.query(models.DocumentoMaestro, models.CamposOficio, models.CamposResolucion)\
            .outerjoin(models.CamposOficio, models.DocumentoMaestro.id == models.CamposOficio.maestro_id)\
            .outerjoin(models.CamposResolucion, models.DocumentoMaestro.id == models.CamposResolucion.maestro_id)

        # Apply Filters
        if tipo:
            query = query.filter(models.DocumentoMaestro.tipo_documento == tipo)
            
        if fecha_inicio:
            query = query.filter(cast(models.DocumentoMaestro.fecha_registro, Date) >= fecha_inicio)
            
        if fecha_fin:
            query = query.filter(cast(models.DocumentoMaestro.fecha_registro, Date) <= fecha_fin)

        if q:
            # Search in common fields of oficio and resolucion
            search_term = f"%{q}%"
            query = query.filter(
                or_(
                    models.DocumentoMaestro.codigo_unico.ilike(search_term),
                    models.CamposOficio.nro_oficio.ilike(search_term),
                    models.CamposOficio.asunto.ilike(search_term),
                    models.CamposOficio.destinatario_nombre.ilike(search_term),
                    models.CamposResolucion.nro_resolucion.ilike(search_term),
                    models.CamposResolucion.lema_anio.ilike(search_term)
                )
            )

        documentos = query.all()
        
        resultados = []
        for maestro, oficio, resolucion in documentos:
            campos_especificos = {}
            if maestro.tipo_documento.value == "oficio" and oficio:
                campos_especificos = {
                    "nro_oficio": oficio.nro_oficio,
                    "lema_anio": oficio.lema_anio,
                    "lugar_fecha": oficio.lugar_fecha,
                    "destinatario_titulo": oficio.destinatario_titulo,
                    "destinatario_nombre": oficio.destinatario_nombre,
                    "destinatario_cargo": oficio.destinatario_cargo,
                    "destinatario_dependencia": oficio.destinatario_dependencia,
                    "asunto": oficio.asunto,
                    "referencia": oficio.referencia,
                    "cuerpo_mensaje": oficio.cuerpo_mensaje,
                    "remitente_nombre": oficio.remitente_nombre,
                    "nt": oficio.nt,
                    "folios": oficio.folios,
                    "copia": oficio.copia
                }
            elif maestro.tipo_documento.value == "resolucion" and resolucion:
                campos_especificos = {
                    "nro_resolucion": resolucion.nro_resolucion,
                    "lema_anio": resolucion.lema_anio,
                    "secretario_nombre": resolucion.secretario_nombre,
                    "rectora_nombre": resolucion.rectora_nombre
                }
            
            resultados.append({
                "id_maestro": maestro.id,
                "codigo_unico": maestro.codigo_unico,
                "tipo_documento": maestro.tipo_documento.value.upper(),
                "fecha_registro": maestro.fecha_registro.strftime("%Y-%m-%d %H:%M:%S"),
                "estado": maestro.estado,
                "pdf_url": f"/api/v1/generar/documentos/{maestro.tipo_documento.value}_{maestro.id}.pdf",
                "campos_especificos": campos_especificos
            })
            
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener documentos: {str(e)}")

@router.get("/documentos/{filename}")
def descargar_documento(
    filename: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file_path = os.path.join("documentos_generados", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Documento no encontrado o no ha sido generado")
        
    return FileResponse(file_path, media_type="application/pdf", filename=filename)
