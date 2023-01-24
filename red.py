from router import Router
import logging
import networkx as nx
import matplotlib.pyplot as plt
import json

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
        plt.figure(figsize=(10, 7))
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

    def crearUsuario(self, router, user, privilegios, password):
        if router in self.routers:
            router_arreglo = self.routers[router]
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            router_cercano.crearUsuario(user, privilegios, password)
            
        else:
            if router == "global":
                for router in self.routers:
                    router_arreglo = self.routers[router]
                    router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
                    router_cercano.crearUsuario(user, privilegios, password)
            else:
                raise Exception("Router no encontrado")

    def consultarUsuarios(self, router):
        if router in self.routers:
            router_arreglo = self.routers[router]
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            return router_cercano.consultarUsuarios()
        else:
            if router == "global":
                usuarios_cuenta = []
                usuarios = []

                # Obtenermos los usuarios de cada router y los agregamos a una lista con su número de repeticiones
                usuarios_cuenta = {}
                for router in self.routers:
                    router_arreglo = self.routers[router]
                    router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])

                    usuarios_router = router_cercano.consultarUsuarios()

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

                return [usuario for usuario in usuarios if usuario.get("global", False)==True]
            else:
                raise Exception("Router no encontrado")
    
    def eliminarUsuario(self, router, user):
        if router in self.routers:
            router_arreglo = self.routers[router]
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            if len(router_cercano.consultarUsuarios()) > 1:
                router_cercano.eliminarUsuario(user)
        else:
            if router == "global":
                for router in self.routers:
                    router_arreglo = self.routers[router]
                    router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
                    
                    if len(router_cercano.consultarUsuarios()) <= 1:
                        return
                
                for router in self.routers:
                    router_arreglo = self.routers[router]
                    router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
                    router_cercano.eliminarUsuario(user)

            else:
                raise Exception("Router no encontrado")     
            
    def actualizarUsuario(self, router, user, new_user, privilegios, password):
        if router in self.routers:
            router_arreglo = self.routers[router]
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            
            router_cercano.actualizarUsuario(user, new_user, privilegios, password)
        else:
            if router == "global":
                for router in self.routers:
                    router_arreglo = self.routers[router]
                    router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            
                    router_cercano.actualizarUsuario(user, new_user, privilegios, password)
            else:
                raise Exception("Router no encontrado")

    def configurarSNMPV3(self, router):
        if router in self.routers:
            router_arreglo = self.routers[router]
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            router_cercano.configurarSNMPV3()
        else:
            raise Exception("Router no encontrado")
    
    def consultarMIB(self, router):
        if router in self.routers:
            router_arreglo = self.routers[router]
            logging.debug(router_arreglo)
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            return router_cercano.consultarMIB()
        else:
            raise Exception("Router no encontrado")

    def modificarMIB(self, router, nombre, descripcion, contacto, localizacion):
        if router in self.routers:
            router_arreglo = self.routers[router]
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            return router_cercano.modificarMIB(nombre, descripcion, contacto, localizacion)
        else:
            raise Exception("Router no encontrado")

    def monitorear(self, router, interfaz, periodo):
        if router in self.routers:
            router_arreglo = self.routers[router]
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            
            return router_cercano.monitorear(interfaz, periodo)
        else:
            raise Exception("Router no encontrado")
        
    def obtenerProtocolos(self):
        with open("protocolos.json", "r") as file:
            protocolos = json.load(file)

        protocolos_filtrados = []
        for protocolo in protocolos:
            protocolo_filtrado = {
                'nombre': protocolo["nombre"],
                'estado': protocolo["estado"]
            }
            protocolos_filtrados.append(protocolo_filtrado)

        return protocolos

    def modificarProtocolo(self, nombreProtocolo, mode=True):
        # Si se desactiva, comprobamos que uno este activo
        protocolos = self.obtenerProtocolos()
        activos = 0
        for protocolo in protocolos:
            if protocolo["estado"] == "Activo":
                activos += 1

        if activos <= 1 and not mode:
            raise Exception("Debe haber al menos un protocolo activo")

        # Configuramos el protocolo en cada router
        for router in reversed(self.routers):
            router_arreglo = self.routers[router]
            router_cercano = Router(router_arreglo["ip"], router, router_arreglo["user"], router_arreglo["password"])
            router_cercano.modificarProtocolo(nombreProtocolo, mode)