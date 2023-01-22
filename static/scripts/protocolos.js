/* VARIABLES Y CONSTANTES */
let protocolos = null;
let topologia = null;
const containerProtocolo = document.querySelector(".protocolos");

/* LISTENERS */
// Documento
document.addEventListener('DOMContentLoaded', async () => {
    /* Mostrando la tabla */
    const tabla = document.querySelector("#tabla-protocolos");

    const protocolos = await obtenerProtocolos();

    const activos = protocolos.filter(protocolo => protocolo.estado == "Activo").length;
    tabla.innerHTML = `
        ${protocolos.map((protocolo, index) => `
        <tr class="border-t border-gray-500">
            <td>
                <p class="text-center">${protocolo.nombre}</p>
            </td>
            <td>
                <p class="text-center">${protocolo.estado}</p>
            </td>
            <td>
                ${protocolo.estado != "Activo"
                ? `<button id="btn-activar-protocolo"
                class="bg-sky-500 hover:bg-sky-800 text-slate-100 duration-200 font-bold px-2 py-1 rounded-md text-center text-sm mr-2 my-1"
                onclick="activarProtocolo(${index})"
                >Activar</button>`
                : `${activos > 1
                    ? `<button id="btn-desactivar-protocolo"
                    class="bg-sky-500 hover:bg-sky-800 text-slate-100 duration-200 font-bold px-2 py-1 rounded-md text-center text-sm mr-2 my-1"
                    onclick="desactivarProtocolo(${index})"
                    >Desactivar</button>`
                    : ""
                    }`
                }                
            </td>
        </tr>

        `).join('')}
        `

    containerProtocolo.style.display = "block";
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

async function obtenerProtocolos() {
    try {
        const response = await fetch('/modif-protocolos');
        const data = await response.json();
        console.log(data)
        protocolos = data

    } catch (error) {
        console.log(error)
        protocolos = [
            {
                nombre: "RIP",
                estado: "Activo"
            },
            {
                nombre: "OSPF",
                estado: "Activo"
            },
            {
                nombre: "EIGRP",
                estado: "Activo"
            },
            {
                nombre: "BGP",
                estado: "Inactivo"
            },
        ];
    }
    return protocolos;
    
}

async function activarProtocolo(index) {
    const nombreProtocolo = protocolos[index].nombre;

        try {
            const response = await fetch('/modif-protocolos', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({nombreProtocolo})
            });
            const data= await response.json();
            console.log(data)
            if (data.status == "ok")
                window.location.href = "http://127.0.0.1:5000/protocolos"
        }
        catch {
        }
}

async function desactivarProtocolo(index) {
    const nombreProtocolo = protocolos[index].nombre;

        try {
            const response = await fetch('/modif-protocolos', {
                method: "DELETE",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({nombreProtocolo})
            });
            const data= await response.json();
            console.log(data)
            if (data.status == "ok")
                window.location.href = "http://127.0.0.1:5000/protocolos"
        }
        catch {
        }
}