from flask import Flask, jsonify, json, request
from pysnmp.entity.rfc3413.oneliner import cmdgen
import datetime

from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import threading
import paramiko
import pexpect
import io
import logging
import base64
import matplotlib.pyplot as matplot

max_buffer = 65535

#Variables
paquetes = []
trampas = []
fechas = []
fecha_subida = []
fecha_bajada = []
iteraciones=0
octeto_anterior = 0
paquete_anterior = 0
contenedor = {}

#OID
in_paquetes = '1.3.6.1.2.1.2.2.1.11.1'
in_octetos = '1.3.6.1.2.1.2.2.1.10.1'
out_paquetes = '1.3.6.1.2.1.2.2.1.17.1'
out_octetos =  '1.3.6.1.2.1.2.2.1.16.1'
sistema = '1.3.6.1.2.1.1.5.0'

#escucha traps
traps_escucha = '10.0.1.1'

def snmp_query(host, community, oid):
    errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
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
            
def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
    global paquetes
    global fechas
    global fecha_subida
    global fecha_bajada

    valor = str((varBinds.pop())[-1])
    with open('status.txt', 'w') as f:
        f.write(valor+"\n")
        f.close()
    print(valor)
    if valor == "administratively down":
        fechas.append(str(datetime.datetime.now()))
        fecha_bajada.append(str(datetime.datetime.now()))
        paquetes.append(paquetes[len(paquetes)-1])
    elif valor=="Keepalive OK" or valor=="up":
        fechas.append(str(datetime.datetime.now()))
        fecha_subida.append(str(datetime.datetime.now()))
        paquetes.append(paquetes[len(paquetes)-1])

def monitor_paq():
    global paquetes
    global fechas
    global iteraciones
    global octeto_anterior
    global paquete_anterior
    global contenedor

    resultado = {}
    resultado["Tiempo"] = str(datetime.datetime.now())
    fechas.append(str(datetime.datetime.now()))
    resultado["hostname"]=snmp_query('10.0.1.254', comunidad, sistema)
    resultado['Interfaz-octetos-entrada']=snmp_query('10.0.1.254', comunidad, in_octetos)
    resultado['Interfaz-paquetes-entrada']=snmp_query('10.0.1.254', comunidad, in_paquetes)

    if iteraciones == 0:
        resultado['dif_oct'] = 0
        octeto_anterior = int(snmp_query('10.0.1.254', comunidad, in_octetos))
        resultado['dif_pack'] = 0
        paquete_anterior= int(snmp_query('10.0.1.254', comunidad, in_paquetes))
    else:
        resultado['dif_oct'] = int(snmp_query('10.0.1.254', comunidad, in_octetos))-oct_anterior
        octeto_anterior = int(snmp_query('10.0.1.254', comunidad, in_octetos))
        resultado['dif_pack'] = int(snmp_query('10.0.1.254', comunidad, in_paquetes))-paquete_anterior
        paquete_anterior= int(snmp_query('10.0.1.254', comunidad, in_paquetes))
    
    paquetes.append(resultado['dif_pack'])
    contenedor["Iteracion_"+str(iteraciones)] = resultado
    iteraciones += 1
    print("Iteracion:"+ str(iteraciones))

    if iteraciones <= 10:
        time.sleep(10)
        monitor_paq()
    return

def monitor_trampa(host, comunidad, vista):
    snmpEngine = engine.SnmpEngine()

    config.addTransport(
        snmpEngine, udp.domainName + (1,),
        udp.UdpTransport().openServerMode((traps_escucha, 162))
    )

    config.addV1System(snmpEngine, vista, comunidad)

    ntfrcv.NotificationReceiver(snmpEngine, cbFun)
    snmpEngine.transportDispatcher.jobStarted(1)  

    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise
    
    return

app = Flask(__name__)

@app.get('/monitoreo-red')
def monitoreo_snmp():
    global paquetes
    global trampas
    global fechas
    global fecha_subida
    global fecha_bajada
    global contenedor
    
    retorno={}
    tiempo_inicial = datetime.datetime.now()

    t1=threading.Thread(target = monitor_paq)
    t2=threading.Thread(target = monitor_trampa, args=('10.0.1.1','comunidad','vis_comunidad_read'))

    t1.start()
    t2.start()

    print("Lazamiento de hilos listo\n")

    t1.join()

    tiempo_final = datetime.datetime.now()

    retorno["Paquetes:"] = contenedor
    retorno["Trampas:"] = trampas

    fechas.pop(0)
    paquetes.pop(0)

    matplot.plot(fechas,paquetes)

    for x in fecha_subida:
        matplot.axvline(x = x, color = 'green', label = 'Se levanta interfaz')
    for x in fecha_bajada:
        matplot.axvline(x = x, color = 'red', label = 'Se baja interfaz')
    
    matplot.gcf().autofmt_xdate()
    matplot.ylabel('Paquetes recibidos')

    imagen = io.BytesIO()
    matplot.savefig(imagen, format='png')
    imagen.seek(0)
    grafica = base64.b64encode(imagen.getvalue()).decode()
    matplot.clf()
    matplot.savefig("static/grafica.jpg")

    return 200 
