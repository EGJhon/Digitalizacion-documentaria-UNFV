
// Helper para dar formato a Lugar y Fecha
function formatLugarFecha(lugarId, fechaId) {
    const lugar = document.getElementById(lugarId)?.value?.trim() || '';
    const fechaVal = document.getElementById(fechaId)?.value;
    if (!fechaVal) return lugar;
    const parts = fechaVal.split('-');
    if (parts.length !== 3) return lugar;
    const meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
    const dia = parseInt(parts[2], 10);
    const mes = meses[parseInt(parts[1], 10) - 1];
    const anio = parts[0];
    const fechaStr = `${dia} de ${mes} de ${anio}`;
    return lugar ? `${lugar}, ${fechaStr}` : fechaStr;
}


window.downloadSecurePdf = async function(url) {
    try {
        const res = await window.apiFetch(url);
        if (!res.ok) {
            alert("No tienes permiso para ver este documento o no existe.");
            return;
        }
        const blob = await res.blob();
        const blobUrl = URL.createObjectURL(blob);
        window.open(blobUrl, '_blank');
    } catch (e) {
        console.error(e);
        alert("Error de conexión al abrir el documento.");
    }
};


window.apiFetch = async function(url, options = {}) {
    options.headers = options.headers || {};
    const token = localStorage.getItem("unfv_token");
    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }
    return fetch(url, options);
};

// Elementos UI Compartidos
const resultGlobalPanel = document.getElementById('resultGlobalPanel');
const globalSuccessMsg = document.getElementById('globalSuccessMsg');
const globalResId = document.getElementById('globalResId');
const globalResCodigo = document.getElementById('globalResCodigo');

// Check role and show Usuarios menu if admin
const userRoleId = localStorage.getItem('unfv_role_id');
const username = localStorage.getItem('unfv_username');

if (userRoleId === "1") {
    const menuUsuarios = document.getElementById('menuUsuarios');
    if (menuUsuarios) menuUsuarios.classList.remove('hidden');
    
    const menuAuditoria = document.getElementById('menuAuditoria');
    if (menuAuditoria) menuAuditoria.classList.remove('hidden');
}

if (username) {
    const topbarUserRole = document.getElementById('topbarUserRole');
    const topbarUserAvatar = document.getElementById('topbarUserAvatar');
    if (topbarUserRole) {
        topbarUserRole.textContent = userRoleId === "1" ? "Admin Panel" : "Panel Usuario";
    }
    if (topbarUserAvatar) {
        topbarUserAvatar.textContent = username.substring(0, 2).toUpperCase();
        topbarUserAvatar.title = username;
    }
}

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
        
        // Si entramos a auditoría, cargar logs
        if(targetId === 'auditoriaPanel') {
            cargarAuditoria();
        }
    });
});

// Función genérica para enviar datos (POST /generar)
async function guardarDocumento(data, formElement) {
    try {
        const res = await window.apiFetch("/api/v1/generar/oficio", {
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
            lugar_fecha: formatLugarFecha('c_lugar', 'c_fecha'),
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
            copia: document.getElementById('c_copia').value,
            usuario_id: parseInt(localStorage.getItem('unfv_user_id')) || null
        };
        guardarDocumento(data, docFormCrear);
    });
}

const btnPrevisualizarCrear = document.getElementById('btnPrevisualizarCrear');
if(btnPrevisualizarCrear) {
    btnPrevisualizarCrear.addEventListener('click', async () => {
        if (!docFormCrear.checkValidity()) {
            docFormCrear.reportValidity();
            return;
        }
        
        const data = {
            lema_anio: document.getElementById('c_lema_anio').value,
            lugar_fecha: formatLugarFecha('c_lugar', 'c_fecha'),
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
            copia: document.getElementById('c_copia').value,
            usuario_id: parseInt(localStorage.getItem('unfv_user_id')) || null
        };
        
        try {
            const btnOriginalText = btnPrevisualizarCrear.innerHTML;
            btnPrevisualizarCrear.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
            
            const res = await window.apiFetch("/api/v1/generar/oficio/preview", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            
            btnPrevisualizarCrear.innerHTML = btnOriginalText;
            
            if (res.ok) {
                const html = await res.text();
                const iframe = document.getElementById('previewIframeCrear');
                iframe.srcdoc = html;
            } else {
                const err = await res.json();
                alert("Error al previsualizar: " + JSON.stringify(err));
            }
        } catch (e) {
            alert("Error de conexión al servidor.");
            btnPrevisualizarCrear.innerHTML = '<i class="fas fa-eye"></i> Previsualizar';
        }
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
        const currentUserId = localStorage.getItem('unfv_user_id');
        if (currentUserId) {
            formData.append("usuario_id", currentUserId);
        }

        const tipo = document.getElementById('tipoDigitalizarSelect')?.value || 'oficio';

        try {
            const res = await window.apiFetch(`/api/v1/extraer/${tipo}`, {
                method: "POST",
                body: formData
            });
            
            if (res.ok) {
                const data = await res.json();
                ocrMsg.textContent = "¡Datos extraídos con éxito! Revisalos abajo.";
                
                formularioRevisionContainer.classList.remove('hidden');
                
                if (tipo === 'oficio') {
                    document.getElementById('docFormDigitalizar').classList.remove('hidden');
                    const formRes = document.getElementById('docFormDigitalizarResolucion');
                    if(formRes) formRes.classList.add('hidden');
                    
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
                } else if (tipo === 'resolucion') {
                    document.getElementById('docFormDigitalizar').classList.add('hidden');
                    const formRes = document.getElementById('docFormDigitalizarResolucion');
                    if(formRes) formRes.classList.remove('hidden');
                    
                    document.getElementById('dr_lema_anio').value = data.datos_sugeridos.lema_anio || "";
                    document.getElementById('dr_lugar_fecha').value = data.datos_sugeridos.lugar_fecha || "";
                    document.getElementById('dr_nro_resolucion').value = data.datos_sugeridos.nro_resolucion || "";
                    document.getElementById('dr_vistos_texto').value = data.datos_sugeridos.vistos_texto || "";
                    document.getElementById('dr_considerandos').value = (data.datos_sugeridos.considerandos || []).join("\n");
                    document.getElementById('dr_parrafo_previo_resuelve').value = data.datos_sugeridos.parrafo_previo_resuelve || "";
                    document.getElementById('dr_articulos').value = (data.datos_sugeridos.articulos || []).map(a => `${a.numero}|${a.texto}`).join("\n");
                    document.getElementById('dr_texto_cierre').value = data.datos_sugeridos.texto_cierre || "";
                    document.getElementById('dr_secretario_nombre').value = data.datos_sugeridos.secretario_nombre || "";
                    document.getElementById('dr_rectora_nombre').value = data.datos_sugeridos.rectora_nombre || "";
                }
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
            copia: document.getElementById('d_copia').value,
            usuario_id: parseInt(localStorage.getItem('unfv_user_id')) || null
        };
        guardarDocumento(data, docFormDigitalizar);
    });
}

// ---------------- LÓGICA: HISTORIAL / TABLA ----------------
const btnRefreshTabla = document.getElementById('btnRefreshTabla');
const btnBuscarHistorial = document.getElementById('btnBuscarHistorial');

if(btnBuscarHistorial) {
    btnBuscarHistorial.addEventListener('click', cargarHistorial);
}
if(btnRefreshTabla) {
    btnRefreshTabla.addEventListener('click', cargarHistorial);
}

const tablaOficiosBody = document.getElementById('tablaOficiosBody');

async function cargarHistorial() {
    if(!tablaOficiosBody) return;
    tablaOficiosBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Cargando registros...</td></tr>';
    
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
        const res = await window.apiFetch(`/api/v1/generar/documentos?${params.toString()}`);
        if(res.ok) {
            const data = await res.json();
            if(data.length === 0) {
                tablaOficiosBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No hay documentos registrados aún.</td></tr>';
                return;
            }
            
            // Save data globally to use in Modal
            window.documentosHistorialData = data;
            
            tablaOficiosBody.innerHTML = '';
            data.forEach((doc, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight:600;">${doc.id_maestro}</td>
                    <td style="font-family:monospace;">${doc.codigo_unico.substring(0,8)}...</td>
                    <td><span class="badge badge-primary">${doc.tipo_documento}</span></td>
                    <td>
                        <span style="font-size: 0.85rem; color: #555;">
                            ${doc.tipo_documento.toLowerCase() === 'oficio' ? (doc.campos_especificos?.asunto ? 'Asunto: ' + doc.campos_especificos.asunto : 'N/A') :
                              doc.tipo_documento.toLowerCase() === 'resolucion' ? (doc.campos_especificos?.nro_resolucion ? 'Nro. Res: ' + doc.campos_especificos.nro_resolucion : 'N/A') :
                              'N/A'}
                        </span>
                    </td>
                    <td>${doc.fecha_registro}</td>
                    <td><span class="badge badge-success">${doc.estado.toUpperCase()}</span></td>
                    <td>
                        <button class="btn btn-blue" style="padding: 4px 8px; font-size: 0.85rem;" onclick="abrirModalDetalles(${index})"><i class="fas fa-eye"></i> Detalles</button>
                        <button onclick="window.downloadSecurePdf('${doc.pdf_url}')" class="btn btn-orange" style="padding: 4px 8px; font-size: 0.85rem; text-decoration: none; display: inline-block; margin-left: 5px;"><i class="fas fa-file-pdf"></i></button>
                    </td>
                `;
                tablaOficiosBody.appendChild(tr);
            });
        } else {
            tablaOficiosBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: red;">Error al cargar historial</td></tr>';
        }
    } catch (e) {
        tablaOficiosBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: red;">Error de conexión</td></tr>';
    }
}

// ---- LOGICA MODAL DETALLES ----
const detallesModal = document.getElementById('detallesModal');
const btnCerrarModal = document.getElementById('btnCerrarModal');
const closeModalBtn = document.getElementById('closeModalBtn');
const modalDetallesBody = document.getElementById('modalDetallesBody');

function abrirModalDetalles(index) {
    const doc = window.documentosHistorialData[index];
    if(!doc) return;
    
    let html = '';
    const campos = doc.campos_especificos || {};
    
    // Convert object properties to friendly rows
    for(const key in campos) {
        if(campos[key]) {
            const label = key.replace(/_/g, ' ').toUpperCase();
            html += `
            <div class="detalle-row">
                <span class="detalle-label">${label}:</span>
                <span class="detalle-value">${campos[key]}</span>
            </div>
            `;
        }
    }
    
    if(html === '') {
        html = '<p style="color:#888;">No hay campos específicos registrados para este documento.</p>';
    }
    
    modalDetallesBody.innerHTML = html;
    detallesModal.classList.remove('hidden');
}

function cerrarModal() {
    detallesModal.classList.add('hidden');
}

if(btnCerrarModal) btnCerrarModal.addEventListener('click', cerrarModal);
if(closeModalBtn) closeModalBtn.addEventListener('click', cerrarModal);



async function cargarAuditoria() {
    const tablaAuditoriaBody = document.getElementById('tablaAuditoriaBody');
    if(!tablaAuditoriaBody) return;
    
    tablaAuditoriaBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Cargando logs...</td></tr>';
    
    const fechaInicio = document.getElementById('filtroAuditoriaInicio')?.value || '';
    const fechaFin = document.getElementById('filtroAuditoriaFin')?.value || '';
    
    const params = new URLSearchParams();
    if(fechaInicio) params.append('fecha_inicio', fechaInicio);
    if(fechaFin) params.append('fecha_fin', fechaFin);
    
    try {
        const res = await window.apiFetch(`/api/v1/auditoria/logs?${params.toString()}`);
        if(res.ok) {
            const logs = await res.json();
            window.auditoriaLogsData = logs; // Guardar globalmente para exportación
            if(logs.length === 0) {
                tablaAuditoriaBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No hay registros de auditoría.</td></tr>';
                return;
            }
            
            tablaAuditoriaBody.innerHTML = '';
            logs.forEach(log => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${log.fecha_accion}</td>
                    <td style="font-weight: 500;">${log.usuario}</td>
                    <td><span class="badge badge-${log.accion === 'CREAR' ? 'success' : 'primary'}">${log.accion}</span></td>
                    <td>${log.modulo}</td>
                    <td>${log.detalles || ''}</td>
                `;
                tablaAuditoriaBody.appendChild(tr);
            });
        } else {
            tablaAuditoriaBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: red;">Error al cargar logs</td></tr>';
        }
    } catch (e) {
        tablaAuditoriaBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: red;">Error de conexión</td></tr>';
    }
}

document.getElementById('btnFiltrarAuditoria')?.addEventListener('click', cargarAuditoria);

document.getElementById('btnDescargarAuditoria')?.addEventListener('click', () => {
    const logs = window.auditoriaLogsData || [];
    if(logs.length === 0) {
        alert("No hay datos para exportar.");
        return;
    }
    
    // Crear CSV
    let csvContent = "Fecha y Hora,Usuario,Accion,Modulo,Detalles\n";
    logs.forEach(log => {
        let det = log.detalles || "";
        det = det.replace(/"/g, '""'); // Escapar comillas dobles
        if (det.includes(',') || det.includes('\\n')) {
            det = `"${det}"`; // Envolver en comillas si hay comas o saltos de línea
        }
        
        csvContent += `${log.fecha_accion},${log.usuario},${log.accion},${log.modulo},${det}\n`;
    });
    
    // Crear enlace de descarga
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "auditoria_logs.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// -----------------------------------------
// GESTION DE USUARIOS
// -----------------------------------------
const userForm = document.getElementById('userForm');
const u_role_id = document.getElementById('u_role_id');
const tablaUsuariosBody = document.getElementById('tablaUsuariosBody');
const userMsg = document.getElementById('userMsg');

async function cargarRoles() {
    if(!u_role_id) return;
    try {
        const res = await window.apiFetch('/api/v1/users/roles');
        if(res.ok) {
            const roles = await res.json();
            u_role_id.innerHTML = '';
            roles.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r.id;
                opt.textContent = r.nombre.toUpperCase();
                u_role_id.appendChild(opt);
            });
        }
    } catch(e) {
        console.error(e);
        u_role_id.innerHTML = '<option value="">Error cargando roles</option>';
    }
}

async function cargarUsuarios() {
    if(!tablaUsuariosBody) return;
    try {
        const res = await window.apiFetch('/api/v1/users/');
        if(res.ok) {
            const usuarios = await res.json();
            tablaUsuariosBody.innerHTML = '';
            usuarios.forEach(u => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${u.id}</td>
                    <td>${u.username}</td>
                    <td>${u.role_id}</td>
                `;
                tablaUsuariosBody.appendChild(tr);
            });
        }
    } catch(e) {
        console.error(e);
        tablaUsuariosBody.innerHTML = '<tr><td colspan="3" style="color:red; text-align:center;">Error cargando usuarios</td></tr>';
    }
}

if(userForm) {
    userForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('u_username').value;
        const password = document.getElementById('u_password').value;
        const role_id = document.getElementById('u_role_id').value;

        try {
            const res = await window.apiFetch('/api/v1/users/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password, role_id: parseInt(role_id)})
            });
            
            if(res.ok) {
                userMsg.textContent = "Usuario creado exitosamente.";
                userMsg.style.color = "green";
                userForm.reset();
                cargarUsuarios();
            } else {
                const err = await res.json();
                userMsg.textContent = err.detail || "Error al crear usuario.";
                userMsg.style.color = "red";
            }
        } catch(e) {
            userMsg.textContent = "Error de conexión.";
            userMsg.style.color = "red";
        }
    });
}

// Inicializar funciones de usuarios
document.addEventListener('DOMContentLoaded', () => {
    // Si estamos logueados y somos admin, cargamos roles y usuarios
    const roleId = localStorage.getItem('unfv_role_id');
    if(roleId == 1) { // 1 = admin
        cargarRoles();
        cargarUsuarios();
    }
});

// -----------------------------------------
// CAMBIAR CONTRASEÑA
// -----------------------------------------
const menuCambiarClave = document.getElementById('menuCambiarClave');
const modalCambiarClave = document.getElementById('modalCambiarClave');
const btnCloseModalClave = document.getElementById('btnCloseModalClave');
const formCambiarClave = document.getElementById('formCambiarClave');
const msgCambiarClave = document.getElementById('msgCambiarClave');

if(menuCambiarClave) {
    menuCambiarClave.addEventListener('click', (e) => {
        e.preventDefault();
        modalCambiarClave.classList.remove('hidden');
        modalCambiarClave.style.display = 'flex';
    });
}

if(btnCloseModalClave) {
    btnCloseModalClave.addEventListener('click', () => {
        modalCambiarClave.classList.add('hidden');
        modalCambiarClave.style.display = 'none';
        formCambiarClave.reset();
        msgCambiarClave.textContent = '';
    });
}

if(formCambiarClave) {
    formCambiarClave.addEventListener('submit', async (e) => {
        e.preventDefault();
        const old_password = document.getElementById('old_password').value;
        const new_password = document.getElementById('new_password').value;
        const username = localStorage.getItem('unfv_username');
        
        try {
            const res = await window.apiFetch('/api/v1/users/password', {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, old_password, new_password})
            });
            
            if(res.ok) {
                msgCambiarClave.textContent = "Contraseña actualizada exitosamente.";
                msgCambiarClave.style.color = "green";
                setTimeout(() => {
                    modalCambiarClave.classList.add('hidden');
                    modalCambiarClave.style.display = 'none';
                    formCambiarClave.reset();
                    msgCambiarClave.textContent = '';
                }, 1500);
            } else {
                const err = await res.json();
                msgCambiarClave.textContent = err.detail || "Error al actualizar contraseña.";
                msgCambiarClave.style.color = "red";
            }
        } catch(e) {
            msgCambiarClave.textContent = "Error de conexión.";
            msgCambiarClave.style.color = "red";
        }
    });
}



document.getElementById('btnPrevisualizarResolucion')?.addEventListener('click', async () => {
    const r_origen = document.getElementById('r_origen')?.value || 'manual';
    if(r_origen === 'ia') {
        alert("En modo extracción IA, primero guarde y genere el PDF final.");
        return;
    }
    
    const datosDict = {
        nro_resolucion: document.getElementById('r_nro_resolucion').value,
        lema_anio: document.getElementById('r_lema_anio').value,
        lugar_fecha: formatLugarFecha('r_lugar', 'r_fecha'),
        vistos_texto: document.getElementById('r_vistos_texto').value,
        considerandos: document.getElementById('r_considerandos').value,
        parrafo_previo_resuelve: document.getElementById('r_parrafo_previo_resuelve').value,
        articulos: document.getElementById('r_articulos').value,
        texto_cierre: document.getElementById('r_texto_cierre').value,
        secretario_nombre: document.getElementById('r_secretario_nombre').value,
        rectora_nombre: document.getElementById('r_rectora_nombre').value,
    };

    try {
        const token = localStorage.getItem("unfv_token");
        const res = await fetch('/api/v1/generar/resolucion/preview', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(datosDict)
        });

        if (res.ok) {
            const html = await res.text();
            const iframe = document.getElementById('previewIframeCrear');
            iframe.contentWindow.document.open();
            iframe.contentWindow.document.write(html);
            iframe.contentWindow.document.close();
        } else {
            const error = await res.json();
            alert("Error: " + error.detail);
        }
    } catch (e) {
        console.error(e);
        alert("Error de conexión al servidor.");
    }
});


document.getElementById('docFormResolucion')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const token = localStorage.getItem("unfv_token");
    if (!token) {
        alert("Sesión expirada. Por favor inicie sesión nuevamente.");
        return;
    }
    
    const datosDict = {
        nro_resolucion: document.getElementById('r_nro_resolucion').value,
        lema_anio: document.getElementById('r_lema_anio').value,
        lugar_fecha: formatLugarFecha('r_lugar', 'r_fecha'),
        vistos_texto: document.getElementById('r_vistos_texto').value,
        considerandos: document.getElementById('r_considerandos').value,
        parrafo_previo_resuelve: document.getElementById('r_parrafo_previo_resuelve').value,
        articulos: document.getElementById('r_articulos').value,
        texto_cierre: document.getElementById('r_texto_cierre').value,
        secretario_nombre: document.getElementById('r_secretario_nombre').value,
        rectora_nombre: document.getElementById('r_rectora_nombre').value,
    };
    
    const formData = new FormData();
    formData.append('datos', JSON.stringify(datosDict));
    
    const fileInput = document.getElementById('r_adjuntoPdf');
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        if (file.size > 10 * 1024 * 1024) { // 10 MB limit
            alert("El PDF adjunto supera los 10MB permitidos.");
            return;
        }
        formData.append('adjuntoPdf', file);
    }
    
    try {
        const res = await fetch('/api/v1/generar/resolucion', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            alert("¡Resolución generada correctamente!");
            
            const iframe = document.getElementById('previewIframeCrear');
            window.downloadSecurePdf(data.pdf_url).then(blob => {
                if (blob) {
                    const objectUrl = URL.createObjectURL(blob);
                    iframe.src = objectUrl;
                }
            });
            
            e.target.reset();
        } else {
            const error = await res.json();
            alert("Error: " + error.detail);
        }
    } catch (e) {
        console.error(e);
        alert("Error de conexión.");
    }
});


// Toggle visibility of forms for Oficio / Resolucion
document.getElementById('tipoCrearSelect')?.addEventListener('change', (e) => {
    if (e.target.value === 'oficio') {
        document.getElementById('docFormCrear').classList.remove('hidden');
        const resForm = document.getElementById('docFormResolucion');
        if(resForm) resForm.classList.add('hidden');
    } else if (e.target.value === 'resolucion') {
        document.getElementById('docFormCrear').classList.add('hidden');
        const resForm = document.getElementById('docFormResolucion');
        if(resForm) resForm.classList.remove('hidden');
    }
});


// Toggle form when changing Digitalizar select
document.getElementById('tipoDigitalizarSelect')?.addEventListener('change', (e) => {
    // Hide revision container until extraction
    document.getElementById('formularioRevisionContainer').classList.add('hidden');
});


document.getElementById('docFormDigitalizarResolucion')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const token = localStorage.getItem("unfv_token");
    if (!token) {
        alert("Sesión expirada. Por favor inicie sesión nuevamente.");
        return;
    }
    
    const datosDict = {
        nro_resolucion: document.getElementById('dr_nro_resolucion').value,
        lema_anio: document.getElementById('dr_lema_anio').value,
        lugar_fecha: document.getElementById('dr_lugar_fecha').value,
        vistos_texto: document.getElementById('dr_vistos_texto').value,
        considerandos: document.getElementById('dr_considerandos').value,
        parrafo_previo_resuelve: document.getElementById('dr_parrafo_previo_resuelve').value,
        articulos: document.getElementById('dr_articulos').value,
        texto_cierre: document.getElementById('dr_texto_cierre').value,
        secretario_nombre: document.getElementById('dr_secretario_nombre').value,
        rectora_nombre: document.getElementById('dr_rectora_nombre').value,
    };
    
    const formData = new FormData();
    formData.append('datos', JSON.stringify(datosDict));
    
    const fileInput = document.getElementById('dr_adjuntoPdf');
    if (fileInput && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        if (file.size > 10 * 1024 * 1024) {
            alert("El PDF adjunto supera los 10MB permitidos.");
            return;
        }
        formData.append('adjuntoPdf', file);
    }
    
    try {
        const res = await fetch('/api/v1/generar/resolucion', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (res.ok) {
            alert("¡Resolución generada correctamente a partir de los datos extraídos!");
            document.getElementById('formularioRevisionContainer').classList.add('hidden');
            e.target.reset();
            // Reset file viewer if needed
        } else {
            const error = await res.json();
            alert("Error: " + error.detail);
        }
    } catch (err) {
        console.error(err);
        alert("Error de conexión al guardar.");
    }
});
