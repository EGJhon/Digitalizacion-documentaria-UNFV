// Elementos UI Compartidos
const resultGlobalPanel = document.getElementById('resultGlobalPanel');
const globalSuccessMsg = document.getElementById('globalSuccessMsg');
const globalResId = document.getElementById('globalResId');
const globalResCodigo = document.getElementById('globalResCodigo');

// Navegación de Paneles
const menuLinks = document.querySelectorAll('.menu-link');
const viewPanels = document.querySelectorAll('.view-panel');

menuLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        // Quitar clase activa
        menuLinks.forEach(l => l.classList.remove('active'));
        // Ocultar paneles
        viewPanels.forEach(p => p.classList.add('hidden'));
        
        // Activar el clickeado
        const linkElement = e.currentTarget;
        linkElement.classList.add('active');
        const targetId = linkElement.getAttribute('data-target');
        
        if (targetId) {
            document.getElementById(targetId).classList.remove('hidden');
        }
        if (resultGlobalPanel) {
            resultGlobalPanel.classList.add('hidden');
        }
        
        // Si entramos a historial, cargar datos
        if(targetId === 'historialPanel') {
            cargarHistorial();
        }
    });
});

// Función genérica para enviar datos (POST /generar)
async function guardarDocumento(data, formElement) {
    try {
        const res = await fetch("/api/v1/generar/oficio", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        
        if (res.ok) {
            const json = await res.json();
            globalSuccessMsg.textContent = json.mensaje;
            globalResId.textContent = json.id_maestro;
            globalResCodigo.textContent = json.codigo_unico;
            resultGlobalPanel.classList.remove('hidden');
            formElement.reset();
            
            // Si estábamos en digitalizar, ocultar la revisión
            const revContainer = document.getElementById('formularioRevisionContainer');
            if(revContainer) revContainer.classList.add('hidden');
        } else {
            const err = await res.json();
            alert("Error al generar: " + JSON.stringify(err));
        }
    } catch (e) {
        alert("Error de conexión al generar documento.");
    }
}

// ---------------- LÓGICA: CREAR DOCUMENTOS ----------------
const docFormCrear = document.getElementById('docFormCrear');
if(docFormCrear) {
    docFormCrear.addEventListener('submit', (e) => {
        e.preventDefault();
        const data = {
            lema_anio: document.getElementById('c_lema_anio').value,
            lugar_fecha: document.getElementById('c_lugar_fecha').value,
            nro_oficio: document.getElementById('c_nro_oficio').value,
            destinatario_titulo: document.getElementById('c_destinatario_titulo').value,
            destinatario_nombre: document.getElementById('c_destinatario_nombre').value,
            destinatario_cargo: document.getElementById('c_destinatario_cargo').value,
            destinatario_dependencia: document.getElementById('c_destinatario_dependencia').value,
            asunto: document.getElementById('c_asunto').value,
            referencia: document.getElementById('c_referencia').value,
            cuerpo_mensaje: document.getElementById('c_cuerpo_mensaje').value,
            remitente_nombre: document.getElementById('c_remitente_nombre').value,
            nt: document.getElementById('c_nt').value,
            folios: document.getElementById('c_folios').value,
            copia: document.getElementById('c_copia').value
        };
        guardarDocumento(data, docFormCrear);
    });
}

// ---------------- LÓGICA: DIGITALIZAR DOCUMENTOS ----------------
const fileInput = document.getElementById('fileInput');
const btnExtraer = document.getElementById('btnExtraer');
const ocrLoader = document.getElementById('ocrLoader');
const ocrMsg = document.getElementById('ocrMsg');
const docFormDigitalizar = document.getElementById('docFormDigitalizar');
const formularioRevisionContainer = document.getElementById('formularioRevisionContainer');

if(fileInput) {
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        const viewer = document.getElementById('pdfViewer');
        const placeholder = document.getElementById('pdfPlaceholder');
        if (file && file.type === 'application/pdf') {
            const url = URL.createObjectURL(file);
            viewer.src = url;
            viewer.classList.remove('hidden');
            placeholder.classList.add('hidden');
        } else {
            if(viewer && placeholder) {
                viewer.classList.add('hidden');
                viewer.src = "";
                placeholder.classList.remove('hidden');
            }
            if (file) console.log("La vista previa solo está disponible para PDFs.");
        }
    });
}

if(btnExtraer) {
    btnExtraer.addEventListener('click', async () => {
        if (!fileInput.files || fileInput.files.length === 0) {
            alert("Seleccione una imagen primero.");
            return;
        }
        
        ocrLoader.style.display = 'block';
        ocrMsg.textContent = "Extrayendo información...";
        formularioRevisionContainer.classList.add('hidden');
        
        const formData = new FormData();
        formData.append("archivo", fileInput.files[0]);

        try {
            const res = await fetch("/api/v1/extraer/oficio", {
                method: "POST",
                body: formData
            });
            
            if (res.ok) {
                const data = await res.json();
                ocrMsg.textContent = "¡Datos extraídos con éxito! Revisalos abajo.";
                
                // Mostrar y autocompletar formulario
                formularioRevisionContainer.classList.remove('hidden');
                document.getElementById('d_lema_anio').value = data.datos_sugeridos.lema_anio || "";
                document.getElementById('d_lugar_fecha').value = data.datos_sugeridos.lugar_fecha || "";
                document.getElementById('d_nro_oficio').value = data.datos_sugeridos.nro_oficio || "";
                document.getElementById('d_destinatario_titulo').value = data.datos_sugeridos.destinatario_titulo || "";
                document.getElementById('d_destinatario_nombre').value = data.datos_sugeridos.destinatario_nombre || "";
                document.getElementById('d_destinatario_cargo').value = data.datos_sugeridos.destinatario_cargo || "";
                document.getElementById('d_destinatario_dependencia').value = data.datos_sugeridos.destinatario_dependencia || "";
                document.getElementById('d_asunto').value = data.datos_sugeridos.asunto || "";
                document.getElementById('d_referencia').value = data.datos_sugeridos.referencia || "";
                document.getElementById('d_cuerpo_mensaje').value = data.texto_crudo || "";
                document.getElementById('d_remitente_nombre').value = data.datos_sugeridos.remitente_nombre || "";
                document.getElementById('d_nt').value = data.datos_sugeridos.nt || "";
                document.getElementById('d_folios').value = data.datos_sugeridos.folios || "";
                document.getElementById('d_copia').value = data.datos_sugeridos.copia || "";
            } else {
                ocrMsg.textContent = "";
                alert("Error en la extracción OCR.");
            }
        } catch (e) {
            ocrMsg.textContent = "";
            alert("Error de conexión con el servidor OCR.");
        } finally {
            ocrLoader.style.display = 'none';
        }
    });
}

if(docFormDigitalizar) {
    docFormDigitalizar.addEventListener('submit', (e) => {
        e.preventDefault();
        const data = {
            lema_anio: document.getElementById('d_lema_anio').value,
            lugar_fecha: document.getElementById('d_lugar_fecha').value,
            nro_oficio: document.getElementById('d_nro_oficio').value,
            destinatario_titulo: document.getElementById('d_destinatario_titulo').value,
            destinatario_nombre: document.getElementById('d_destinatario_nombre').value,
            destinatario_cargo: document.getElementById('d_destinatario_cargo').value,
            destinatario_dependencia: document.getElementById('d_destinatario_dependencia').value,
            asunto: document.getElementById('d_asunto').value,
            referencia: document.getElementById('d_referencia').value,
            cuerpo_mensaje: document.getElementById('d_cuerpo_mensaje').value,
            remitente_nombre: document.getElementById('d_remitente_nombre').value,
            nt: document.getElementById('d_nt').value,
            folios: document.getElementById('d_folios').value,
            copia: document.getElementById('d_copia').value
        };
        guardarDocumento(data, docFormDigitalizar);
    });
}

// ---------------- LÓGICA: HISTORIAL / TABLA ----------------
const btnRefreshTabla = document.getElementById('btnRefreshTabla');
const btnBuscarHistorial = document.getElementById('btnBuscarHistorial');
const tablaOficiosBody = document.getElementById('tablaOficiosBody');

async function cargarHistorial() {
    if(!tablaOficiosBody) return;
    tablaOficiosBody.innerHTML = '<tr><td colspan="8" style="text-align: center;">Cargando registros...</td></tr>';
    
    // Recoger filtros
    const q = document.getElementById('filtroTexto') ? document.getElementById('filtroTexto').value : '';
    const tipo = document.getElementById('filtroTipo') ? document.getElementById('filtroTipo').value : '';
    const fechaInicio = document.getElementById('filtroFechaInicio') ? document.getElementById('filtroFechaInicio').value : '';
    const fechaFin = document.getElementById('filtroFechaFin') ? document.getElementById('filtroFechaFin').value : '';

    const params = new URLSearchParams();
    if(q) params.append('q', q);
    if(tipo) params.append('tipo', tipo);
    if(fechaInicio) params.append('fecha_inicio', fechaInicio);
    if(fechaFin) params.append('fecha_fin', fechaFin);

    try {
        const res = await fetch(`/api/v1/generar/documentos?${params.toString()}`);
        if(res.ok) {
            const data = await res.json();
            if(data.length === 0) {
                tablaOficiosBody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No hay documentos registrados aún.</td></tr>';
                return;
            }
            
            let filas = '';
            data.forEach(doc => {
                filas += `
                    <tr>
                        <td><strong>${doc.id_maestro}</strong></td>
                        <td><span style="text-transform: capitalize;">${doc.tipo_documento}</span></td>
                        <td>${doc.nro_documento}</td>
                        <td>${doc.fecha_registro}</td>
                        <td>${doc.asunto}</td>
                        <td>${doc.destinatario}</td>
                        <td><span class="badge">${doc.estado}</span></td>
                        <td><a href="${doc.pdf_url}" target="_blank" class="btn btn-blue" style="padding: 5px 10px; font-size:0.8em;">Ver PDF</a></td>
                    </tr>
                `;
            });
            tablaOficiosBody.innerHTML = filas;
        } else {
            tablaOficiosBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: red;">Error al cargar datos.</td></tr>';
        }
    } catch (e) {
        tablaOficiosBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: red;">Error de red.</td></tr>';
    }
}

if(btnRefreshTabla) {
    btnRefreshTabla.addEventListener('click', cargarHistorial);
}

if(btnBuscarHistorial) {
    btnBuscarHistorial.addEventListener('click', cargarHistorial);
}
