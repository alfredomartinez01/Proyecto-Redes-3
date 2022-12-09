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

    def leerTopologia(self):
        # Obteniendo información de los routers
        routers = {}
        router_cercano = Router(self.ip, self.name, self.user, self.password)
        router_cercano.buscarVecinos(routers)

        # Generano gráfico
        plt.clf() # Limpiando imagen
        G = nx.Graph()
        for router in routers: # Agregando routers
            G.add_node(router, name=router)
        for r1 in routers: # Generando conexiones
            for r2 in routers[r1]["conectados"]:
                G.add_edge(r1, r2)

        nx.draw_networkx(G, with_labels=True, node_color="g") # Creando gráfico
        plt.savefig("static/topologia.jpg")