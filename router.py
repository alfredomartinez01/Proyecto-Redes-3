import pexpect
import paramiko
import getpass
import logging
import time
from pysnmp.hlapi import *
max_buffer = 65535

class Router:
    def __init__(self, ip, name, user="root", password="root"):
        self.ip = ip
        self.name = name
        self.user = user
        self.password = password
    
    def buscarVecinos(self, routers = {}):
        if self.name in routers.keys(): # Si ya fue obtenido, no lo volvemos a obtener
            return
        
        mensaje = "Conectando a " + self.name
        logging.debug(mensaje)

        """ Nos conectamos al router """
        child = pexpect.spawn('telnet '+ self.ip)
        child.expect('Username: ')
        child.sendline(self.user)
        child.expect('Password: ')
        child.sendline(self.password)
        
        """Obtenemos la tabla de dispositivos conectados """
        child.expect(self.name+"#")
        child.sendline('show cdp ne | begin Device') # Obtenemos la tabla de dispositivos
        child.expect(self.name+"#")
        tabla_dispositivos = child.before.decode().split()
        
        conectados = [x for x in tabla_dispositivos if "Enrutador" in x] # Agrega a la lista si tiene la palabra Enrutador
        interfaces = []
        [interfaces.append(x) for x in tabla_dispositivos if ("/" in x) and (x not in interfaces)] # Agrega a la lista si tiene / y no repetidos

        """ Registramos el router """  
        routers[self.name] = {"ip": self.ip, "user": self.user, "password": self.password, "conectados": [x.split(".")[0] for x in conectados], "interfaces": interfaces} # Guardamos la info del dispositivo
        
        """ Obtenemos la informacion de cada dispositivo conectado """
        for dispositivo in conectados:
            # Obtenemos la info del dispositivo
            child.sendline('sh cdp entry '+ dispositivo)
            child.expect(self.name+"#")
            info_dispositivo = child.before.decode().split()
                
            # Obtenemos la ip del dispositivo
            ip = None
            for linea in range(0, len(info_dispositivo)):
                if 'address:' == info_dispositivo[linea]:
                    ip = info_dispositivo[linea+1]
            
            # Examinamos los routers vecinos
            enrutador = Router(str(ip), dispositivo.split(".")[0], self.user, self.password)
            enrutador.buscarVecinos(routers)


    def crearUsuario(self, user, privilegios, password):        
        """ Nos conectamos al router """
        child = pexpect.spawn('telnet '+ self.ip)
        child.expect('Username: ')
        child.sendline(self.user)
        child.expect('Password: ')
        child.sendline(self.password)
        
        """ Configurando el ssh """
        child.expect(self.name+"#")
        child.sendline('configure terminal')
        
        child.expect("#")
        child.sendline('ip domain-name adminredes.escom.ipn.mx')
        child.expect("#")
        child.sendline('ip ssh rsa keypair-name sshkey')
        child.expect("#")
        child.sendline('crypto key generate rsa usage-keys label sshkey modulus 1024')
        child.expect("#")
        child.sendline('ip ssh version 2')
        child.expect("#")
        child.sendline('ip ssh time-out 30')
        child.expect("#")
        child.sendline('ip ssh authentication-retries 3')
        child.expect("#")
        usuario = 'username ' + user + ' privilege '+ privilegios +' password '+password
        child.sendline(usuario)
        logging.debug(usuario)
        child.expect("#")
        child.sendline('line vty 0 4')
        child.expect("#")
        child.sendline('transport input ssh')   
        child.expect("#")
        child.sendline('login local')
        child.expect("#")
        child.sendline('exit')     
        child.expect("#")
        child.sendline('exit')      

    def eliminarUsuario(self, user):
        """ Nos conectamos al router """
        child = pexpect.spawn('telnet '+ self.ip)
        child.expect('Username:')
        child.sendline(self.user)
        child.expect('Password:')
        child.sendline(self.password)
        
        """ Eliminando el usuario ssh """
        child.expect(self.name+"#")
        child.sendline('configure terminal')
        child.expect("#")
        child.sendline('no username '+ user)
        child.expect("#")
        child.sendline('exit')

    def actualizarUsuario(self, user, new_user, privilegios, password):
        """ Nos conectamos al router """
        child = pexpect.spawn('telnet '+ self.ip)
        child.expect('Username:')
        child.sendline(self.user)
        child.expect('Password:')
        child.sendline(self.password)

        """ Eliminando el usuario ssh """
        child.expect(self.name+"#")
        child.sendline('configure terminal')
        child.expect("#")
        child.sendline('no username '+ user)
        child.expect("#")

        """Insertando de nuevo el usuario"""
        child.sendline('ip domain-name adminredes.escom.ipn.mx')
        child.expect("#")
        child.sendline('ip ssh rsa keypair-name sshkey')
        child.expect("#")
        child.sendline('crypto key generate rsa usage-keys label sshkey modulus 1024')
        child.expect("#")
        child.sendline('ip ssh version 2')
        child.expect("#")
        child.sendline('ip ssh time-out 30')
        child.expect("#")
        child.sendline('ip ssh authentication-retries 3')
        child.expect("#")
        usuario = 'username ' + new_user + ' privilege '+ privilegios +' password '+password
        logging.debug(usuario)
        child.sendline(usuario)
        child.expect("#")
        child.sendline('line vty 0 4')
        child.expect("#")
        child.sendline('transport input ssh')   
        child.expect("#")
        child.sendline('login local')
        child.expect("#")
        child.sendline('exit')     
        child.expect("#")
        child.sendline('exit')

    def consultarUsuarios(self):
        """ Nos conectamos al router """
        child = pexpect.spawn('telnet '+ self.ip)
        child.expect('Username:')
        child.sendline(self.user)
        child.expect('Password:')
        child.sendline(self.password)
        
        """ Consultando usuarios ssh """
        child.expect(self.name+"#")
        logging.debug("Consultando usuarios")
        child.sendline('sh run | i user')
        child.expect(self.name+"#")
        info_usuarios = child.before.decode().split("\n")
        # logging.debug(info_usuarios)

        usuarios = []
        for n_cadena in range(0, len(info_usuarios)):
            data = info_usuarios[n_cadena].split(" ")

            if data[0] == "username" and data[2] == "privilege":
                usuario={
                    'user': data[1],
                    'password': data[6],
                    'privilegios': data[3]
                }
                usuarios.append(usuario)
            elif data[0] == "username":
                usuario={
                    'user': data[1],
                    'password': data[4],
                    'privilegios': "1"
                }
                usuarios.append(usuario)
        
        return usuarios

    def clear_buffer(self, conexion):
        if conexion.recv_ready():
            return conexion.recv(max_buffer)

    def configurarSNMPV3(self):
        mensaje = "Conectando a " + self.name
        logging.debug(mensaje)

        """ Nos conectamos al router """
        conexion = paramiko.SSHClient()
        conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conexion.connect(self.ip, username=self.user, password=self.password, look_for_keys=False, allow_agent=False)
        nueva_conexion = conexion.invoke_shell()
        self.clear_buffer(nueva_conexion)
        time.sleep(2)
        nueva_conexion.send("terminal length 0 \n")
        self.clear_buffer(nueva_conexion)
        
        """ Configuramos el snmp"""
        nueva_conexion.send("conf term\n")
        time.sleep(2)
        self.clear_buffer(nueva_conexion)
        nueva_conexion.send("snmp-server group infoMIB v3 auth read MIBRead write MIBWrite\n")
        time.sleep(2)
        self.clear_buffer(nueva_conexion)
        nueva_conexion.send("snmp-server user root infoMIB v3 auth sha root1234\n")
        time.sleep(2)
        self.clear_buffer(nueva_conexion)
        nueva_conexion.send("snmp-server view MIBRead iso included\n")
        time.sleep(2)
        self.clear_buffer(nueva_conexion)
        nueva_conexion.send("snmp-server view MIBWrite iso included\n")
        time.sleep(2)
        self.clear_buffer(nueva_conexion)

        nueva_conexion.close()


    def snmpV3_query(self, host, oid, mode="lectura", valor=""):
        auth = UsmUserData(
            userName = "root",
            authKey="root1234",
            authProtocol=usmHMACSHAAuthProtocol
        )
        if mode == "lectura":
            iterator = getCmd(
                SnmpEngine(),
                auth,
                UdpTransportTarget((host, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
        else:
            iterator = setCmd(
                SnmpEngine(),
                auth,
                UdpTransportTarget((host, 161)),
                ContextData(),
                ObjectType(
                    ObjectIdentity(oid),
                    OctetString(valor)
                )
            )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            logging.error(errorIndication)
        
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        
        else:
            for name, val in varBinds:
                return(str(val))

    def consultarMIB(self):
        info_mib = {}
        info_mib["nombre"] = self.snmpV3_query(self.ip, '1.3.6.1.2.1.1.5.0')
        info_mib["descripcion"] = self.snmpV3_query(self.ip, '1.3.6.1.2.1.1.1.0')
        info_mib["contacto"] = self.snmpV3_query(self.ip, '1.3.6.1.2.1.1.4.0')
        info_mib["localizacion"] = self.snmpV3_query(self.ip, '1.3.6.1.2.1.1.6.0')
        
        return info_mib
    
    def modificarMIB(self, nombre, descripcion, contacto, localizacion):        
        # self.snmpV3_query("10.0.1.254", '1.3.6.1.2.1.1.5.0', mode="escritura", valor=nombre)
        # self.snmpV3_query("10.0.1.254", '1.3.6.1.2.1.1.1.0', mode="escritura", valor=descripcion)
        self.snmpV3_query(self.ip, '1.3.6.1.2.1.1.4.0', mode="escritura", valor=contacto)
        self.snmpV3_query(self.ip, '1.3.6.1.2.1.1.6.0', mode="escritura", valor=localizacion)

    def monitorear(self,intefaz, periodo):
        pass