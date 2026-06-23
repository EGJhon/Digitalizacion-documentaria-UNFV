import re

def extraer_campos_oficio(texto_crudo: str) -> dict:
    """
    Aplica Expresiones Regulares sobre un texto extraído por OCR 
    para obtener los campos complejos de un Oficio.
    """

    datos = {
        "lema_anio": "",
        "lugar_fecha": "",
        "nro_oficio": "",
        "destinatario_titulo": "",
        "destinatario_nombre": "",
        "destinatario_cargo": "",
        "destinatario_dependencia": "",
        "asunto": "",
        "referencia": "",
        "remitente_nombre": "",
        "nt": "",
        "folios": "",
        "copia": ""
    }

    # Lema del año (busca algo entre comillas o al menos la frase clave)
    # Con OCR muchas veces no lee las comillas correctamente
    match_lema = re.search(r'A[ñn]o de la\s+([^\n"\'”]+)', texto_crudo, re.IGNORECASE)
    if match_lema:
        datos["lema_anio"] = "Año de la " + match_lema.group(1).strip()
        
    # Lugar y fecha (ej: San Miguel, 27 de mayo de 2025)
    match_fecha = re.search(r'([A-Za-z\s]+,\s*\d{1,2}\s*de\s*[A-Za-z]+\s*de\s*\d{4})', texto_crudo)
    if match_fecha:
        datos["lugar_fecha"] = match_fecha.group(1).strip()

    # Búsqueda Regex N° de Oficio (Tolerante a OCR N' o N° o N*)
    match_oficio = re.search(r'OFICIO\s*(?:m[uú]ltiple)?\s*[Nn]?[°º\'\*]?\s*([A-Za-z0-9\-\_]+)', texto_crudo, re.IGNORECASE)
    if match_oficio:
        datos["nro_oficio"] = match_oficio.group(1).strip()
        
    # Destinatario completo (Capturar bloque entre Oficio y Asunto)
    # Tolerar espacios o saltos de línea y símbolos sucios al final de Presente
    match_bloque_destinatario = re.search(r'(Se[ñn]or[a]?\s*(?:doctor|doctora|magister|licenciado)?[a-z]*|Dr\.|Dra\.|Mg\.)[\s\n]+([A-Za-zñÑáéíóúÁÉÍÓÚ\s\.]+)[\s\n]+([A-Za-zñÑáéíóúÁÉÍÓÚ\s]+)[\s\n]+([A-Za-zñÑáéíóúÁÉÍÓÚ\s]+)[\s\n]+Presente', texto_crudo, re.IGNORECASE)
    if match_bloque_destinatario:
        datos["destinatario_titulo"] = match_bloque_destinatario.group(1).strip()
        datos["destinatario_nombre"] = match_bloque_destinatario.group(2).strip()
        datos["destinatario_cargo"] = match_bloque_destinatario.group(3).strip()
        datos["destinatario_dependencia"] = match_bloque_destinatario.group(4).strip()
        
    # Asunto
    match_asunto = re.search(r'ASUNTO\s*:\s*([^\n]+)', texto_crudo, re.IGNORECASE)
    if match_asunto:
        datos["asunto"] = match_asunto.group(1).strip()
        
    # Referencia (puede ser multilínea, nos detenemos antes de 'De mi consideración' o un párrafo nuevo)
    match_ref = re.search(r'Referencia\s*:\s*(.+?)(?=\n\s*\n|\nDe mi consideración)', texto_crudo, re.IGNORECASE | re.DOTALL)
    if match_ref:
        datos["referencia"] = match_ref.group(1).strip()
        
    # Remitente: Buscar firma o "Atentamente," (tolerante a ; en vez de ,) y extraer nombre
    match_remitente = re.search(r'Atentamente[;,][\s\n]*((?:Mg\.|Dr\.|Lic\.|Mg-)?[\s]*[A-Za-zñÑáéíóúÁÉÍÓÚ\s]+)', texto_crudo, re.IGNORECASE)
    if match_remitente:
        remitente_texto = match_remitente.group(1).strip().split('\n')[0]
        # Limpiar si agarró parte de la firma digital (ej. "por TdefanEs")
        remitente_texto = re.split(r'\s+por\s+', remitente_texto, flags=re.IGNORECASE)[0]
        datos["remitente_nombre"] = remitente_texto.strip()
        
    # NT (Número de Trámite)
    match_nt = re.search(r'NT:\s*([0-9\-\s/]+)', texto_crudo, re.IGNORECASE)
    if match_nt:
        datos["nt"] = match_nt.group(1).strip()
        
    # Folios
    match_folios = re.search(r'Folios:\s*([0-9]+)', texto_crudo, re.IGNORECASE)
    if match_folios:
        datos["folios"] = match_folios.group(1).strip()
        
    # Copia (Cc)
    match_copia = re.search(r'Cc:\s*([^\n]+)', texto_crudo, re.IGNORECASE)
    if match_copia:
        datos["copia"] = match_copia.group(1).strip()
        
    return datos

def transformar_donut_a_oficio(donut_json: dict) -> dict:
    """
    Toma el diccionario JSON nativo devuelto por Donut y lo mapea
    al esquema esperado por el módulo de oficios.
    """
    datos = {
        "lema_anio": "",
        "lugar_fecha": "",
        "nro_oficio": "",
        "destinatario_titulo": "",
        "destinatario_nombre": "",
        "destinatario_cargo": "",
        "destinatario_dependencia": "",
        "asunto": "",
        "referencia": "",
        "remitente_nombre": "",
        "nt": "",
        "folios": "",
        "copia": ""
    }
    
    # Donut devuelve diccionarios anidados. Aplanamos para buscar valores
    # por palabras clave en los strings.
    def buscar_en_dict(d, text_acc=""):
        if isinstance(d, dict):
            for v in d.values():
                text_acc += " " + buscar_en_dict(v)
        elif isinstance(d, list):
            for item in d:
                text_acc += " " + buscar_en_dict(item)
        elif isinstance(d, str):
            text_acc += " " + d
        return text_acc.strip()
    
    # Si usamos Donut sin fine-tuning específico para oficios peruanos, 
    # es posible que extraiga todo el texto como un gran string bajo algunas keys 
    # o intente estructurarlo según el dataset CORD. 
    # Lo más seguro es aplanar el JSON y pasarle nuestras regex actuales como fallback,
    # o extraer directamente si las keys coinciden.
    
    texto_plano = buscar_en_dict(donut_json)
    
    # Usamos las regex existentes sobre el texto estructurado extraído 
    # ya que Donut al menos nos da el texto con mejor exactitud sin fallas de OCR 
    # comunes (como confundir I con l, etc).
    datos = extraer_campos_oficio(texto_plano)
    
    return datos

