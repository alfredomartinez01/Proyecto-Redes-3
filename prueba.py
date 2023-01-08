a = [{"user": "admin", "password": "admin", "privilegios": "15"}, {"user": "root", "password": "root", "privilegios": "0"}, {"user": "admin2", "password": "admin", "privilegios": "1"}]
b = [{"user": "admin", "password": "admin", "privilegios": "15"}, {"user": "root", "password": "root",  "privilegios": "0"}]
c = [{"user": "root", "password": "root",  "privilegios": "0"}, {"user": "admin2", "password": "admin", "privilegios": "1"}]


usuarios_cuenta = {}
for member in a:
    cadena_comparar = member["user"] + member["password"] + member["privilegios"]
    usuarios_cuenta[cadena_comparar] = usuarios_cuenta.get(cadena_comparar, 0) + 1

for member in b:
    cadena_comparar = member["user"] + member["password"] + member["privilegios"]
    usuarios_cuenta[cadena_comparar] = usuarios_cuenta.get(cadena_comparar, 0) + 1
    
for member in c:
    cadena_comparar = member["user"] + member["password"] + member["privilegios"]
    usuarios_cuenta[cadena_comparar] = usuarios_cuenta.get(cadena_comparar, 0) + 1

usuarios_globales = []
for usuario_cuenta in usuarios_cuenta:
    if usuarios_cuenta[usuario_cuenta] == 3:
        usuarios_globales.append(usuario_cuenta)


print(usuarios_globales)