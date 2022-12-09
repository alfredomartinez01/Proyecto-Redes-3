from router import Router
import logging

class Red():

    def __init__(self, ip, name, user="root", password="root"):
        self.ip = ip
        self.name = name
        self.user = user
        self.password = password

    def leerTopologia(self):
        routers = {}
        router_conector = Router(self.ip, self.name, self.user, self.password)
        router_conector.buscarVecinos(routers)

        
        return routers
