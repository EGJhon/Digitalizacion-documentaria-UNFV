from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ocr_service import extraer_datos_oficio

router = APIRouter(
    prefix="/api/v1/extraer",
    tags=["Extracción OCR"]
)

@router.post("/oficio")
async def extraer_oficio(archivo: UploadFile = File(...)):
    # Validar que sea imagen o PDF
    if not (archivo.content_type.startswith("image/") or archivo.content_type == "application/pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (PNG/JPG) o un documento PDF")
    
    try:
        contenido = await archivo.read()
        datos = extraer_datos_oficio(contenido, archivo.filename)
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en OCR: {str(e)}")
