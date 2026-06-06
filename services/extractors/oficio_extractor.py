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

    # Lema del año (busca algo entre comillas)
    match_lema = re.search(r'["\'](Año de [^"\']+)["\']', texto_crudo, re.IGNORECASE)
    if match_lema:
        datos["lema_anio"] = match_lema.group(1).strip()
        
    # Lugar y fecha (ej: San Miguel, 27 de mayo de 2025)
    match_fecha = re.search(r'([A-Za-z\s]+,\s*\d{1,2}\s*de\s*[A-Za-z]+\s*de\s*\d{4})', texto_crudo)
    if match_fecha:
        datos["lugar_fecha"] = match_fecha.group(1).strip()

    # Búsqueda Regex N° de Oficio
    match_oficio = re.search(r'OFICIO\s*(?:múltiple)?\s*[Nn]?[°º]?\s*([A-Za-z0-9\-\_]+)', texto_crudo, re.IGNORECASE)
    if match_oficio:
        datos["nro_oficio"] = match_oficio.group(1).strip()
        
    # Destinatario completo (Capturar bloque entre Oficio y Asunto)
    # Asume que empieza con Señor / Dra / etc.
    match_bloque_destinatario = re.search(r'(Señor[a]?\s*[a-z]*|Dr\.|Dra\.|Mg\.)\s*\n+([A-Za-zñÑáéíóúÁÉÍÓÚ\s\.]+)\n+([A-Za-zñÑáéíóúÁÉÍÓÚ\s]+)\n+([A-Za-zñÑáéíóúÁÉÍÓÚ\s]+)\n+Presente', texto_crudo, re.IGNORECASE)
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
        
    # Remitente: Buscar firma o "Atentamente," y extraer nombre
    match_remitente = re.search(r'Atentamente,[\s\n]*((?:Mg\.|Dr\.|Lic\.)?[A-Za-zñÑáéíóúÁÉÍÓÚ\s]+)', texto_crudo, re.IGNORECASE)
    if match_remitente:
        remitente_texto = match_remitente.group(1).strip().split('\n')[0]
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
