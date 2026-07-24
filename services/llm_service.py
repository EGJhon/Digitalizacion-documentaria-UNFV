import os
import requests
import json

# URL by default is host.docker.internal to reach the host from within the docker container
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b-instruct-q8_0")

def extraer_json_con_llm(texto_ocr: str) -> dict:
    """
    Envía el texto OCR crudo a un modelo LLM local (Ollama) para que
    lo estructure en formato JSON según el esquema de Oficio.
    """
    prompt = f"""
Eres un asistente experto en extracción de datos de documentos oficiales peruanos (Oficios).
Te voy a dar el texto crudo extraído mediante OCR de un documento físico. 
Tu tarea es leer el texto y extraer los siguientes campos en formato JSON estricto. 
Si no encuentras un campo, asigna el valor null. 
NO incluyas ninguna explicación, texto adicional ni formato markdown. SOLO responde con el JSON válido.

Estructura JSON esperada:
{{
    "lema_anio": "frase del año si existe",
    "lugar_fecha": "ej. Lima, 10 de octubre de 2024",
    "nro_oficio": "solo el número y siglas, ej. 001-2024-UNFV",
    "destinatario_titulo": "ej. Señor, Doctor, Magister",
    "destinatario_nombre": "nombre completo del destinatario",
    "destinatario_cargo": "cargo del destinatario",
    "destinatario_dependencia": "dependencia o institución del destinatario",
    "asunto": "el asunto resumido del documento",
    "referencia": "referencias mencionadas, si las hay",
    "cuerpo_mensaje": "el texto completo y detallado del cuerpo del mensaje",
    "remitente_nombre": "quién firma el documento al final",
    "nt": "número de trámite si se menciona",
    "folios": "cantidad de folios si se menciona",
    "copia": "personas o áreas en copia (cc) si se mencionan"
}}

Texto OCR:
{texto_ocr}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",  # Fuerza a Ollama a devolver un JSON estructurado
        "stream": False,
        "options": {
            "temperature": 0.1  # Temperatura baja para mayor precisión
        }
    }

    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        response_text = data.get("response", "")
        
        # Limpiar si el LLM incluye markdown a pesar de las instrucciones
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        json_data = json.loads(response_text.strip())
        return json_data
        
    except Exception as e:
        print(f"Error comunicándose con el LLM local: {e}")
        return None


def extraer_json_con_llm_resolucion(texto_ocr: str) -> dict:
    """
    Envía el texto OCR crudo a un modelo LLM local (Ollama) para que
    lo estructure en formato JSON según el esquema de Resolución.
    """
    prompt = f"""
Eres un asistente experto en extracción de datos de documentos oficiales peruanos (Resoluciones).
Te voy a dar el texto crudo extraído mediante OCR de un documento físico. 
Tu tarea es leer el texto y extraer los siguientes campos en formato JSON estricto. 
Si no encuentras un campo, asigna el valor null. 
NO incluyas ninguna explicación, texto adicional ni formato markdown. SOLO responde con el JSON válido.

Estructura JSON esperada:
{{
    "lema_anio": "frase del año si existe",
    "lugar_fecha": "ej. San Miguel, 10 de octubre de 2024",
    "nro_resolucion": "solo el número y siglas, ej. 001-2024-UNFV",
    "vistos_texto": "el texto completo del párrafo de Vistos",
    "considerandos": ["párrafo considerando 1", "párrafo considerando 2"],
    "parrafo_previo_resuelve": "el pequeño texto previo a la palabra SE RESUELVE",
    "articulos": [
        {{"numero": "1", "texto": "texto del articulo 1"}},
        {{"numero": "2", "texto": "texto del articulo 2"}}
    ],
    "texto_cierre": "el texto final como Comuníquese, regístrese y archívese.",
    "secretario_nombre": "nombre completo del secretario que firma",
    "rectora_nombre": "nombre completo del rector(a) que firma"
}}

Nota: Para los 'considerandos', extrae cada párrafo como un elemento de un arreglo de strings.
Para los 'articulos', extrae cada uno en un objeto con 'numero' (solo el número) y 'texto' (el contenido).

Texto OCR:
{texto_ocr}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    try:
        response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        response_text = data.get("response", "")
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        json_data = json.loads(response_text.strip())
        return json_data
        
    except Exception as e:
        print(f"Error comunicándose con el LLM local: {e}")
        return None
