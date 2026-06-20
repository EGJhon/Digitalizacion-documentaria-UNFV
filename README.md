# Módulo de Digitalización Documentaria - UNFV

Este es el backend del Módulo de Digitalización Documentaria, construido con FastAPI. Permite la extracción de datos de documentos mediante OCR, la generación de PDFs estructurados y el almacenamiento de la información en una base de datos relacional.

## Tecnologías Utilizadas

- **FastAPI**: Framework web de alto rendimiento.
- **SQLAlchemy**: ORM para la interacción con la base de datos.
- **Tesseract OCR (pytesseract)**: Para la extracción de texto de imágenes y PDFs.
- **SQL Server / SQLite**: Base de datos principal (SQL Server) con soporte local (SQLite).
- **Docker**: Para facilitar el despliegue de la aplicación.

## Características Principales

1. **Extracción (OCR)**: Subida de documentos (PDF o Imagen) para extraer su contenido de texto.
2. **Generación de Documentos**: Creación de documentos oficiales ("Oficios" y próximamente "Resoluciones") y generación física de PDFs.
3. **Gestión Documental**: Almacenamiento del registro (Documento Maestro) e historial de documentos generados.
4. **Autenticación**: Endpoint básico de login protegido por variables de entorno.

## Requisitos Previos

- Python 3.10+ (si se ejecuta localmente sin Docker).
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado en tu sistema.
- Docker y Docker Compose (opcional, para despliegue en contenedores).

## Configuración y Variables de Entorno

El proyecto soporta configuración mediante variables de entorno. Puedes crear un archivo `.env` o configurarlas directamente en tu sistema o en el `docker-compose.yml`:

```env
# Credenciales de acceso de administrador (Auth)
APP_ADMIN_USERNAME=admin
APP_ADMIN_PASSWORD=admin123

# Configuración de Base de Datos (SQL Server)
DB_SERVER=host.docker.internal,1433
DB_USER=Digital
DB_PASSWORD=**********
DB_NAME=DigitalizacionDB
```

*Nota: Si las variables de base de datos no están definidas, la aplicación utilizará automáticamente una base de datos SQLite de forma local para facilitar el desarrollo.*

## Configuración de SQL Server (Solo Windows)

Si vas a conectar la aplicación (ya sea desde Docker o localmente) a una instancia de SQL Server en tu máquina, debes asegurarte de realizar estas configuraciones previas:

### 1. Habilitar el puerto TCP/IP 1433
Por defecto, SQL Server no permite conexiones por red, lo cual es estrictamente necesario para conectar la aplicación (especialmente si corre en Docker) a tu base de datos local.
1. Abre **SQL Server Configuration Manager** (Administrador de configuración de SQL Server) en Windows o `CMD + R` y SQLServerManager16.msc.
2. Expande **Configuración de red de SQL Server** y selecciona **Protocolos de MSSQLSERVER** (o la instancia que uses, como `SQLEXPRESS`).
3. Haz clic derecho en **TCP/IP** y selecciona **Habilitar**.
4. Haz doble clic en **TCP/IP**, ve a la pestaña **Direcciones IP**, y baja hasta la sección **IPAll** (al final). Asegúrate de que el campo **Puerto TCP** tenga el valor `1433` (y deja vacíos los Puertos dinámicos TCP).
5. Ve a **Servicios de SQL Server** en el panel izquierdo, haz clic derecho en tu servicio principal (ej. `SQL Server (MSSQLSERVER)` o `SQL Server (SQLEXPRESS)`) y selecciona **Reiniciar**.
*(Importante: Si el Firewall de Windows está activo, asegúrate de crear una nueva regla de entrada para permitir el tráfico en el puerto TCP 1433).*

### 2. Crear un usuario de SQL Server (Autenticación Mixta)
El usuario que definas en tu archivo `.env` o en el bloque de variables de entorno debe existir en la base de datos con los permisos necesarios.
1. Abre **SQL Server Management Studio (SSMS)** y conéctate a tu servidor local.
2. Asegúrate de que el servidor permita autenticación por usuario/contraseña: Haz clic derecho a tu servidor en el Explorador de objetos > Propiedades > Seguridad > Selecciona **"Modo de autenticación de Windows y SQL Server"** > Ok (Requerirá reiniciar el servicio).
3. Expande la carpeta **Seguridad** > **Inicios de sesión**.
4. Haz clic derecho y selecciona **Nuevo inicio de sesión...**
5. En **Nombre de inicio de sesión**, escribe el usuario que usarás (ej. `Digital`).
6. Selecciona **Autenticación de SQL Server**, ingresa tu contraseña y desmarca "Exigir directivas de contraseña" para evitar que caduque rápidamente.
7. En el panel izquierdo, ve a la pestaña **Asignación de usuarios**, selecciona tu base de datos (ej. `DigitalizacionDB`) y en la parte inferior marca el rol `db_owner` (o los permisos de lectura/escritura que correspondan).
8. Haz clic en **Aceptar**.

## Ejecución con Docker (Recomendado)

1. Clona el repositorio.
2. Configura las variables en el archivo `docker-compose.yml` o en tu entorno.
3. Levanta los contenedores:
   ```bash
   docker-compose up -d --build
   ```
4. Accede a la interfaz web principal en: `http://localhost:8000/` 
5. Revisa la documentación interactiva de la API (Swagger) en: `http://localhost:8000/docs`

## Ejecución Local (Sin Docker)

1. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   # Activar el entorno
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```
2. Asegúrate de tener **Tesseract OCR** instalado. Si usas Windows, es posible que necesites descomentar y ajustar la ruta de instalación en el archivo `services/ocr_service.py`:
   ```python
   # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```
3. Inicia el servidor de desarrollo:
   ```bash
   uvicorn main:app --reload
   ```

## Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación FastAPI.
- `models.py` / `schemas.py`: Definición de modelos de base de datos (SQLAlchemy) y esquemas de validación (Pydantic).
- `database.py`: Configuración y lógica de conexión a la base de datos.
- `router_*.py`: Controladores (Endpoints) divididos por dominio funcional de la API.
- `services/`: Lógica de negocio core (OCR, Generación de PDFs, etc).
- `static/`: Archivos del frontend (HTML, CSS, JS) servidos directamente.
- `documentos_generados/`: Directorio donde se almacenan temporal o permanentemente los PDFs generados.
