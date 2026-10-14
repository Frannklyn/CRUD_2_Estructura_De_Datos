from datetime import date


class ModeloBase:

    def __init__(self, id_registro):
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        datos = dict(datos)
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)

    def a_diccionario(self):
        return {"id": self.id}

    def etiqueta(self):
        return f"registro {self.id}"

    def __str__(self):
        return f"[{self.id}] {self.etiqueta()}"


class Persona(ModeloBase):

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Cliente(Persona):

    def __init__(self, id_registro, nombre, apellido, email, telefono="", ciudad=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.telefono = telefono
        self.ciudad = ciudad

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["telefono"] = self.telefono
        datos["ciudad"] = self.ciudad
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.email} · {self.ciudad or 'sin ciudad'}"


class Producto(ModeloBase):

    STOCK_MINIMO = 5
    IVA = 0.15
    total_creados = 0

    def __init__(self, id_registro, nombre, precio, stock=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.precio = float(precio)
        self.stock = int(stock)
        Producto.total_creados += 1

    @staticmethod
    def es_precio_valido(valor):
        try:
            return float(valor) > 0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def con_iva(monto):
        return round(monto * (1 + Producto.IVA), 2)

    def stock_bajo(self):
        return self.stock <= Producto.STOCK_MINIMO

    def hay_stock(self, cantidad):
        return 0 < cantidad <= self.stock

    def descontar_stock(self, cantidad):
        self.stock -= cantidad

    def devolver_stock(self, cantidad):
        self.stock += cantidad

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["precio"] = self.precio
        datos["stock"] = self.stock
        return datos

    def etiqueta(self):
        alerta = " ⚠ stock bajo" if self.stock_bajo() else ""
        return f"{self.nombre} · ${self.precio:.2f} · stock {self.stock}{alerta}"


class Venta(ModeloBase):

    def __init__(self, id_registro, cliente_id, producto_id, cantidad,
                 precio_unitario, fecha=""):
        super().__init__(id_registro)
        self.cliente_id = int(cliente_id)
        self.producto_id = int(producto_id)
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.fecha = fecha or date.today().isoformat()

    def calcular_total(self):
        return round(self.cantidad * self.precio_unitario, 2)

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["cliente_id"] = self.cliente_id
        datos["producto_id"] = self.producto_id
        datos["cantidad"] = self.cantidad
        datos["precio_unitario"] = self.precio_unitario
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · cliente {self.cliente_id} · "
                f"{self.cantidad} x producto {self.producto_id} "
                f"= ${self.calcular_total():.2f}")


# =====================================================================
# PAGO: un solo pago por venta
# =====================================================================
class Pago(ModeloBase):
    """El pago de UNA venta, en UN solo pago. Se relaciona con la venta por id."""

    # ATRIBUTO ESTÁTICO: los métodos de pago aceptados. TUPLA porque no cambian.
    METODOS = ("efectivo", "tarjeta", "transferencia")

    def __init__(self, id_registro, venta_id, monto, metodo, recibido=0, fecha=""):
        super().__init__(id_registro)
        self.venta_id = int(venta_id)
        self.monto = round(float(monto), 2)          # foto del total CON IVA del momento
        self.metodo = metodo
        # Si no se indicó lo recibido (tarjeta, transferencia), es el monto exacto
        self.recibido = round(float(recibido), 2) if recibido else self.monto
        self.fecha = fecha or date.today().isoformat()

    # MÉTODO ESTÁTICO: la regla no depende de ningún pago concreto
    @staticmethod
    def es_metodo_valido(metodo):
        return str(metodo).strip().lower() in Pago.METODOS

    # MÉTODO DE INSTANCIA: se calcula, NO se guarda
    def calcular_cambio(self):
        return round(self.recibido - self.monto, 2)

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["venta_id"] = self.venta_id
        datos["monto"] = self.monto
        datos["metodo"] = self.metodo
        datos["recibido"] = self.recibido
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · venta {self.venta_id} · "
                f"${self.monto:.2f} en {self.metodo}")