import smtplib,Encriptado
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

#Encriptación y obtencion de contraseña del correo
Encriptado.generar()
password = (str)(Encriptado.desencriptar()).split("'")

remitente = 'r1enable.notification@gmail.com'
destinatario = 'reina.zirtaeb@gmail.com'


#Función para agregar imagenes al html
def cargarArchivoEmail(email, filename, extra_headers=None):
    with open(filename, "rb") as f:
        file_attachment = MIMEApplication(f.read())   
    file_attachment.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    if extra_headers is not None:
        for name, value in extra_headers.items():
            file_attachment.add_header(name, value)
    email.attach(file_attachment)

#Funcion para establecer cuerpo de correo de notificación de paquetes perdidos
def enviarCorreoPerdidos(nombreRouter, nombreEnlace):
    #Lectura de estilos
    estilos = open('css/estilos.css','r').read()

    #Cuerpo del correo
    msg = "un rebase en el porcentaje de paquetes perdidos "

    cuerpo = open('html/perdidos_dañados.html','r').read().format(estilos=estilos, msg=msg, nombreR=nombreRouter, nombreI=nombreEnlace)
    #print(cuerpo)
    enviarCorreo(cuerpo, 'perdidos.png')

#Funcion para establecer cuerpo de correo de notificación de paquetes dañados
def enviarCorreoDañados(nombreRouter, nombreEnlace):
    #Lectura de estilos
    estilos = open('css/estilos.css','r').read()

    #Cuerpo del correo
    msg = "un rebase en el porcentaje de paquetes dañados "

    cuerpo = open('html/perdidos_dañados.html','r').read().format(estilos=estilos, msg=msg, nombreR=nombreRouter, nombreI=nombreEnlace)
    #print(cuerpo)
    enviarCorreo(cuerpo, 'dañados.png')

#Objeto de prueba para probar la funcion enviarCorreoModificacionMIB
obj = {
    'nombre': 'R3',
    'descripcion': 'Probando',
    'ubicacion': 'Estado de mexico',
    'contacto': 'Admin'
}

#Funcion para enviar la notificación por correo cuando haya una modificación en la MIB
def enviarCorreoModificacionMIB(nombreRouter, objNuevaInfoMib):
    #Lectura de estilos
    estilos = open('css/estilos.css','r').read()

    #Cuerpo del correo
    cuerpo = open('html/modificacionMIB.html','r').read().format(estilos=estilos, nombreR=nombreRouter, nombreMIB=objNuevaInfoMib['nombre'], desMIB=objNuevaInfoMib['descripcion'], ubiMIB=objNuevaInfoMib['ubicacion'], contMIB=objNuevaInfoMib['contacto'])
    #print(cuerpo)
    enviarCorreo(cuerpo, 'mib.png')

#Funcion para enviar la notificación por correo cuando se detecte una caida o un arranque de interfaz
def enviarCorreoEstadoInterfaz(nombreRouter, nombreEnlace, valor):
    #Lectura de estilos
    estilos = open('css/estilos.css','r').read()

    #Cuerpo del correo
    if valor == 0:
        msg = "una caida "
        img = 'caida.png'
    elif valor == 1:
        msg = "un arranque "
        img = 'arranque.png'

    cuerpo = open('html/estadoInt.html','r').read().format(estilos=estilos, msg=msg, nombreR=nombreRouter, nombreI=nombreEnlace)
    #print(cuerpo)
    enviarCorreo(cuerpo, img)

#Funcion para enviar la notificación por correo cuando se edite el dispositivo por consola
def enviarCorreoConsola(nombreRouter):
    #Lectura de estilos
    estilos = open('css/estilos.css','r').read()

    #Cuerpo del correo
    cuerpo = open('html/consola.html','r').read().format(estilos=estilos, nombreR=nombreRouter)
    #print(cuerpo)
    enviarCorreo(cuerpo, 'consola.png')

def enviarCorreo(cuerpoC, nombreI):
    #Creacion del email declarando que contendra contenido MIME
    email = MIMEMultipart()
    #Agremamos las imagenes del html
    cargarArchivoEmail(email, 'imagenes/logoIPN.png', {'Content-ID': '<logoIPN>'})
    cargarArchivoEmail(email, 'imagenes/logoEscom.png', {'Content-ID': '<logoEscom>'})
    cargarArchivoEmail(email, 'imagenes/' + nombreI, {'Content-ID': '<imagen>'})

    #Asignación de remitente, destinatario, asunto y cuerpo al correo que se mandara
    email['From'] = remitente
    email['To'] = destinatario
    email['Subject'] ='Alerta del admistrador'
    #cuerpo = enviarCorreoPerdidos('R1', 'f 0/0')

    email.attach(MIMEText(cuerpoC, "html")) 

    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp.login(remitente, password[1])
    smtp.sendmail(remitente, destinatario, email.as_string())
    smtp.quit()

if __name__ == '__main__':
    #enviarCorreoPerdidos('R1', 'f 0/0')
    #enviarCorreoDañados('R1', 'f 0/0')
    #enviarCorreoModificacionMIB('R3', obj)
    enviarCorreoEstadoInterfaz('R2', 'F 1/2', 0) #Caida
    #enviarCorreoEstadoInterfaz('R2', 'F 1/2', 1) #Arranque
    #enviarCorreoConsola('R4')


