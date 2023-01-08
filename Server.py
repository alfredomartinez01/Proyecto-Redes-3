import time
import paramiko
import pexpect
import datetime
from flask import Flask, jsonify, json, request

max_buffer = 65535

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
		
		print("snmp-server community "+body['community_name']+" WR"+body['view_name'])
		nueva_conexion.send("snmp-server community "+body['community_name']+" WR"+body['view_name']+"\n")
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

