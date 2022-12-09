/* Agregando listeners */
// Documento
document.addEventListener('DOMContentLoaded', cargarTopologia);

async function cargarTopologia() {
    const response = await fetch('/topologia',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'ip': '10.0.1.254',
                'name': 'Enrutador-4',
                'user': 'admin',
                'password': 'admin'
            })
        }
    );
    const data = await response.json();
    console.log(data);
};