from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

gestor_estudiantes = GestorJSON("data/estudiantes.json")
gestor_materias = GestorJSON("data/materias.json")
gestor_matriculas = GestorJSON("data/matriculas.json")

CAMPOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet", "carrera")
CAMPOS_MATERIA = ("nombre", "codigo", "creditos", "cupos")
BUSCABLES_ESTUDIANTE = ("nombre", "apellido", "email", "carnet", "carrera")
BUSCABLES_MATERIA = ("nombre", "codigo")


def leer_objetos(gestor, clase):
    return [clase.desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(gestor, clase, id_registro):
    for registro in gestor.leer():
        if registro["id"] == id_registro:
            return clase.desde_diccionario(registro)
    return None


def buscar(gestor, clase, termino, campos):
    termino = str(termino).strip().lower()
    if termino == "":
        return []
    encontrados = []
    for registro in gestor.leer():
        for campo in campos:
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(clase.desde_diccionario(registro))
                break
    return encontrados


def siguiente_id(gestor):
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1


def guardar_nuevo(gestor, objeto):
    registros = gestor.leer()
    registros.append(objeto.a_diccionario())
    return gestor.guardar(registros)


def reemplazar(gestor, objeto):
    registros = gestor.leer()
    for indice, registro in enumerate(registros):
        if registro["id"] == objeto.id:
            registros[indice] = objeto.a_diccionario()
            return gestor.guardar(registros)
    return False


def eliminar(gestor, id_registro):
    registros = gestor.leer()
    quedan = [registro for registro in registros if registro["id"] != id_registro]
    if len(quedan) == len(registros):
        return False
    return gestor.guardar(quedan)


def ids_registrados(gestor):
    return {registro["id"] for registro in gestor.leer()}


def indice_por_id(gestor, clase):
    return {registro["id"]: clase.desde_diccionario(registro) for registro in gestor.leer()}


def convertir_entero(valor):
    try:
        return int(str(valor).strip())
    except ValueError:
        return None


def carnets_registrados(excepto_id=None):
    return {
        registro["carnet"].upper()
        for registro in gestor_estudiantes.leer()
        if registro["id"] != excepto_id
    }


def emails_registrados(excepto_id=None):
    return {
        registro["email"].lower()
        for registro in gestor_estudiantes.leer()
        if registro["id"] != excepto_id
    }


def validar_estudiante(datos, id_actual=None):
    if id_actual is None:
        for campo in ("nombre", "apellido", "email", "carnet"):
            if str(datos.get(campo, "")).strip() == "":
                return f"El campo {campo} es obligatorio"
    for campo in ("nombre", "apellido", "carnet"):
        if campo in datos and str(datos[campo]).strip() == "":
            return f"El campo {campo} no puede quedar vacío"
    if "email" in datos:
        email = str(datos["email"]).strip().lower()
        if not es_email_valido(email):
            return f"Email inválido: '{email}'"
        if email in emails_registrados(id_actual):
            return "Ese email ya está registrado"
    if "carnet" in datos:
        carnet = str(datos["carnet"]).strip().upper()
        if carnet in carnets_registrados(id_actual):
            return "Ese carnet ya está registrado"
    return None


def crear_estudiante(datos):
    error = validar_estudiante(datos)
    if error:
        return False, error
    estudiante = Estudiante(
        siguiente_id(gestor_estudiantes),
        str(datos["nombre"]).strip().title(),
        str(datos["apellido"]).strip().title(),
        str(datos["email"]).strip().lower(),
        str(datos["carnet"]).strip().upper(),
        str(datos.get("carrera", "")).strip().title(),
    )
    if not guardar_nuevo(gestor_estudiantes, estudiante):
        return False, "No se pudo escribir el archivo"
    return True, f"Estudiante creado: {estudiante.etiqueta()}"


def obtener_estudiantes():
    return leer_objetos(gestor_estudiantes, Estudiante)


def obtener_estudiante(id_estudiante):
    return obtener_por_id(gestor_estudiantes, Estudiante, id_estudiante)


def buscar_estudiantes(termino):
    return buscar(gestor_estudiantes, Estudiante, termino, BUSCABLES_ESTUDIANTE)


def actualizar_estudiante(id_estudiante, cambios):
    estudiante = obtener_estudiante(id_estudiante)
    if estudiante is None:
        return False, f"No existe un estudiante con id {id_estudiante}"
    if not cambios:
        return False, "No se indicó ningún cambio"
    desconocidos = set(cambios) - set(CAMPOS_ESTUDIANTE)
    if desconocidos:
        return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
    error = validar_estudiante(cambios, id_estudiante)
    if error:
        return False, error
    for campo, valor in cambios.items():
        valor = str(valor).strip()
        if campo in ("nombre", "apellido", "carrera"):
            valor = valor.title()
        elif campo == "email":
            valor = valor.lower()
        elif campo == "carnet":
            valor = valor.upper()
        setattr(estudiante, campo, valor)
    if not reemplazar(gestor_estudiantes, estudiante):
        return False, "No se pudo escribir el archivo"
    return True, f"Estudiante {id_estudiante} actualizado"


def eliminar_estudiante(id_estudiante):
    if obtener_estudiante(id_estudiante) is None:
        return False, f"No existe un estudiante con id {id_estudiante}"
    if id_estudiante in matriculas_por_estudiante():
        return False, "El estudiante tiene matrículas registradas: retírelas antes de eliminarlo"
    if not eliminar(gestor_estudiantes, id_estudiante):
        return False, "No se pudo escribir el archivo"
    return True, f"Estudiante {id_estudiante} eliminado"


def codigos_registrados(excepto_id=None):
    return {
        registro["codigo"].upper()
        for registro in gestor_materias.leer()
        if registro["id"] != excepto_id
    }


def validar_materia(datos, id_actual=None):
    if id_actual is None:
        for campo in ("nombre", "codigo", "creditos", "cupos"):
            if str(datos.get(campo, "")).strip() == "":
                return f"El campo {campo} es obligatorio"
    for campo in ("nombre", "codigo"):
        if campo in datos and str(datos[campo]).strip() == "":
            return f"El campo {campo} no puede quedar vacío"
    if "codigo" in datos:
        codigo = str(datos["codigo"]).strip().upper()
        if codigo in codigos_registrados(id_actual):
            return "Ese código ya está registrado"
    if "creditos" in datos:
        creditos = convertir_entero(datos["creditos"])
        if creditos is None or not 1 <= creditos <= 10:
            return "Los créditos deben ser un número entero entre 1 y 10"
    if "cupos" in datos:
        cupos = convertir_entero(datos["cupos"])
        if cupos is None or not 0 <= cupos <= Materia.CUPOS_MAXIMOS:
            return f"Los cupos deben ser un número entero entre 0 y {Materia.CUPOS_MAXIMOS}"
    return None


def limpiar_nombre(valor):
    texto = " ".join(str(valor).split())
    return texto[:1].upper() + texto[1:]


def crear_materia(datos):
    error = validar_materia(datos)
    if error:
        return False, error
    materia = Materia(
        siguiente_id(gestor_materias),
        limpiar_nombre(datos["nombre"]),
        str(datos["codigo"]).strip().upper(),
        int(str(datos["creditos"]).strip()),
        int(str(datos["cupos"]).strip()),
    )
    if not guardar_nuevo(gestor_materias, materia):
        return False, "No se pudo escribir el archivo"
    return True, f"Materia creada: {materia.etiqueta()}"


def obtener_materias():
    return leer_objetos(gestor_materias, Materia)


def obtener_materia(id_materia):
    return obtener_por_id(gestor_materias, Materia, id_materia)


def buscar_materias(termino):
    return buscar(gestor_materias, Materia, termino, BUSCABLES_MATERIA)


def actualizar_materia(id_materia, cambios):
    materia = obtener_materia(id_materia)
    if materia is None:
        return False, f"No existe una materia con id {id_materia}"
    if not cambios:
        return False, "No se indicó ningún cambio"
    desconocidos = set(cambios) - set(CAMPOS_MATERIA)
    if desconocidos:
        return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
    error = validar_materia(cambios, id_materia)
    if error:
        return False, error
    for campo, valor in cambios.items():
        if campo == "nombre":
            materia.nombre = limpiar_nombre(valor)
        elif campo == "codigo":
            materia.codigo = str(valor).strip().upper()
        elif campo == "creditos":
            materia.creditos = int(str(valor).strip())
        elif campo == "cupos":
            materia.cupos = int(str(valor).strip())
    if not reemplazar(gestor_materias, materia):
        return False, "No se pudo escribir el archivo"
    return True, f"Materia {id_materia} actualizada"


def eliminar_materia(id_materia):
    if obtener_materia(id_materia) is None:
        return False, f"No existe una materia con id {id_materia}"
    materias_con_matriculas = {registro["materia_id"] for registro in gestor_matriculas.leer()}
    if id_materia in materias_con_matriculas:
        return False, "La materia tiene matrículas registradas: retírelas antes de eliminarla"
    if not eliminar(gestor_materias, id_materia):
        return False, "No se pudo escribir el archivo"
    return True, f"Materia {id_materia} eliminada"


def materias_sin_cupo():
    return [materia for materia in obtener_materias() if not materia.hay_cupo()]


def es_periodo_valido(periodo):
    partes = periodo.split("-")
    return len(partes) == 2 and len(partes[0]) == 4 and partes[0].isdigit() and partes[1].isdigit()


def validar_matricula(datos):
    estudiante_id = convertir_entero(datos.get("estudiante_id", ""))
    materia_id = convertir_entero(datos.get("materia_id", ""))
    if estudiante_id is None or materia_id is None:
        return "estudiante_id y materia_id deben ser números enteros"
    periodo = str(datos.get("periodo", "")).strip()
    if periodo == "":
        return "El período es obligatorio"
    if not es_periodo_valido(periodo):
        return "El período debe tener el formato AAAA-N, por ejemplo 2026-1"
    if estudiante_id not in ids_registrados(gestor_estudiantes):
        return f"No existe un estudiante con id {estudiante_id}"
    materia = obtener_materia(materia_id)
    if materia is None:
        return f"No existe una materia con id {materia_id}"
    if not materia.hay_cupo():
        return f"La materia {materia.nombre} no tiene cupos disponibles"
    for registro in gestor_matriculas.leer():
        existente = (registro["estudiante_id"], registro["materia_id"], registro["periodo"])
        if existente == (estudiante_id, materia_id, periodo):
            return "El estudiante ya está matriculado en esa materia en ese período"
    return None


def crear_matricula(datos):
    error = validar_matricula(datos)
    if error:
        return False, error
    materia = obtener_materia(int(str(datos["materia_id"]).strip()))
    matricula = Matricula(
        siguiente_id(gestor_matriculas),
        int(str(datos["estudiante_id"]).strip()),
        materia.id,
        str(datos["periodo"]).strip(),
    )
    materia.ocupar_cupo()
    if not reemplazar(gestor_materias, materia):
        return False, "No se pudo escribir el archivo"
    if not guardar_nuevo(gestor_matriculas, matricula):
        materia.liberar_cupo()
        reemplazar(gestor_materias, materia)
        return False, "No se pudo escribir el archivo"
    return True, f"Matrícula {matricula.id} registrada: {materia.nombre} ({matricula.periodo})"


def obtener_matriculas():
    return leer_objetos(gestor_matriculas, Matricula)


def obtener_matricula(id_matricula):
    return obtener_por_id(gestor_matriculas, Matricula, id_matricula)


def registrar_nota(id_matricula, nota):
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return False, f"No existe la matrícula {id_matricula}"
    valor = str(nota).strip().replace(",", ".")
    if not Materia.es_nota_valida(valor):
        return False, "La nota debe ser un número entre 0 y 20"
    matricula.nota = round(float(valor), 2)
    if not reemplazar(gestor_matriculas, matricula):
        return False, "No se pudo escribir el archivo"
    return True, f"Nota {matricula.nota:.2f} registrada en la matrícula {id_matricula}: {matricula.estado()}"


def retirar_matricula(id_matricula):
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return False, f"No existe la matrícula {id_matricula}"
    materia = obtener_materia(matricula.materia_id)
    if materia is not None:
        materia.liberar_cupo()
        if not reemplazar(gestor_materias, materia):
            return False, "No se pudo escribir el archivo"
    if not eliminar(gestor_matriculas, id_matricula):
        return False, "No se pudo escribir el archivo"
    return True, f"Matrícula {id_matricula} retirada y cupo liberado"


def certificado(id_matricula):
    matricula = obtener_matricula(id_matricula)
    if matricula is None:
        return None
    estudiantes = indice_por_id(gestor_estudiantes, Estudiante)
    materias = indice_por_id(gestor_materias, Materia)
    estudiante = estudiantes.get(matricula.estudiante_id)
    materia = materias.get(matricula.materia_id)
    texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
    if estudiante:
        texto += f"Estudiante: {estudiante.nombre_completo()}   ({estudiante.carnet})\n"
    else:
        texto += "Estudiante: eliminado\n"
    if materia:
        texto += f"Materia   : {materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos\n"
    else:
        texto += "Materia   : eliminada\n"
    texto += "-" * 42 + "\n"
    nota = "sin registrar" if matricula.nota is None else f"{matricula.nota:g}"
    texto += f"Nota      : {nota}\n"
    texto += f"Estado    : {matricula.estado()}"
    return texto


def matriculas_por_estudiante():
    agrupadas = {}
    for matricula in obtener_matriculas():
        agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
    return agrupadas


def promedio_de_estudiante(id_estudiante):
    if id_estudiante not in ids_registrados(gestor_estudiantes):
        return False, f"No existe un estudiante con id {id_estudiante}"
    matriculas = matriculas_por_estudiante().get(id_estudiante, [])
    notas = [matricula.nota for matricula in matriculas if matricula.nota is not None]
    if not notas:
        return False, "El estudiante todavía no tiene notas registradas"
    return True, round(sum(notas) / len(notas), 2)


def resumen():
    estudiantes = obtener_estudiantes()
    matriculas = obtener_matriculas()
    return {
        "estudiantes": len(estudiantes),
        "carreras": sorted({e.carrera for e in estudiantes if e.carrera != ""}),
        "materias_sin_cupo": [m.nombre for m in materias_sin_cupo()],
        "matriculas": len(matriculas),
        "matriculas_aprobadas": len([m for m in matriculas if m.esta_aprobada()]),
    }
