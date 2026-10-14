import math
from abc import ABC, abstractmethod

from models import Cliente, Producto, Venta, Pago
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


class ClienteController(CrudBase):

    def __init__(self, archivo="data/clientes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Cliente.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for cliente in self.lista:
            datos.append(cliente.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            usados = {c.email for c in self.lista if c.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        telefono = str(datos.get("telefono", "")).strip()
        if telefono != "" and not telefono.isdigit():
            return "El teléfono solo puede tener números"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_cliente):
        for cliente in self.lista:
            if cliente.id == id_cliente:
                return cliente
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for cliente in self.lista:
            if (texto in cliente.nombre.lower()
                    or texto in cliente.apellido.lower()
                    or texto in cliente.email
                    or texto in cliente.telefono
                    or texto in cliente.ciudad.lower()):
                encontrados.append(cliente)
        return encontrados

    def siguiente(self):
        mayor = 0
        for cliente in self.lista:
            if cliente.id > mayor:
                mayor = cliente.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cliente = Cliente(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          str(datos["apellido"]).strip().title(),
                          str(datos["email"]).strip().lower(),
                          str(datos.get("telefono", "")).strip(),
                          str(datos.get("ciudad", "")).strip().title())
        self.lista.append(cliente)
        self.guardar()
        return True, f"Cliente creado: {cliente.etiqueta()}"

    def actualizar(self, id_cliente, datos):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe un cliente con id {id_cliente}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "apellido", "email", "telefono", "ciudad"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_cliente)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "ciudad"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            setattr(cliente, campo, valor)

        self.guardar()
        return True, f"Cliente {id_cliente} actualizado"

    def eliminar(self, id_cliente):
        cliente = self.obtener(id_cliente)
        if cliente is None:
            return False, f"No existe un cliente con id {id_cliente}"

        self.lista.remove(cliente)
        self.guardar()
        return True, f"Cliente {id_cliente} eliminado"

    def ciudades(self):
        return sorted({c.ciudad for c in self.lista if c.ciudad != ""})


class ProductoController(CrudBase):

    def __init__(self, archivo="data/productos.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Producto.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for producto in self.lista:
            datos.append(producto.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "precio"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "precio" in datos and not Producto.es_precio_valido(datos["precio"]):
            return f"Precio inválido: '{datos['precio']}' (debe ser un número mayor a 0)"

        stock = str(datos.get("stock", "")).strip()
        if stock != "" and not stock.isdigit():
            return "El stock debe ser un número entero positivo"

        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otro in self.lista:
                if otro.nombre == nombre and otro.id != id_actual:
                    return f"Ya existe un producto llamado {nombre}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_producto):
        for producto in self.lista:
            if producto.id == id_producto:
                return producto
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for producto in self.lista:
            if texto in producto.nombre.lower():
                encontrados.append(producto)
        return encontrados

    def siguiente(self):
        mayor = 0
        for producto in self.lista:
            if producto.id > mayor:
                mayor = producto.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        stock = str(datos.get("stock", "")).strip()
        producto = Producto(self.siguiente(),
                            str(datos["nombre"]).strip().title(),
                            float(datos["precio"]),
                            int(stock) if stock != "" else 0)
        self.lista.append(producto)
        self.guardar()
        return True, f"Producto creado: {producto.etiqueta()}"

    def actualizar(self, id_producto, datos):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe un producto con id {id_producto}"
        if not datos:
            return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "precio", "stock"}
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_producto)
        if error:
            return False, error

        if "nombre" in datos:
            producto.nombre = str(datos["nombre"]).strip().title()
        if "precio" in datos:
            producto.precio = float(datos["precio"])
        if "stock" in datos:
            producto.stock = int(datos["stock"])

        self.guardar()
        return True, f"Producto {id_producto} actualizado"

    def eliminar(self, id_producto):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe un producto con id {id_producto}"

        self.lista.remove(producto)
        self.guardar()
        return True, f"Producto {id_producto} eliminado"

    def con_stock_bajo(self):
        bajos = []
        for producto in self.lista:
            if producto.stock_bajo():
                bajos.append(producto)
        return bajos


class VentaController(CrudBase):

    def __init__(self, clientes, productos, archivo="data/ventas.json"):
        self.clientes = clientes
        self.productos = productos
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Venta.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for venta in self.lista:
            datos.append(venta.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            cliente_id = int(datos.get("cliente_id", 0))
            producto_id = int(datos.get("producto_id", 0))
            cantidad = int(datos.get("cantidad", 0))
        except (TypeError, ValueError):
            return "cliente_id, producto_id y cantidad deben ser números enteros"

        if cantidad <= 0:
            return "La cantidad debe ser mayor a 0"
        if self.clientes.obtener(cliente_id) is None:
            return f"No existe un cliente con id {cliente_id}"

        producto = self.productos.obtener(producto_id)
        if producto is None:
            return f"No existe un producto con id {producto_id}"
        if not producto.hay_stock(cantidad):
            return (f"Stock insuficiente de {producto.nombre}: "
                    f"hay {producto.stock}, piden {cantidad}")
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_venta):
        for venta in self.lista:
            if venta.id == id_venta:
                return venta
        return None

    def buscar(self, texto):
        texto = texto.strip()
        encontradas = []
        if texto == "":
            return encontradas

        for venta in self.lista:
            if texto in venta.fecha:
                encontradas.append(venta)
        return encontradas

    def siguiente(self):
        mayor = 0
        for venta in self.lista:
            if venta.id > mayor:
                mayor = venta.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        producto = self.productos.obtener(int(datos["producto_id"]))
        venta = Venta(self.siguiente(),
                      int(datos["cliente_id"]),
                      producto.id,
                      int(datos["cantidad"]),
                      producto.precio)

        producto.descontar_stock(venta.cantidad)
        self.productos.guardar()
        self.lista.append(venta)
        self.guardar()
        return True, f"Venta {venta.id} registrada por ${venta.calcular_total():.2f}"

    def actualizar(self, id_venta, datos):
        return False, "Las ventas no se pueden modificar: anúlela y registre otra"

    def eliminar(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return False, f"No existe la venta {id_venta}"

        producto = self.productos.obtener(venta.producto_id)
        if producto is not None:
            producto.devolver_stock(venta.cantidad)
            self.productos.guardar()

        self.lista.remove(venta)
        self.guardar()
        return True, f"Venta {id_venta} anulada y stock devuelto"

    def comprobante(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return None

        cliente = self.clientes.obtener(venta.cliente_id)
        producto = self.productos.obtener(venta.producto_id)
        total = venta.calcular_total()

        texto = f"COMPROBANTE #{venta.id}   fecha: {venta.fecha}\n"
        texto += f"Cliente : {cliente.nombre_completo() if cliente else 'eliminado'}\n"
        texto += f"Producto: {producto.nombre if producto else 'eliminado'}\n"
        texto += f"Cantidad: {venta.cantidad} x ${venta.precio_unitario:.2f}\n"
        texto += "-" * 42 + "\n"
        texto += f"SUBTOTAL: ${total:.2f}\n"
        texto += f"TOTAL con IVA: ${Producto.con_iva(total):.2f}"
        return texto

    def ventas_por_cliente(self):
        agrupadas = {}
        for venta in self.lista:
            if venta.cliente_id not in agrupadas:
                agrupadas[venta.cliente_id] = []
            agrupadas[venta.cliente_id].append(venta)
        return agrupadas

    def total_vendido(self):
        total = 0
        for venta in self.lista:
            total += venta.calcular_total()
        return round(total, 2)


class PagoController(CrudBase):

    def __init__(self, ventas, archivo="data/pagos.json"):
        self.ventas = ventas
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Pago.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for pago in self.lista:
            datos.append(pago.a_diccionario())
        self.gestor.guardar(datos)

    def leer(self):
        return self.lista

    def obtener(self, id_pago):
        for pago in self.lista:
            if pago.id == id_pago:
                return pago
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for pago in self.lista:
            if texto in pago.fecha or texto in pago.metodo:
                encontrados.append(pago)
        return encontrados

    def siguiente(self):
        mayor = 0
        for pago in self.lista:
            if pago.id > mayor:
                mayor = pago.id
        return mayor + 1

    def ventas_pagadas(self):
        return {pago.venta_id for pago in self.lista}

    def esta_pagada(self, venta_id):
        return venta_id in self.ventas_pagadas()

    def pago_de_venta(self, venta_id):
        for pago in self.lista:
            if pago.venta_id == venta_id:
                return pago
        return None

    def total_a_pagar(self, venta):
        return Producto.con_iva(venta.calcular_total())

    def validar(self, datos):
        try:
            venta_id = int(datos.get("venta_id", 0))
        except (TypeError, ValueError):
            return "El id de la venta debe ser un número entero", None

        venta = self.ventas.obtener(venta_id)
        if venta is None:
            return f"No existe la venta {venta_id}", None
        if self.esta_pagada(venta_id):
            return f"La venta {venta_id} ya está pagada", None

        metodo = str(datos.get("metodo", "")).strip().lower()
        if not Pago.es_metodo_valido(metodo):
            return f"Método de pago no válido: '{metodo}'", None

        total = self.total_a_pagar(venta)
        if metodo != "efectivo":
            return None, (venta, metodo, total)

        try:
            recibido = float(str(datos.get("recibido", "")).strip())
        except ValueError:
            return "El monto recibido debe ser un número", None
        if not math.isfinite(recibido):
            return "El monto recibido debe ser un número", None
        if recibido < total:
            return f"Monto insuficiente: faltan ${total - recibido:.2f}", None
        return None, (venta, metodo, recibido)

    def crear(self, datos):
        error, resultado = self.validar(datos)
        if error:
            return False, error

        venta, metodo, recibido = resultado
        pago = Pago(self.siguiente(),
                    venta.id,
                    self.total_a_pagar(venta),
                    metodo,
                    recibido)
        self.lista.append(pago)
        self.guardar()
        return True, f"Pago {pago.id} registrado · cambio ${pago.calcular_cambio():.2f}"

    def actualizar(self, id_pago, datos):
        return False, "Un pago registrado no se puede modificar"

    def eliminar(self, id_pago):
        return False, "Un pago registrado no se puede eliminar"

    def recibo(self, id_pago):
        pago = self.obtener(id_pago)
        if pago is None:
            return None

        texto = f"RECIBO DE PAGO #{pago.id}   fecha: {pago.fecha}\n"
        texto += f"Venta   : #{pago.venta_id}\n"
        texto += f"Método  : {pago.metodo}\n"
        texto += "-" * 42 + "\n"
        texto += f"TOTAL   : ${pago.monto:.2f}\n"
        texto += f"Recibido: ${pago.recibido:.2f}\n"
        texto += f"Cambio  : ${pago.calcular_cambio():.2f}\n"
        texto += "Estado  : PAGADA"
        return texto

    def ventas_pendientes(self):
        pagadas = self.ventas_pagadas()
        pendientes = []
        for venta in self.ventas.leer():
            if venta.id not in pagadas:
                pendientes.append(venta)
        return pendientes

    def total_cobrado(self):
        total = 0
        for pago in self.lista:
            total += pago.monto
        return round(total, 2)

    def anular_venta(self, id_venta):
        if self.esta_pagada(id_venta):
            return False, "No se puede anular una venta pagada"
        return self.ventas.eliminar(id_venta)
