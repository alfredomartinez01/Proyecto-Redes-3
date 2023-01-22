import threading
import time
import paramiko
import pexpect
import datetime
from flask import Flask, jsonify, json, request
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import io
import logging
import base64
import matplotlib.pyplot as plt

max_buffer = 65535

cmdGen = cmdgen.CommandGenerator()
	
host = None
community = None
view = None
container = {}
trampas = {}
fechas = []
fechas_bajas = []
fechas_subida = []
packets = []
iterations = 0
oct_anterior = 0
pack_anterior = 0
countTraps = 0

#Hostname OID
system_name = None
#Interface OID
fa2_0_in_oct = None
fa2_0_in_uPackets = None
fa2_0_out_oct = None
fa2_0_out_uPackets = None

snmpEngine = engine.SnmpEngine()

TrapAgentAddress='192.168.0.10'; #Direccion del escucha de traps
Port=162;  #Puerto

def snmp_query(host, community, oid):
	errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
		cmdgen.CommunityData(community),
		cmdgen.UdpTransportTarget((host, 161)),
		oid
	)

	# Revisamos errores e imprimimos resultados
	if errorIndication:
		print(errorIndication)
	else:
		if errorStatus:
			print('%s at %s' % (
				errorStatus.prettyPrint(),
				errorIndex and varBinds[int(errorIndex)-1] or '?'
				)
			)
		else:
			for name, val in varBinds:
				return(str(val))

def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
	global trampas
	global countTraps
	global fechas
	global fechas_subida
	global fechas_bajas
	global packets
	accion = {}

	tiempo_aux = str(datetime.datetime.now())
	accion['Tiempo'] = tiempo_aux

	for name, val in varBinds:
		logging.info("'%s' : %s," % (name.prettyPrint(), val.prettyPrint()))
		accion[name.prettyPrint()] = val.prettyPrint()

		if val.prettyPrint() == "administratively down":
			fechas.append(tiempo_aux)
			fechas_bajas.append(tiempo_aux)
			auxi = packets[len(packets) - 1]
			packets.append(auxi)
			print("Mensaje nuevo de traps recibido: "+ str(val.prettyPrint()))
		elif val.prettyPrint() == "Keepalive OK" or val.prettyPrint() == "up":
			fechas.append(tiempo_aux)
			fechas_subida.append(tiempo_aux)
			auxi = packets[len(packets) - 1]
			packets.append(auxi)
			print("Mensaje nuevo de traps recibido: "+ str(val.prettyPrint()))

	trampas['Trampa' + str(countTraps)] = accion
	countTraps+=1
	
## Implementacion de los programas con hilos ##
def monitorInt():
	global oct_anterior
	global pack_anterior
	global iterations
	global container
	global t1
	global fechas
	global fechas_subida
	global fechas_bajas
	global packets

	result = {}
	tiempo_aux = str(datetime.datetime.now())
	result['Tiempo'] = tiempo_aux
	fechas.append(tiempo_aux)
	result['hostname'] = snmp_query(host, community, system_name)
	result['Fa0-0_In_Octet'] = snmp_query(host, community, fa2_0_in_oct)
	result['Fa0-0_In_uPackets'] = snmp_query(host, community, fa2_0_in_uPackets)

	if iterations == 0:
		result['dif_oct'] = 0
		oct_anterior = int(snmp_query(host, community, fa2_0_in_oct))
		result['dif_pack'] = 0
		pack_anterior = int(snmp_query(host, community, fa2_0_in_uPackets))
	else:
		result['dif_oct'] = int(snmp_query(host, community, fa2_0_in_oct)) - oct_anterior
		oct_anterior = int(snmp_query(host, community, fa2_0_in_oct))
		result['dif_pack'] = int(snmp_query(host, community, fa2_0_in_uPackets)) - pack_anterior
		pack_anterior = int(snmp_query(host, community, fa2_0_in_uPackets))

	packets.append(result['dif_pack'])

	container['Iteration_'+str(iterations)] = result
	iterations+=1
	print("Iteracion "+ str(iterations))

	if iterations <= 10:
		time.sleep(10)
		monitorInt()

	return
	
def monitorTrampas():
	global iterations

	config.addTransport(
	    snmpEngine,
    	udp.domainName + (1,),
    	udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
	)

	#Configuracion de comunidad V1 y V2c
	config.addV1System(snmpEngine, view, community)

	ntfrcv.NotificationReceiver(snmpEngine, cbFun)

	snmpEngine.transportDispatcher.jobStarted(1)

	try:
		snmpEngine.transportDispatcher.runDispatcher()
	except:
		snmpEngine.transportDispatcher.closeDispatcher()
		raise

	return

def clear_buffer(conexion):
	if conexion.recv_ready():
		return conexion.recv(max_buffer)
		
def activate_routing(body):
	retorno = []
	
	conexion = paramiko.SSHClient()
	conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	conexion.connect(body['ip_address'],username= body['username'],password=body['password'],look_for_keys=False,allow_agent=False)
	
	nueva_conexion = conexion.invoke_shell()
	salida = clear_buffer(nueva_conexion)
	time.sleep(2)
	nueva_conexion.send("terminal length 0 \n")
	salida = clear_buffer(nueva_conexion)
	
	comandos = body['comands']
	
	for comand in comandos:
		print("Sending... "+comand+" ...")
		nueva_conexion.send(comand+"\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		retorno.append(str(salida))
	
	nueva_conexion.close()
	
	return jsonify(direction = body['ip_address'], comands = retorno)
	
app = Flask(__name__)

@app.route('/saludo')
def saludo():
	return 'Saludito'
	
@app.route('/monitoreo', methods= ['POST'])
def monitoreo():
	global system_name
	global fa2_0_in_oct
	global fa2_0_in_uPackets
	global fa2_0_out_oct
	global fa2_0_out_uPackets
	global host
	global community
	global view

	body = request.get_json()

	host = body['loopback']
	community = body['community']
	view = body['view']

	#Hostname OID
	system_name = '1.3.6.1.2.1.1.5.0'

	interfaceSelected = body['interface']

	#Interface OID
	if interfaceSelected == "fa20":
		fa2_0_in_oct = '1.3.6.1.2.1.2.2.1.10.1'
		fa2_0_in_uPackets = '1.3.6.1.2.1.2.2.1.11.1'
		fa2_0_out_oct = '1.3.6.1.2.1.2.2.1.16.1'
		fa2_0_out_uPackets = '1.3.6.1.2.1.2.2.1.17.1'

	retorno = {}
	time_ini = datetime.datetime.now()
	t1 = threading.Thread(target = monitorInt)
	t2 = threading.Thread(target = monitorTrampas)

	t1.start()
	t2.start()

	print("Se han lanzado varios hilos")

	t1.join()
	print("Ya termino el primero")
	#t2.join()

	time_fin = datetime.datetime.now()

	#print("Tiempo transcurrido: "+ str(time_fin.second - time_ini.second))
	print("\n\n")
	print(container)
	print("\n\n")
	print(trampas)

	print("\n\nTo print:")
	print(fechas)
	print(packets)

	retorno['packetes'] = container
	retorno['trampas'] = trampas

	fechas.pop(0)
	packets.pop(0)

	plt.plot(fechas,packets)

	for x in fechas_subida:
		plt.axvline(x = x, color = 'b', label = 'subida de interfaz')
	for x in fechas_bajas:
		plt.axvline(x = x, color = 'r', label = 'bajada de interfaz')

	# beautify the x-labels
	plt.gcf().autofmt_xdate()
	plt.ylabel('Packetes Recibidos')
	
	img = io.BytesIO()
	plt.savefig(img,format='png')
	img.seek(0)
	grafica = base64.b64encode(img.getvalue()).decode()
	plt.clf()
	
	return '<img src = "data:image/png;base64,{}">'.format(grafica)

@app.route('/snmp/desactivate')
def desactivate_snmp():
	ip_add = request.args.get('ip_add', type = str)
	username = 'cisco'
	password = 'cisco'
	
	conexion = paramiko.SSHClient()
	conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	conexion.connect(ip_add,username=username,password=password,look_for_keys=False,allow_agent=False)
	
	nueva_conexion = conexion.invoke_shell()
	salida = clear_buffer(nueva_conexion)
	time.sleep(2)
	nueva_conexion.send("terminal length 0 \n")
	salida = clear_buffer(nueva_conexion)
	
	retorno = None
	
	try:
		print("conf ter")
		nueva_conexion.send("conf term\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("no snmp-server")
		nueva_conexion.send("no snmp-server\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		retorno = "Se ha dado de baja el protocolo SNMP correctamente"
	except:
		retorno = "Ha habido un problema al dar de baja el protocolo SNMP"
		
	return retorno
	

@app.route('/snmp/activate', methods= ['POST'])
def activate_snmp():
	body = request.get_json()
	
	conexion = paramiko.SSHClient()
	conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	conexion.connect(body['ip_address'],username=body['username'],password=body['password'],look_for_keys=False,allow_agent=False)
	
	nueva_conexion = conexion.invoke_shell()
	salida = clear_buffer(nueva_conexion)
	time.sleep(2)
	nueva_conexion.send("terminal length 0 \n")
	salida = clear_buffer(nueva_conexion)
	
	retorno = None
	
	try:
		print("conf ter")
		nueva_conexion.send("conf term\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("snmp-server view "+body['view_name']+" iso included")
		nueva_conexion.send("snmp-server view "+body['view_name']+" iso included\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("snmp-server community "+body['community_name']+" RW "+body['view_name'])
		nueva_conexion.send("snmp-server community "+body['community_name']+" RW "+body['view_name']+"\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("snmp-server host 192.168.0.10 "+body['community_name'])
		nueva_conexion.send("snmp-server host 192.168.0.10 "+body['community_name']+"\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("snmp-server enable traps snmp linkdown")
		nueva_conexion.send("snmp-server enable traps snmp linkdown\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("snmp-server enable traps snmp linkup")
		nueva_conexion.send("snmp-server enable traps snmp linkup\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		retorno = "Se ha levantado SNMP con la baja y alta de interfaces de manera correcta"
	
	except:
		retorno = "Hubo un problema al levantar SNMP"
		
	return retorno
	

@app.route('/routing/rip/desactivate')
def desactivate_rip():
	ip_add = request.args.get('ip_add', type = str)
	username = 'cisco'
	password = 'cisco'
	
	conexion = paramiko.SSHClient()
	conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	conexion.connect(ip_add,username= username,password=password,look_for_keys=False,allow_agent=False)
	
	nueva_conexion = conexion.invoke_shell()
	salida = clear_buffer(nueva_conexion)
	time.sleep(2)
	nueva_conexion.send("terminal length 0 \n")
	salida = clear_buffer(nueva_conexion)
	
	retorno = None
	
	try:
		print("conf ter")
		nueva_conexion.send("conf term\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("no router rip")
		nueva_conexion.send("no router rip\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		nueva_conexion.close()
		retorno = "El protocolo rip ha sido dado de baja correctamente\n"
		
	except:
		retorno = "Error al dar de baja el protocolo eigrp"
	
	return retorno

@app.route('/routing/eigrp/desactivate')
def desactivate_eigrp():
	ip_add = request.args.get('ip_add', type = str)
	username = 'cisco'
	password = 'cisco'
	
	conexion = paramiko.SSHClient()
	conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	conexion.connect(ip_add,username= username,password=password,look_for_keys=False,allow_agent=False)
	
	nueva_conexion = conexion.invoke_shell()
	salida = clear_buffer(nueva_conexion)
	time.sleep(2)
	nueva_conexion.send("terminal length 0 \n")
	salida = clear_buffer(nueva_conexion)
	
	retorno = None
	
	try:
		print("conf ter")
		nueva_conexion.send("conf term\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("no router eigrp 1")
		nueva_conexion.send("no router eigrp 1\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		nueva_conexion.close()
		retorno = "El protocolo eigrp ha sido dado de baja correctamente\n"
		
	except:
		retorno = "Error al dar de baja el protocolo eigrp"
	
	return retorno
	
@app.route('/routing/ospf/desactivate')
def desactivate_ospf():
	ip_add = request.args.get('ip_add', type = str)
	username = 'cisco'
	password = 'cisco'
	
	conexion = paramiko.SSHClient()
	conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	conexion.connect(ip_add,username= username,password=password,look_for_keys=False,allow_agent=False)
	
	nueva_conexion = conexion.invoke_shell()
	salida = clear_buffer(nueva_conexion)
	time.sleep(2)
	nueva_conexion.send("terminal length 0 \n")
	salida = clear_buffer(nueva_conexion)
	
	retorno = None
	
	try:
		print("conf ter")
		nueva_conexion.send("conf term\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		
		print("no router ospf 1")
		nueva_conexion.send("no router ospf 1\n")
		time.sleep(2)
		salida = nueva_conexion.recv(max_buffer)
		print("\t "+ str(salida) )
		nueva_conexion.close()
		retorno = "El protocolo ospf ha sido dado de baja correctamente\n"
		
	except:
		retorno = "Error al dar de baja el protocolo ospf"
	
	return retorno

@app.route('/routing/eigrp', methods= ['POST'])
def eigrp_activate():
	body = request.get_json()	
	return activate_routing(body)

@app.route('/routing/ospf', methods= ['POST'])
def ospf_activate():
	body = request.get_json()	
	return activate_routing(body)

@app.route('/routing/rip', methods= ['POST'])
def rip_activate():
	body = request.get_json()
	return activate_routing(body)

@app.route('/activate_ssh')
def activate_ssh():
	""" Cuando no tiene activado SSH, se activa por telnet, activa SSH y regresa el usuairio con contraseña """
	ip_add = request.args.get('ip_add', type = str)
	username = 'cisco'
	password = 'cisco'
	
	print(ip_add)
	child = pexpect.spawn('telnet ' + ip_add)
	
	child.expect('Username:')
	child.sendline(username)
	child.expect('Password')
	child.sendline(password)
	print(child.before)
	
	#Iniciamos con la configuracion del ssh
	child.expect('R3#')
	child.sendline('configure terminal')
	print(child.before)
	
	#child.expect('R3(config)#')
	child.expect("#")
	
	child.sendline('ip ssh rsa keypair-name sshkey')
	print(child.before)
	print("Hasta este punto bieen")
	child.expect('#')
	child.sendline('crypto key generate rsa usage-keys label sshkey modulus 1024')
	print(child.before)
	child.expect('#')
	child.sendline('ip ssh v 2')
	print(child.before)
	child.expect('#')
	child.sendline('ip ssh time-out 30')
	print(child.before)
	child.expect('#')
	child.sendline('ip ssh authentication-retries 3')
	print(child.before)
	child.expect('#')
	child.sendline('line vty 0 15')
	print(child.before)
	child.expect('#')
	child.sendline('password cisco')
	print(child.before)
	child.expect('#')
	child.sendline('login local')
	print(child.before)
	child.expect('#')
	child.sendline('transport input ssh telnet')
	print(child.before)
	child.expect('#')
	child.sendline('exit')
	print(child.before)
	child.expect('#')
	child.sendline('exit')
	print(child.before)
	child.expect('#')
	child.sendline('sh runn | i ssh')
	
	retorno = child.before
	print(retorno)
	
	return 'SSH levantado correctamente'
	
@app.route('/ssh_activated')
def ssh_activated():
	retorno = None
	try:
		ip_add = request.args.get('ip_add', type = str)
		conexion = paramiko.SSHClient()
		conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		conexion.connect(ip_add,username='cisco',password='cisco',look_for_keys=False,allow_agent=False)
		nueva_conexion = conexion.invoke_shell()
	
		salida = nueva_conexion.recv(5000)
	
		nueva_conexion.send("show runn | i ssh\n")
		time.sleep(3)
	
		salida = nueva_conexion.recv(5000)
		print(salida)
		
		retorno = salida
		
	except:
		retorno = "No hay conexion ssh"
	
	return retorno

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

