import os
import pdfkit
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Configurar Jinja2
env = Environment(loader=FileSystemLoader("templates"))

def generar_html(datos: dict) -> str:
    """
    Renderiza la plantilla HTML para un Oficio y retorna el HTML como string.
    """
    template = env.get_template("plantilla_oficio.html")
    # Agregar fecha actual
    datos["fecha_actual"] = datetime.now().strftime("%d de %B del %Y")
    return template.render(datos)

def generar_pdf(datos: dict, id_maestro: int, output_dir: str) -> str:
    """
    Renderiza la plantilla HTML para un Oficio y lo exporta a PDF.
    Retorna la ruta relativa del archivo creado.
    """
    template = env.get_template("plantilla_oficio.html")
    
    # Agregar fecha actual
    datos["fecha_actual"] = datetime.now().strftime("%d de %B del %Y")
    
    html_out = template.render(datos)
    
    pdf_filename = f"oficio_{id_maestro}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)
    
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
    }
    
    try:
        pdfkit.from_string(html_out, pdf_path, options=options)
    except Exception as e:
        print(f"Advertencia: No se pudo generar el PDF. Error: {e}")
        
    return pdf_path
