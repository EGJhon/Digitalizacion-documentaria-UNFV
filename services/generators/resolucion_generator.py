import os
import pdfkit
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Configurar Jinja2
env = Environment(loader=FileSystemLoader("templates"))

def format_datos(datos: dict) -> dict:
    d = dict(datos)
    
    # Process considerandos from newline separated string to list
    cons = d.get('considerandos', '')
    if isinstance(cons, str):
        d['considerandos'] = [c.strip() for c in cons.split('\n') if c.strip()]
        
    # Process articulos from newline separated string to list of dicts
    arts = d.get('articulos', '')
    if isinstance(arts, str):
        parsed_arts = []
        for a in arts.split('\n'):
            a = a.strip()
            if not a: continue
            parts = a.split('|', 1)
            if len(parts) == 2:
                parsed_arts.append({"numero": parts[0].strip(), "texto": parts[1].strip()})
            else:
                parsed_arts.append({"numero": str(len(parsed_arts) + 1), "texto": a})
        d['articulos'] = parsed_arts
        
    d["fecha_actual"] = datetime.now().strftime("%d de %B del %Y")
    return d

def generar_html(datos: dict) -> str:
    """
    Renderiza la plantilla HTML para una Resolución y retorna el HTML como string.
    """
    template = env.get_template("plantilla_resolucion.html")
    formatted_datos = format_datos(datos)
    return template.render(formatted_datos)

def generar_pdf(datos: dict, id_maestro: int, output_dir: str) -> str:
    """
    Renderiza la plantilla HTML para una Resolución y lo exporta a PDF.
    Retorna la ruta relativa del archivo creado.
    """
    template = env.get_template("plantilla_resolucion.html")
    formatted_datos = format_datos(datos)
    
    html_out = template.render(formatted_datos)
    
    pdf_filename = f"resolucion_{id_maestro}.pdf"
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
