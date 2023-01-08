/* VARIABLES Y CONSTANTES */
let topologia = null;
let protocolos = null;
const containerRouter = document.querySelector(".selector-router");
const formularioMib = document.querySelector(".info-mib");

/* LISTENERS */
// Documento
document.addEventListener('DOMContentLoaded', async () => {
    await obtenerInfoTopologia();

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
        topologia = routers;
    } catch (error) {

    }
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

async function consultarMIB(router) {
    let infoMibRouter; // Aquí se guardará la información de la MIB del router
    try {
        const response = await fetch(`/mib/${router.name}`);
        const data = await response.json();
        console.log(data);
    } catch (error) {

    }
    return infoMibRouter;
}
