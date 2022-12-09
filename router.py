import pexpect
import getpass
# import networkx as nx
# import matplotlib.pyplot as plt

class Router:
    def __init__(self, ip, name, user="root", password="root"):
        self.ip = ip
        self.name = name
        self.user = user
        self.password = password
    
    def buscarVecinos(self, routers):
        if self.name in routers.keys(): # Si ya fue obtenido, no lo volvemos a obtener
            return
        
        """ Nos conectamos al router """
        child = pexpect.spawn('telnet '+ self.ip)
        child.expect('Username: ')
        child.sendline(self.user)
        child.expect('Password: ')
        child.sendline(self.user)
        
        """Obtenemos la tabla de dispositivos conectados """
        child.expect(self.name+"#")
        child.sendline('show cdp ne | begin Device') # Obtenemos la tabla de dispositivos
        child.expect(self.name+"#")
        tabla_dispositivos = child.before.decode()
        n_conectados = len(tabla_dispositivos) # Obtenemos el numero de dispositivos conectados

        """ Obtenemos la informacion de cada dispositivo conectado """
        for i_dispositivo in range(0, n_conectados):
            nombre = tabla_dispositivos[i_dispositivo]
            
            # Obtenemos la info del dispositivo
            child.sendline('sh cdp entry '+ nombre)
            child.expect(self.name+"#")
            info_dispositivo = child.before.decode().split()
            
            # Obtenemos la ip del dispositivo
            for linea in range(0, len(info_dispositivo)):
                if 'address:' == info_dispositivo[linea]:
                    ip = info_dispositivo[linea+1]
                    
                    routers[nombre] = {"ip": ip, "user": self.user, "password": self.password} # Guardamos la info del dispositivo
                    
        """ Cerramos la conexión """
        child.sendline('exit')
        
        """ Buscamos entre cada dispositivo """
        for i_dispositivo in range(0, n_conectados):
            nombre = tabla_dispositivos[i_dispositivo]
            
            enrutador = Router(routers[nombre]["ip"], nombre, routers[nombre]["user"], routers[nombre]["password"])
            enrutador.buscarVecinos(routers)
