from router import Router


class Red():

    def __init__(self, ip, name, user="cisco", password="cisco"):
        self.ip = ip
        self.name = name
        self.user = user
        self.password = password
        self.routers = {}

    def leerTopologia(self):
        router_conector = Router(self.ip, self.name, self.user, self.password)
        router_conector.buscarVecinos(self.routers)

        return routers
