/* VARIABLES Y CONSTANTES */
let topologia = null;
const containerRouter = document.querySelector(".selector-router");
const containerInterfaz = document.querySelector(".selector-interfaz");
const containerPeriodo = document.querySelector(".selector-periodo");
const boton_aceptar = document.querySelector("#btn-aceptar");

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
document.querySelector("#select-router").addEventListener('change', (e) => {
    const router = topologia[e.target.value];

    /* Mostrando las interfaces */
    const selectInterfaz = document.querySelector("#select-interfaz");
    selectInterfaz.innerHTML = `
        <option value="">Selecciona la interfaz</option>
        ${router.interfaces.map((interfaz, index) => `<option value="${index+1}">fas ${interfaz}</option>`).join('')}
    `;

    containerInterfaz.style.display = "block";
});
// Seleccionar interfaz
document.querySelector("#select-interfaz").addEventListener('change', (e) => {
    const selectPeriodo = document.querySelector("#select-periodo");

    containerPeriodo.style.display = "block";
    boton_aceptar.style.display = "block";
});
// Botón aceptar
boton_aceptar.addEventListener('click', async () => {
    // Obteniendo los parámetros del formulario
    const ind_router = document.querySelector("#select-router").value;
    const ind_interfaz = document.querySelector("#select-interfaz").value

    const parametros = {
        router: topologia[ind_router].name,
        interfaz: ind_interfaz,
        periodo: document.querySelector("#select-periodo").value
    };
    console.log(parametros)

    try {
        await monitorear(parametros); // Obtenemos las gráficas

        /* Ocultamos inputs */
        containerRouter.style.display = "none";
        containerInterfaz.style.display = "none";
        containerPeriodo.style.display = "none";
        boton_aceptar.style.display = "none";

        /* Mostramos gráficas */
        setInterval(async ()=>{
            console.log("Consultando...")
            await obtenerGraficas()
            document.querySelector("#imagenes").style.display = "flex";
        }, 3000)

    } catch (error) {
        alert(error);
    }
});


/* FUNCIONES */
async function obtenerInfoTopologia() { // Consultamos la API para obtener la información completa de la topología
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
}

async function monitorear(parametros) { // Consultamos la API para obtener un monitoreo de la interfaz seleccionada
    if (parametros.router == "" || parametros.interfaz == "" || parametros.periodo == "") {
        throw new Error("Debes seleccionar todos los parámetros");
    }

    const response = await fetch(`/monitorear-interfaz`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(parametros)
    });

    console.log(response)
}

async function obtenerGraficas() { // Consultamos la API para obtener las gráficas de la interfaz seleccionada
    const response = await fetch('/paquetes')

    let blob = null;

    // Paquetes
    blob = await response.blob();
    document.querySelector("#paquetes").src = window.URL.createObjectURL(blob);
}