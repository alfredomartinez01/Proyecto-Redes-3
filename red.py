from router import Router
import logging
import networkx as nx
import matplotlib.pyplot as plt


class Red():

    def __init__(self, ip, name, user="root", password="root"):
        self.ip = ip
        self.name = name
        self.user = user
        self.password = password
        self.routers = {}

    def leerTopologia(self):
        # Obteniendo información de los routers
        router_cercano = Router(self.ip, self.name, self.user, self.password)
        router_cercano.buscarVecinos(self.routers)

        # Generando gráfico
        plt.clf()  # Limpiando imagen
        G = nx.Graph()
        for router in self.routers:  # Agregando routers
            G.add_node(router, name=router)
        for r1 in self.routers:  # Generando conexiones
            for r2 in self.routers[r1]["conectados"]:
                G.add_edge(r1, r2)

        nx.draw_networkx(G, with_labels=True,
                         node_color="g")  # Creando gráfico
        plt.savefig("static/topologia.jpg")

    def obtenerRouters(self):
        return self.routers

    def crearUsuario(self, router, user, password, privilegios):
        if router in self.routers:
            self.routers[router].crearUsuario(user, password, privilegios)
        else:
            if router == "global":
                for router in self.routers:
                    self.routers[router].crearUsuario(user, password, privilegios)
            else:
                raise Exception("Router no encontrado")

    def consultarUsuarios(self, router):
        if router in self.routers:
            return self.routers[router].consultarUsuarios()
        else:
            if router == "global":
                usuarios_cuenta = []
                usuarios = []

                # Obtenermos los usuarios de cada router y los agregamos a una lista con su número de repeticiones
                usuarios_cuenta = {}
                for router in self.routers:
                    usuarios_router = self.routers[router].consultarUsuarios()

                    for member in usuarios_router:
                        cadena_comparar = member["user"] + member["password"] + member["privilegios"]
                        usuarios_cuenta[cadena_comparar] = usuarios_cuenta.get(cadena_comparar, 0) + 1

                    usuarios += usuarios_router

                # Obtenemos los usuarios que se repiten en todos los routers
                usuarios_globales = []
                for usuario_cuenta in usuarios_cuenta:
                    if usuarios_cuenta[usuario_cuenta] == len(self.routers):
                        usuarios_globales.append(usuario_cuenta)

                # Encontramos la información separada de los usuarios globales
                for usuario_global in usuarios_globales:
                    for usuario in usuarios:
                        cadena_comparar = usuario["user"] + usuario["password"] + usuario["privilegios"]
                        if cadena_comparar == usuario_global:
                            usuario["global"] = True
                            break

                return usuarios
            else:
                raise Exception("Router no encontrado")
    
    def eliminarUsuario(self, router, user):
        if router in self.routers:
            self.routers[router].eliminarUsuario(user)
        else:
            if router == "global":
                for router in self.routers:
                    self.routers[router].eliminarUsuario(user)
            else:
                raise Exception("Router no encontrado")     
            
    def actualizarUsuario(self, router, user, password, privilegios):
        if router in self.routers:
            self.routers[router].eliminarUsuario(user)
            self.routers[router].crearUsuario(user, password, privilegios)
        else:
            if router == "global":
                for router in self.routers:
                    self.routers[router].eliminarUsuario(user)
                    self.routers[router].crearUsuario(user, password, privilegios)
            else:
                raise Exception("Router no encontrado")

    def configurarSNMP(self, router):
        if router in self.routers:
            enrutador = Router(self.routers[router]["ip"], router, self.routers[router]["user"], self.routers[router]["password"])
            enrutador.configurarSNMP()
        else:
            raise Exception("Router no encontrado")

    def monitorear(self, router, interfaz, periodo):
        if router in self.routers:
            self.routers[router].monitorear(interfaz, periodo)
        else:
            raise Exception("Router no encontrado")