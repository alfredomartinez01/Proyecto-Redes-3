/* VARIABLES Y CONSTANTES */
let protocolos = null;
const containerRouter = document.querySelector(".selector-router");
const containerProtocolo = document.querySelector(".protocolos");

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

    /* Mostrando la tabla */
    const tabla = document.querySelector("#tabla-protocolos");

    await obtenerProtocolos();
    console.log(protocolos);
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
                <button id="btn-desactivar-rip"
                    class="bg-sky-500 hover:bg-sky-800 text-slate-100 duration-200 font-bold px-2 py-1 rounded-md text-center text-sm mr-2 my-1"
                    onclick="activarProtocolo(${index})"
                    >Activar</button>
                <button id="btn-desactivar-rip"
                    class="bg-sky-500 hover:bg-sky-800 text-slate-100 duration-200 font-bold px-2 py-1 rounded-md text-center text-sm mr-2 my-1"
                    onclick="desactivarProtocolo(${index})"
                    >Desactivar</button>
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

async function activarProtocolo(index) {

}

async function desactivarProtocolo(index) {

}