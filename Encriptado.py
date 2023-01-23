from cryptography.fernet import Fernet

def generar():
    clave = Fernet.generate_key()
    with open("clave.key","wb") as archivo_clave:
        archivo_clave.write(clave) 

    f = Fernet(clave)
    encriptado = f.encrypt("bcjlirxbznuesexd".encode())

    with open("pass.key","wb") as archivo_pass:
        archivo_pass.write(encriptado) 

def desencriptar():
    clave = cargar_clave()
    f= Fernet(clave)
    passw = cargar_pass()
    return f.decrypt(passw) 

def cargar_clave():
    return open("clave.key","rb").read()

def cargar_pass():
    return open("pass.key","rb").read()


