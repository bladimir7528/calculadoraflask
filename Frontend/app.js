// 1. Definir una constante global para la URL base
const BASE_URL = "http://127.0.0.1:5000"; // Asegúrate que esta URL coincida con la de tu servidor Flask

// 2. Función para visualizar datos en la tabla
function visualizar(data) {
    let tabla = ""; // Inicializa la variable para almacenar el HTML de la tabla

    // Recorre cada elemento en el array "baul" y crea una fila de tabla
    data.baul.forEach(item => {
        tabla += `
        <tr data-id="${item.password_id}">
            <td>${item.password_id}</td>
            <td>${item.platform}</td>
            <td>${item.username}</td>
            <td>********</td> <!-- No mostrar la clave directamente por seguridad -->
            <td>
                <!-- Código del botón Editar -->
                <button type="button" class="btn btn-info"
                    onclick="location.href = 'edit.html?password_id=${item.password_id}'">
                    Editar
                </button>
                <!-- Código del botón Eliminar -->
                <button type="button" class="btn btn-warning"
                    onclick="eliminar(${item.password_id})">
                    Eliminar
                </button>
            </td>
        </tr>
        `;
    });

    // Inserta las filas generadas en el cuerpo de la tabla
    document.getElementById('data').innerHTML = tabla;
}
// Función para realizar una consulta general (GET)
async function consulta_general() {
    try {
        const fetchUrl = `${BASE_URL}/`;
        console.log('Fetching all data from:', fetchUrl); // Log para depuración

        const response = await fetch(fetchUrl); 
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error HTTP! estado: ${response.status}, mensaje: ${errorText}`);
        }
        const data = await response.json();
        visualizar(data); // Muestra los datos en la tabla
    } catch (error) {
        console.error('Error al obtener los datos:', error); // Captura y muestra errores en la consola
        swal("Error de Conexión", "No se pudo conectar con el servidor de la API. Asegúrate de que el servidor Flask esté ejecutándose en " + BASE_URL, "error");
    }
}

// Función para eliminar un registro (DELETE)
async function eliminar(password_id) { 
    const willDelete = await swal({
        title: "¿Estás seguro?",
        text: "Una vez eliminado, ¡no podrás recuperar este registro!",
        icon: "warning",
        buttons: ["Cancelar", "Eliminar"],
        dangerMode: true,
    });

    if (willDelete) {
        try {
            const fetchUrl = `${BASE_URL}/eliminar/${password_id}`;
            console.log('Deleting data from:', fetchUrl); // Log para depuración

            const response = await fetch(fetchUrl, { method: 'DELETE' }); 
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error HTTP! estado: ${response.status}, mensaje: ${errorText}`);
            }
            const res = await response.json();
            swal("Mensaje", `Registro ${res.mensaje} exitosamente`, "success"); // Notificación de éxito
            consulta_general(); // Recarga la tabla de datos
        } catch (error) {
            console.error('Error al eliminar:', error); // Captura y muestra errores en la consola
            swal("Error de Conexión", "No se pudo eliminar el registro. Asegúrate de que el servidor Flask esté ejecutándose.", "error");
        }
    }
}

// Función para registrar un nuevo registro (POST)
async function registrar() {
    const platform = document.getElementById("platform").value; 
    const username = document.getElementById("username").value; 
    const password_value = document.getElementById("password_value").value; 

    const data = {
        platform: platform,
        username: username,
        password_value: password_value
    };

    try {
        const fetchUrl = `${BASE_URL}/registro`;
        console.log('Registering data to:', fetchUrl, 'with data:', data); // Log para depuración

        const response = await fetch(fetchUrl, { 
            method: "POST", 
            body: JSON.stringify(data), 
            headers: {
                "Content-Type": "application/json"
            }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error HTTP! estado: ${response.status}, mensaje: ${errorText}`);
        }
        const res = await response.json();
        if (res.mensaje.includes("Error")) {
            swal("Mensaje", "Error en el registro", "error"); 
        } else {
            swal("Mensaje", "Registro agregado exitosamente", "success").then(() => {
                window.location.href = 'index.html'; // Redirigir al gestor principal
            });
        }
    } catch (error) {
        console.error('Error al registrar:', error); 
        swal("Error de Conexión", "No se pudo registrar el usuario. Asegúrate de que el servidor Flask esté ejecutándose.", "error");
    }
}

// Función para consultar un registro individual (GET)
async function consulta_individual(password_id) { 
    try {
        const fetchUrl = `${BASE_URL}/consulta_indivual/${password_id}`;
        console.log('Fetching individual data from:', fetchUrl); // Log para depuración

        const response = await fetch(fetchUrl); 
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error HTTP! estado: ${response.status}, mensaje: ${errorText}`);
        }
        const data = await response.json();
        
        if (data.baul) {
            document.getElementById("platform").value = data.baul.platform; 
            document.getElementById("username").value = data.baul.username; 
            // Por seguridad, no precargamos la clave. El usuario debe ingresarla si desea cambiarla.
            document.getElementById("password_value").value = ''; 
        } else {
            swal("Error", data.mensaje || "Registro no encontrado", "error");
        }
    } catch (error) {
        console.error('Error al consultar individualmente:', error); 
        swal("Error de Conexión", "No se pudo consultar el registro. Asegúrate de que el servidor Flask esté ejecutándose.", "error");
    }
}

// Función para modificar un registro existente (PUT)
async function modificar(password_id) { 
    const platform = document.getElementById("platform").value; 
    const username = document.getElementById("username").value; 
    const password_value = document.getElementById("password_value").value; 

    // Opcional: Validar si la clave está vacía, ya que el backend siempre la hashea
    if (!platform || !username || !password_value) {
        swal("Advertencia", "Por favor, complete todos los campos.", "warning");
        return;
    }

    const data = {
        platform: platform,
        username: username,
        password_value: password_value
    };

    try {
        const fetchUrl = `${BASE_URL}/actualizar/${password_id}`;
        console.log('Updating data to:', fetchUrl, 'with data:', data); // Log para depuración

        const response = await fetch(fetchUrl, { 
            method: "PUT", 
            body: JSON.stringify(data), 
            headers: {
                "Content-Type": "application/json"
            }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error HTTP! estado: ${response.status}, mensaje: ${errorText}`);
        }
        const res = await response.json();
        
        if (res.mensaje.includes("Error")) {
            swal("Mensaje", "Error al actualizar el registro", "error"); 
        } else {
            swal("Mensaje", "Registro actualizado exitosamente", "success").then(() => {
                window.location.href = 'index.html'; // Redirigir al gestor principal
            });
        }
    } catch (error) {
        console.error('Error al modificar:', error); 
        swal("Error de Conexión", "No se pudo actualizar el registro. Asegúrate de que el servidor Flask esté ejecutándose.", "error");
    }
}
