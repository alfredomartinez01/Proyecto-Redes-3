/* VARIABLES Y CONSTANTES */
let protocolos = null;
const containerRouter = document.querySelector(".selector-router");
const formularioMib = document.querySelector(".info-mib");

/* LISTENERS */
// Documento
document.addEventListener('DOMContentLoaded', async () => {
    const topologia = await obtenerInfoTopologia();

    /* Mostrando los routers */
    const selectRouter = document.querySelector("#select-router");
    selectRouter.innerHTML = `
        <option value="">Selecciona el router</option>
        ${topologia.map((router, index) => `<option value="${index}">${router.name}</option>`).join('')}
    `;

    containerRouter.style.display = "block";
});
// Select router
document.querySelector("#select-router").addEventListener('change', async (e) => {
    const router = topologia[e.target.value];

    const infoMibRouter = await consultarMIB(router);
    
    /* Mostrando la información */
    document.getElementById("nombre").value = infoMibRouter.nombre;
    document.getElementById("descripcion").value = infoMibRouter.descripcion;
    document.getElementById("contacto").value = infoMibRouter.contacto;
    document.getElementById("localizacion").value = infoMibRouter.localizacion;

    /* Asignando onsumbit al router */
    document.getElementById("info-mib").onsubmit = async (e) => {
        e.preventDefault();
        const info_mib = {
            "nombre": document.getElementById("nombre").value,
            "descripcion": document.getElementById("descripcion").value,
            "contacto": document.getElementById("contacto").value,
            "localizacion": document.getElementById("localizacion").value
        } 

        const nombreRouter = topologia[document.querySelector("#select-router")?.value]?.name ?? "global";
        try {
            const response = await fetch('/mib/' + nombreRouter, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(info_mib)
            });
            const data= await response.json();
            console.log(data)
            if (data.status == "ok")
                window.location.href = "http://127.0.0.1:5000/mib"
        }
        catch {
        }
    }
});


/* FUNCIONES */
async function obtenerInfoTopologia() { // Consultamos la API para obtener la información completa de la topología
    try {
        const response = await fetch('/info-topologia');
        const data = await response.json();

        const routers = []
        for (const router in data) {
            routers.push({
                name: router,
                "ip": data[router]['ip'],
                "interfaces": data[router]['interfaces'] || null
            });
        }
        console.log(routers)
        topologia = routers;

    } catch (error) {
        topologia = [
            {
                name: "R1",
                ip: "192.168.0.5",
                interfaces: [1, 2, 3, 4]
            },
            {
                name: "R2",
                ip: "192.168.0.1",
                interfaces: [1, 2, 3, 4]
            },
            {
                name: "R3",
                ip: "192.168.0.15",
                interfaces: [1, 2, 3, 4]
            },
        ];
    }
    return topologia;
}

async function consultarMIB(router) {
    let infoMibRouter; // Aquí se guardará la información de la MIB del router
    try {
        const response = await fetch(`/mib/${router.name}`);
        const data = await response.json();
        console.log(data);
        infoMibRouter = data
    } catch (error) {

    }
    return infoMibRouter;
}
