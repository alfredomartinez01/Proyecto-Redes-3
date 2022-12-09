/* LISTENERS */
// Documento
document.addEventListener('DOMContentLoaded', cargarTopologia);

/* FUNCIONES */
async function cargarTopologia() { // Consultamos la API para obtener la topologia
    const response = await fetch('/topologia',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'ip': '10.0.1.254',
                'name': 'Enrutador-4',
                'user': 'root',
                'password': 'root'
            })
        }
    );
    // Obtenemos la imagen y la asignamos
    const blob = await response.blob();
    document.querySelector("#imagen-topologia").src = window.URL.createObjectURL(blob);
};
