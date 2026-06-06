import os

# Asegurar que el directorio de salida exista
OUTPUT_DIR = "documentos_generados"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generar_pdf(tipo_documento: str, datos: dict, id_maestro: int) -> str:
    """
    Dispatcher central para la generación de PDFs.
    Enruta la petición al generador específico según el tipo_documento.
    """
    tipo = tipo_documento.lower()
    
    if tipo == "oficio":
        from services.generators.oficio_generator import generar_pdf as gen_oficio
        return gen_oficio(datos, id_maestro, OUTPUT_DIR)
        
    elif tipo == "resolucion":
        # from services.generators.resolucion_generator import generar_pdf as gen_resolucion
        # return gen_resolucion(datos, id_maestro, OUTPUT_DIR)
        raise NotImplementedError("Generador de Resolución aún no implementado")
        
    else:
        raise ValueError(f"Tipo de documento desconocido para PDF: {tipo}")
