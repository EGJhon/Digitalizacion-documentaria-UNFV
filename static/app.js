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

// ---------------- LÓGICA: GESTIÓN DE USUARIOS ----------------
const userForm = document.getElementById('userForm');
const selectRol = document.getElementById('u_role_id');
const tablaUsuariosBody = document.getElementById('tablaUsuariosBody');
const userMsg = document.getElementById('userMsg');

async function cargarRoles() {
    if(!selectRol) return;
    try {
        const res = await fetch("/api/v1/users/roles");
        if (res.ok) {
            const roles = await res.json();
            selectRol.innerHTML = '<option value="">Seleccione un rol...</option>';
            roles.forEach(r => {
                selectRol.innerHTML += `<option value="${r.id}">${r.nombre}</option>`;
            });
        }
    } catch (e) {
        console.error("Error al cargar roles", e);
    }
}

async function cargarUsuarios() {
    if(!tablaUsuariosBody) return;
    try {
        const res = await fetch("/api/v1/users/");
        if (res.ok) {
            const usuarios = await res.json();
            if(usuarios.length === 0) {
                tablaUsuariosBody.innerHTML = '<tr><td colspan="3" style="text-align: center;">No hay usuarios.</td></tr>';
                return;
            }
            let filas = '';
            usuarios.forEach(u => {
                filas += `
                    <tr>
                        <td>${u.id}</td>
                        <td>${u.username}</td>
                        <td>${u.role_id}</td>
                    </tr>
                `;
            });
            tablaUsuariosBody.innerHTML = filas;
        }
    } catch (e) {
        console.error("Error al cargar usuarios", e);
    }
}

if(userForm) {
    userForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const role_id = document.getElementById('u_role_id').value;
        const username = document.getElementById('u_username').value;
        const password = document.getElementById('u_password').value;

        try {
            const res = await fetch("/api/v1/users/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ role_id: parseInt(role_id), username, password })
            });

            if (res.ok) {
                userMsg.textContent = "Usuario creado exitosamente";
                userMsg.style.color = "green";
                userForm.reset();
                cargarUsuarios();
            } else {
                const err = await res.json();
                userMsg.textContent = err.detail || "Error al crear usuario";
                userMsg.style.color = "red";
            }
        } catch (error) {
            userMsg.textContent = "Error de conexión";
            userMsg.style.color = "red";
        }
    });
}

// Interceptar clicks de menú para cargar datos de usuarios
menuLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        const targetId = e.currentTarget.getAttribute('data-target');
        if(targetId === 'usuariosPanel') {
            cargarRoles();
            cargarUsuarios();
        }
    });
});

// ---------------- LÓGICA: CAMBIAR CONTRASEÑA ----------------
const btnCambiarClave = document.getElementById('btnCambiarClave');
const modalCambiarClave = document.getElementById('modalCambiarClave');
const btnCloseModalClave = document.getElementById('btnCloseModalClave');
const formCambiarClave = document.getElementById('formCambiarClave');
const msgCambiarClave = document.getElementById('msgCambiarClave');

if (btnCambiarClave) {
    btnCambiarClave.addEventListener('click', () => {
        modalCambiarClave.classList.remove('hidden');
        msgCambiarClave.textContent = '';
        if(formCambiarClave) formCambiarClave.reset();
    });
}

if (btnCloseModalClave) {
    btnCloseModalClave.addEventListener('click', () => {
        modalCambiarClave.classList.add('hidden');
    });
}

if (formCambiarClave) {
    formCambiarClave.addEventListener('submit', async (e) => {
        e.preventDefault();
        const old_password = document.getElementById('old_password').value;
        const new_password = document.getElementById('new_password').value;
        const current_username = localStorage.getItem('unfv_username');

        if (!current_username) {
            msgCambiarClave.textContent = 'Error: No se encontró el usuario actual.';
            msgCambiarClave.style.color = 'red';
            return;
        }

        try {
            const res = await fetch('/api/v1/users/password', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: current_username,
                    old_password: old_password,
                    new_password: new_password
                })
            });

            if (res.ok) {
                msgCambiarClave.textContent = 'Contraseña actualizada exitosamente.';
                msgCambiarClave.style.color = 'green';
                setTimeout(() => {
                    modalCambiarClave.classList.add('hidden');
                }, 1500);
            } else {
                const err = await res.json();
                msgCambiarClave.textContent = err.detail || 'Error al cambiar contraseña.';
                msgCambiarClave.style.color = 'red';
            }
        } catch (error) {
            msgCambiarClave.textContent = 'Error de conexión.';
            msgCambiarClave.style.color = 'red';
        }
    });
}
