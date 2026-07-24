from pypdf import PdfWriter, PdfReader
import os

# Asegurar que el directorio de salida exista
OUTPUT_DIR = "documentos_generados"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generar_html_preview(tipo_documento: str, datos: dict) -> str:
    """
    Dispatcher central para la generación de HTML (Preview).
    """
    tipo = tipo_documento.lower()
    
    if tipo == "oficio":
        from services.generators.oficio_generator import generar_html as gen_html_oficio
        return gen_html_oficio(datos)
        
    elif tipo == "resolucion":
        from services.generators.resolucion_generator import generar_html as gen_html_res
        return gen_html_res(datos)
        
    else:
        raise ValueError(f"Tipo de documento desconocido para Preview: {tipo}")

def generar_pdf(tipo_documento: str, datos: dict, id_maestro: int, adjunto_path: str = None) -> str:
    """
    Dispatcher central para la generación de PDFs.
    Enruta la petición al generador específico según el tipo_documento.
    """
    tipo = tipo_documento.lower()
    
    pdf_path = None
    if tipo == "oficio":
        from services.generators.oficio_generator import generar_pdf as gen_oficio
        pdf_path = gen_oficio(datos, id_maestro, OUTPUT_DIR)
        
    elif tipo == "resolucion":
        from services.generators.resolucion_generator import generar_pdf as gen_resolucion
        pdf_path = gen_resolucion(datos, id_maestro, OUTPUT_DIR)
        
    else:
        raise ValueError(f"Tipo de documento desconocido para PDF: {tipo}")

    # Merge attachment if provided
    if adjunto_path and os.path.exists(adjunto_path):
        import traceback
        try:
            merger = PdfWriter()
            # Append generated pdf
            merger.append(pdf_path)
            # Append attached pdf
            merger.append(adjunto_path)
            
            # Save merged back to pdf_path
            merged_path = pdf_path.replace('.pdf', '_merged.pdf')
            with open(merged_path, "wb") as f_out:
                merger.write(f_out)
            
            # Replace original with merged
            os.remove(pdf_path)
            os.rename(merged_path, pdf_path)
        except Exception as e:
            print(f"Error al adjuntar archivo PDF: {e}")
            traceback.print_exc()
            # Continue returning pdf_path without merging if error

    return pdf_path
