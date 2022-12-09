from flask import Flask, request, jsonify, send_file
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
    

@app.post('/topologia')
def obtenerTopologia():
    """ Obetener la topologia de la red e inicializa los 
    datos del router al que primero se conecta """
    # Obteniendo credenciales desde la ip
    credenciales = request.get_json()
    ip = credenciales['ip']
    name = credenciales['name']
    user = credenciales['user']
    password = credenciales['password']
    
    # Asignando crecentiales a la red
    logging.debug("Asignando credenciales a la red")
    global red 
    red = Red(ip, name, user, password)
    
    # Leyendo la topologia
    response = jsonify(red.leerTopologia())
    return response


if __name__ == '__main__':
    app.run(debug=True)