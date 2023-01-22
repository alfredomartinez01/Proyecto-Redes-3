/* VARIABLES Y CONSTANTES */
const containerRouter = document.querySelector(".selector-router");
const containerUsuarios = document.querySelector(".usuarios");
let usuarios = null;

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
    selectRouter.innerHTML += "<option value='global'>Global</option>"

    containerRouter.style.display = "block";
});
// Select router
document.querySelector("#select-router").addEventListener('change', async (e) => {
    const router = topologia[e.target.value];

    /* Mostrando la tabla */
    const tabla = document.querySelector("#tabla-usuarios");

    const usuarios = await obtenerUsuarios(router?.name ?? "global");
    tabla.innerHTML = `
        ${usuarios.map((usuario, index) => `
        <tr class="border-t border-gray-500">
            <td>
                <p class="text-center">${usuario.user}</p>
            </td>
            <td>
                <p class="text-center">${usuario.password}</p>
            </td>
            <td>
                <p class="text-center">${usuario.privilegios}</p>
            </td>
            <td>
                ${index != 0 
                    ? `<button id="btn-editar"
                class="bg-sky-500 hover:bg-sky-800 text-slate-100 duration-200 font-bold px-2 py-1 rounded-md text-center text-sm mr-2 my-1"
                onclick="editarUsuario(${index})"
                >Editar</button>`
                :""}
                
            </td>
        </tr>

        `).join('')}
        `

    containerUsuarios.style.display = "block";
    document.getElementById("info-usuario").style.display = "block";
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

async function obtenerUsuarios(nombreRouter) {
    try {
        const response = await fetch('/usuarios/' + nombreRouter);
        const data = await response.json();
        usuarios = data
    }
    catch {
        usuarios = [
            {
                user: "root",
                password: "root",
                privilegios: "0"
            }, {
                user: "admin",
                password: "admin",
                privilegios: "1"
            },
        ];
    }
    return usuarios
}

async function editarUsuario(index) {
    const usuario = usuarios[index]
    document.getElementById("nombre").value = usuario.user;
    document.getElementById("contrasena").value = usuario.password;
    document.getElementById("privilegios").value = usuario.privilegios;

    document.getElementById("btn-guardar").textContent = "Actualizar";
    const eliminar = document.getElementById("btn-eliminar")
    const formulario = document.getElementById("info-usuario")
    formulario.style.display = "block";
    eliminar.style.display = "block";

    eliminar.onclick = async (e) => {
        const user = usuarios[index].user
        const nombreRouter = topologia[document.querySelector("#select-router")?.value]?.name ?? "global";
        try {
            const response = await fetch('/usuarios/' + nombreRouter, {
                method: "DELETE",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({user})
            });
            const data= await response.json();
            console.log(data)
            if (data.status == "ok")
                window.location.href = "http://127.0.0.1:5000/usuarios"
        }
        catch {
        }
    }

    formulario.onsubmit = async (e) => {
        e.preventDefault();
        const usuario = {
            "user": usuarios[index].user,
            "new_user": document.getElementById("nombre").value,
            "password": document.getElementById("contrasena").value,
            "privilegios": document.getElementById("privilegios").value
        } 

        const nombreRouter = topologia[document.querySelector("#select-router")?.value]?.name ?? "global";
        try {
            const response = await fetch('/usuarios/' + nombreRouter, {
                method: "PUT",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(usuario)
            });
            const data= await response.json();
            console.log(data)
            if (data.status == "ok")
                window.location.href = "http://127.0.0.1:5000/usuarios"
        }
        catch {
        }
    }
} 

document.querySelector("#info-usuario").addEventListener('submit', async (e) => {
        e.preventDefault();
        const usuario = {
            "user": document.getElementById("nombre").value,
            "password": document.getElementById("contrasena").value,
            "privilegios": document.getElementById("privilegios").value
        }

        const nombreRouter = topologia[document.querySelector("#select-router")?.value]?.name ?? "global";
        try {
            const response = await fetch('/usuarios/' + nombreRouter, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(usuario)
            });
            const data= await response.json();
            console.log(data)
            if (data.status == "ok")
                window.location.href = "http://127.0.0.1:5000/usuarios"
        }
        catch {
        }
    
});