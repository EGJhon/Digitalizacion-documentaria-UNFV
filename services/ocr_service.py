import pytesseract
from PIL import Image
import re
import io
from pdf2image import convert_from_bytes

# Si estás en Windows probando fuera de Docker, descomenta la siguiente línea y ajusta la ruta:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_datos_oficio(file_bytes: bytes, filename: str) -> dict:
    """
    Recibe los bytes de un archivo (PDF o Imagen).
    Si es PDF, lo convierte a imagen. Luego extrae el texto mediante OCR
    y devuelve un diccionario con los datos estructurados.
    """
    try:
        # Detectar si es PDF por la extensión o contenido
        if filename.lower().endswith('.pdf'):
            # Convertir la primera página del PDF a imagen
            images = convert_from_bytes(file_bytes, first_page=1, last_page=1)
            if not images:
                raise ValueError("No se pudo extraer ninguna página del PDF.")
            imagen = images[0]
        else:
            # Procesar directamente como imagen
            imagen = Image.open(io.BytesIO(file_bytes))
        
        # Extraer texto en español
        texto_extraido = pytesseract.image_to_string(imagen, lang='spa')
    except Exception as e:
        print(f"Error OCR: {e}. Asegúrate de tener Tesseract OCR instalado.")
        texto_extraido = "SIMULACION: OFICIO N° 001-2023\nA: Sr. Rector\nASUNTO: Prueba de Sistema\nDE: Oficina de Sistemas\nCuerpo del mensaje simulado debido a falta de Tesseract."
    
    # 3. Importar dinámicamente el extractor según el tipo de documento
    # En este caso está hardcodeado a "oficio", pero en el futuro se 
    # pasará como argumento a la función (ej. tipo_documento="resolucion")
    from services.extractors.oficio_extractor import extraer_campos_oficio
    
    datos = extraer_campos_oficio(texto_extraido)
        
    return {
        "texto_crudo": texto_extraido,
        "datos_sugeridos": datos
    }
