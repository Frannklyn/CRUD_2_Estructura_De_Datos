from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import (
    CAMPOS_ESTUDIANTE, CAMPOS_MATERIA,
    crear_estudiante, obtener_estudiantes, obtener_estudiante, buscar_estudiantes,
    actualizar_estudiante, eliminar_estudiante,
    crear_materia, obtener_materias, obtener_materia, buscar_materias,
    actualizar_materia, eliminar_materia, materias_sin_cupo,
    crear_matricula, obtener_matriculas, registrar_nota, retirar_matricula,
    certificado, matriculas_por_estudiante, promedio_de_estudiante, resumen
)


def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


def opcion_crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet: "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*crear_estudiante(datos))
    pausa()


def opcion_listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(obtener_estudiantes(), "Todavía no hay estudiantes.")
    pausa()


def opcion_buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    mostrar_lista(buscar_estudiantes(termino), f"Ningún estudiante coincide con '{termino}'.")
    pausa()


def opcion_ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = obtener_estudiante(pedir_entero("Id: "))
    if estudiante is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(estudiante)
    pausa()


def opcion_actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = obtener_estudiante(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()
    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")
    cambios = {}
    for campo in CAMPOS_ESTUDIANTE:
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*actualizar_estudiante(id_estudiante, cambios))
    pausa()


def opcion_eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = obtener_estudiante(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()
    imprimir_info(f"Se eliminará: {estudiante.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*eliminar_estudiante(id_estudiante))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def opcion_crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Código (ej. MAT101): "),
        "creditos": input("Créditos (1 a 10): "),
        "cupos": input("Cupos (0 a 30): "),
    }
    mostrar_resultado(*crear_materia(datos))
    pausa()


def opcion_listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(obtener_materias(), "Todavía no hay materias.")
    pausa()


def opcion_buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(buscar_materias(termino), f"Ninguna materia coincide con '{termino}'.")
    pausa()


def opcion_ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = obtener_materia(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("No encontrada")
    else:
        mostrar_detalle(materia)
    pausa()


def opcion_actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = obtener_materia(id_materia)
    if materia is None:
        imprimir_error("No encontrada")
        return pausa()
    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")
    cambios = {}
    for campo in CAMPOS_MATERIA:
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo
    mostrar_resultado(*actualizar_materia(id_materia, cambios))
    pausa()


def opcion_eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = obtener_materia(id_materia)
    if materia is None:
        imprimir_error("No encontrada")
        return pausa()
    imprimir_info(f"Se eliminará: {materia.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*eliminar_materia(id_materia))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def opcion_materias_sin_cupo():
    imprimir_titulo("MATERIAS SIN CUPO")
    mostrar_lista(materias_sin_cupo(), "Todas las materias tienen cupo.")
    pausa()


def opcion_matricular():
    imprimir_titulo("MATRICULAR")
    imprimir_info("Estudiantes:")
    mostrar_lista(obtener_estudiantes())
    imprimir_info("Materias:")
    mostrar_lista(obtener_materias())
    datos = {
        "estudiante_id": pedir_entero("\nId del estudiante: "),
        "materia_id": pedir_entero("Id de la materia: "),
        "periodo": input("Período (ej. 2026-1): "),
    }
    if datos["estudiante_id"] is None or datos["materia_id"] is None:
        imprimir_error("Los ids deben ser números enteros")
        return pausa()
    mostrar_resultado(*crear_matricula(datos))
    pausa()


def opcion_listar_matriculas():
    imprimir_titulo("MATRÍCULAS")
    mostrar_lista(obtener_matriculas(), "Todavía no hay matrículas.")
    pausa()


def opcion_registrar_nota():
    imprimir_titulo("REGISTRAR NOTA")
    mostrar_lista(obtener_matriculas(), "Todavía no hay matrículas.")
    id_matricula = pedir_entero("\nId de la matrícula: ")
    if id_matricula is None:
        imprimir_error("El id debe ser un número entero")
        return pausa()
    nota = input("Nota (0 a 20): ")
    mostrar_resultado(*registrar_nota(id_matricula, nota))
    pausa()


def opcion_ver_certificado():
    imprimir_titulo("CERTIFICADO")
    texto = certificado(pedir_entero("Id de la matrícula: "))
    if texto is None:
        imprimir_error("No existe esa matrícula")
    else:
        print()
        print(texto)
    pausa()


def opcion_retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_matricula = pedir_entero("Id de la matrícula: ")
    if id_matricula is None:
        imprimir_error("El id debe ser un número entero")
        return pausa()
    if confirmar("Se liberará el cupo. ¿Confirma?"):
        mostrar_resultado(*retirar_matricula(id_matricula))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def opcion_matriculas_por_estudiante():
    imprimir_titulo("MATRÍCULAS POR ESTUDIANTE")
    agrupadas = matriculas_por_estudiante()
    if not agrupadas:
        imprimir_info("Todavía no hay matrículas.")
    for id_estudiante, matriculas in sorted(agrupadas.items()):
        estudiante = obtener_estudiante(id_estudiante)
        nombre = estudiante.nombre_completo() if estudiante else "Estudiante eliminado"
        print(f"\n  {nombre} ({len(matriculas)})")
        for matricula in matriculas:
            print(f"    {matricula}")
    pausa()


def opcion_promedio_estudiante():
    imprimir_titulo("PROMEDIO DE UN ESTUDIANTE")
    id_estudiante = pedir_entero("Id del estudiante: ")
    exito, resultado = promedio_de_estudiante(id_estudiante)
    if exito:
        imprimir_exito(f"Promedio del estudiante {id_estudiante}: {resultado}")
    else:
        imprimir_error(resultado)
    pausa()


def opcion_resumen():
    imprimir_titulo("RESUMEN")
    datos = resumen()
    print(f"  Estudiantes          : {datos['estudiantes']}")
    print(f"  Carreras             : {', '.join(datos['carreras']) or '-'}")
    print(f"  Materias sin cupo    : {', '.join(datos['materias_sin_cupo']) or 'ninguna'}")
    print(f"  Matrículas           : {datos['matriculas']}")
    print(f"  Matrículas aprobadas : {datos['matriculas_aprobadas']}")
    pausa()


MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", opcion_crear_estudiante),
    "2": ("Ver todos", opcion_listar_estudiantes),
    "3": ("Buscar", opcion_buscar_estudiante),
    "4": ("Ver por id", opcion_ver_estudiante),
    "5": ("Actualizar", opcion_actualizar_estudiante),
    "6": ("Eliminar", opcion_eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", opcion_crear_materia),
    "2": ("Ver todas", opcion_listar_materias),
    "3": ("Buscar", opcion_buscar_materia),
    "4": ("Ver por id", opcion_ver_materia),
    "5": ("Actualizar", opcion_actualizar_materia),
    "6": ("Eliminar", opcion_eliminar_materia),
    "7": ("Materias sin cupo", opcion_materias_sin_cupo),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Matricular", opcion_matricular),
    "2": ("Ver todas", opcion_listar_matriculas),
    "3": ("Registrar nota", opcion_registrar_nota),
    "4": ("Ver certificado", opcion_ver_certificado),
    "5": ("Retirar matrícula", opcion_retirar_matricula),
    "6": ("Matrículas por estudiante", opcion_matriculas_por_estudiante),
    "7": ("Promedio de un estudiante", opcion_promedio_estudiante),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()
        tecla = input("Opción: ").strip()
        if tecla not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue
        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO")
        print("  1. Estudiantes")
        print("  2. Materias")
        print("  3. Matrículas")
        print("  4. Resumen")
        print("  0. Salir\n")
        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)
        elif tecla == "4":
            opcion_resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego!")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
