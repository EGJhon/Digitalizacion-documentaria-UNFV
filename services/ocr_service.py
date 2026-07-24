import io
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
import easyocr

# Variable global para cargar el modelo de forma perezosa (lazy loading)
reader = None

def load_ai_model():
    global reader
    if reader is None:
        print("Cargando modelo de IA (EasyOCR con Deep Learning)...")
        # Inicializa el modelo para español. Usa GPU si está disponible, sino CPU.
        reader = easyocr.Reader(['es'], gpu=False)
        print("Modelo IA cargado correctamente.")

def extraer_datos_oficio(file_bytes: bytes, filename: str) -> dict:
    """
    Recibe los bytes de un archivo (PDF o Imagen).
    Utiliza el modelo de Inteligencia Artificial EasyOCR (Redes Neuronales)
    para leer el documento completo con altísima precisión.
    """
    try:
        # 1. Preparar la imagen
        if filename.lower().endswith('.pdf'):
            images = convert_from_bytes(file_bytes, first_page=1, last_page=1)
            if not images:
                raise ValueError("No se pudo extraer ninguna página del PDF.")
            imagen = images[0].convert("RGB")
        else:
            imagen = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        
        # 2. Cargar el modelo AI
        load_ai_model()
        
        # 3. EasyOCR requiere un arreglo numpy en lugar de un objeto PIL Image
        img_np = np.array(imagen)

        # 4. Extraer SIN agrupar párrafos (mantiene saltos de línea estrictos para las Regex)
        result_para_regex = reader.readtext(img_np, detail=0, paragraph=False)
        texto_para_regex = "\n".join(result_para_regex)
        
        # 5. Extraer AGRUPANDO párrafos (para mostrar un texto bonito en la interfaz)
        result_para_ui = reader.readtext(img_np, detail=0, paragraph=True)
        texto_para_ui = "\n\n".join(result_para_ui)
        
    except Exception as e:
        print(f"Error procesando con IA local: {e}")
        return {
            "texto_crudo": f"Error IA: {str(e)}",
            "datos_sugeridos": {"nro_oficio": None, "fecha": None, "remitente": None, "destinatario": None, "asunto": None}
        }
    
    # 6. Intentar extracción con LLM Local (Ollama)
    from services.llm_service import extraer_json_con_llm
    datos = extraer_json_con_llm(texto_para_regex)
    
    if not datos:
        print("Fallback a extracción por expresiones regulares (Regex).")
        from services.extractors.oficio_extractor import extraer_campos_oficio
        datos = extraer_campos_oficio(texto_para_regex)
    
    # 7. Recortar el texto bonito para que SOLO muestre el cuerpo del mensaje
    import re
    # Busca desde "De mi consideración" (incluyéndolo) hasta antes de "Atentamente"
    match_cuerpo = re.search(r'(De mi consideraci[oó]n:?.*?)(?=\n*Atentamente)', texto_para_ui, re.IGNORECASE | re.DOTALL)
    if match_cuerpo:
        cuerpo_bonito = match_cuerpo.group(1).strip()
    else:
        # Fallback alternativo: Desde "Tengo el agrado"
        match_cuerpo = re.search(r'(Tengo el agrado.*?)(?=\n*Atentamente)', texto_para_ui, re.IGNORECASE | re.DOTALL)
        if match_cuerpo:
            cuerpo_bonito = match_cuerpo.group(1).strip()
        else:
            # Si no encuentra ninguna de las frases clave, devuelve todo
            cuerpo_bonito = texto_para_ui
        
    return {
        "texto_crudo": cuerpo_bonito, # Devolvemos a la UI SOLO el cuerpo recortado
        "datos_sugeridos": datos
    }


def extraer_datos_resolucion(file_bytes: bytes, filename: str) -> dict:
    """
    Recibe los bytes de un archivo (PDF o Imagen).
    Utiliza IA (EasyOCR y LLM) para leer y estructurar una resolución.
    """
    try:
        load_ai_model()
        texto_para_regex = ""

        if filename.lower().endswith('.pdf'):
            # Convertir todas las páginas (no limitar a last_page=1)
            images = convert_from_bytes(file_bytes)
            if not images:
                raise ValueError("No se pudo extraer ninguna página del PDF.")
            
            for i, img in enumerate(images):
                imagen = img.convert("RGB")
                img_np = np.array(imagen)
                result = reader.readtext(img_np, detail=0, paragraph=False)
                texto_para_regex += "\n".join(result) + "\n"
        else:
            imagen = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            img_np = np.array(imagen)
            result = reader.readtext(img_np, detail=0, paragraph=False)
            texto_para_regex = "\n".join(result)

        
    except Exception as e:
        print(f"Error procesando con IA local: {e}")
        return {
            "texto_crudo": f"Error IA: {str(e)}",
            "datos_sugeridos": {}
        }
    
    from services.llm_service import extraer_json_con_llm_resolucion
    datos = extraer_json_con_llm_resolucion(texto_para_regex)
    
    if not datos:
        print("Fallo el LLM para resolucion, devolviendo vacio.")
        datos = {}
        
    return {
        "texto_crudo": texto_para_regex,
        "datos_sugeridos": datos
    }
