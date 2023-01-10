from flask import Flask, request, jsonify, send_file, redirect
from red import Red
import logging

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', handlers=[logging.FileHandler('app.log')])
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

app = Flask(__name__)
red = None

@app.get('/')
def index():    
    """ Obtiene la pagina principal """
    return send_file('static/index.html')
    
@app.get('/usuarios')
def usuarios():    
    """ Obtiene la pagina de gestión de usuarios """
    return send_file('static/usuarios.html')

@app.get('/monitorear')
def monitorear():
    """ Obtiene la pagina de monitoreo """
    return send_file('static/monitorear.html')

@app.get('/protocolos')
def protocolos():
    """ Obtiene la pagina de protocolos """
    return send_file('static/protocolos.html')

@app.get('/mib')
def mib():
    """ Obtiene la pagina de modificar los datos de la mib """
    return send_file('static/modificar-mib.html')
    
@app.get('/mib/<router>')
def consultarMIB(router):
    """ Consultando informacion de la MIB de router """
    
    # Levantando protocolo SNMP en el router
    # red.configurarSNMP(router)
    
    return jsonify({"status": "ok"})
    
@app.post('/topologia')
def obtenerTopologia():
    """ Obetener la topologia de la red e inicializa los 
    datos del router al que primero se conecta """
    # Obteniendo credenciales desde la petición
    credenciales = request.get_json()
    ip = credenciales['ip']
    name = credenciales['name']
    user = credenciales['user']
    password = credenciales['password']
    
    # Asignando crecentiales a la red
    global red 
    red = Red(ip, name, user, password)
    
    # Leyendo la topologia
    red.leerTopologia() # almacena en el archivo topologia.jpg
    
    return send_file('static/topologia.jpg')

@app.get('/info-topologia')
def obtenerInfoTopologia():
    """ Obetener la topologia de la red e inicializa los 
    datos del router al que primero se conecta """
    
    # Obteniendo la infomración de la topologia
    global red
    if red == None:
        return redirect("/")

    infoTopologia = red.obtenerRouters()
    
    return jsonify(infoTopologia)

@app.post('/monitorear-interfaz')
def monitorearInterfaz():
    """ Realizando monitoreo en interfaz de router """
    # Obteniendo parametros desde la peticion
    credenciales = request.get_json()
    router = credenciales['router']
    interfaz = credenciales['interfaz']
    periodo = credenciales['periodo']
    
    # Levantando protocolo SNMP
    red.configurarSNMP(router)
    
    try:
        # Realizando monitoreo
        red.monitorear(router, intefaz, periodo)
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "Error monitoreando"}), 500        

@app.post('/usuarios/<router>')
def crearUsuario(router):
    """ Creando un nuevo usuario SSH """
    # Obteniendo parametros desde la peticion
    credenciales = request.get_json()
    user = credenciales['user']
    password = credenciales['password']
    privilegios = credenciales['privilegios']

    try:
        red.crearUsuario(router, user, privilegios, password)
        return jsonify({"status": "ok"})        
    except:
        return jsonify({"status": "Error creando usuario"}), 500 
    
@app.get('/usuarios/<router>')
def consultarUsuarios(router):
    """ Obteniendo los usuarios SSH de router """
    try:
        usuarios = red.consultarUsuarios(router)
        return jsonify(usuarios)
    except Exception as e:
        logging.error(str(e))
        return jsonify({"status": "Error obteniendo usuarios " + str(e)}), 500

@app.route('/usuarios/<router>', methods=['DELETE'])
def eliminarUsuario(router):
    """ Eliminando un usuario SSH """
    # Obteniendo parametros desde la peticion
    credenciales = request.get_json()
    user = credenciales['user']
    logging.debug(user)

    try:
        red.eliminarUsuario(router, user)
        return jsonify({"status": "ok"})        
    except Exception as e:
        logging.error(str(e))
        return jsonify({"status": "Error eliminando usuario" + str(e)}), 500

@app.route('/usuarios/<router>', methods=['PUT'])
def actualizarUsuario(router):
    """ Actualizando un usuario SSH """
    # Obteniendo parametros desde la peticion
    credenciales = request.get_json()
    user = credenciales['user']
    new_user = credenciales['new_user']
    password = credenciales['password']
    privilegios = credenciales['privilegios']
    
    logging.debug(user+password+privilegios)

    try:
        red.actualizarUsuario(router, user, new_user, privilegios, password)
        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(str(e))
        return jsonify({"status": "Error actualizando usuario" + str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)