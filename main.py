import logging
from abc import ABC, abstractmethod
from datetime import datetime

# =====================================================================
# MÓDULO 1: CONFIGURACIÓN DE LOGS Y EXCEPCIONES PERSONALIZADAS
# (Ideal para rama: feature/excepciones-logs)
# =====================================================================
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


class ErrorSoftwareFJ(Exception):
    """Excepción base para todos los errores del sistema Software FJ."""
    pass


class DatosInvalidosError(ErrorSoftwareFJ):
    """Se lanza cuando un dato ingresado es inválido o faltante."""
    pass


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta reservar un servicio inactivo o sin cupo."""
    pass


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Se lanza ante operaciones no permitidas o estados inválidos en reservas."""
    pass


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Se lanza cuando ocurre un fallo al calcular costos, impuestos o descuentos."""
    pass


# =====================================================================
# MÓDULO 2: ENTIDAD ABSTRACTA Y CLIENTE (Encapsulación y Validaciones)
# (Ideal para rama: feature/clientes)
# =====================================================================
class EntidadSistema(ABC):
    """Clase abstracta que representa cualquier entidad general del sistema."""

    def __init__(self, entidad_id: str):
        if not entidad_id or not isinstance(entidad_id, str):
            raise DatosInvalidosError("El ID de la entidad debe ser un texto no vacío.")
        self._id = entidad_id.strip()
        self._fecha_creacion = datetime.now()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""
        pass


class Cliente(EntidadSistema):
    """Representa un cliente de Software FJ con encapsulación y validaciones estrictas."""

    def __init__(self, cliente_id: str, nombre: str, correo: str, telefono: str):
        super().__init__(cliente_id)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatosInvalidosError(f"Nombre de cliente inválido: '{valor}'.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or "@" not in valor or "." not in valor.split("@")[-1]:
            raise DatosInvalidosError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not valor.isdigit() or len(valor) < 7:
            raise DatosInvalidosError(f"Teléfono inválido (solo dígitos, mín. 7): '{valor}'.")
        self._telefono = valor

    def describir(self) -> str:
        return f"Cliente[{self.id}] {self.nombre} ({self.correo})"


# =====================================================================
# MÓDULO 3: CLASE ABSTRACTA SERVICIO Y 3 SERVICIOS ESPECIALIZADOS
# (Ideal para rama: feature/servicios)
# =====================================================================
class Servicio(EntidadSistema, ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, servicio_id: str, nombre: str, tarifa_hora: float, disponible: bool = True):
        super().__init__(servicio_id)
        if not nombre or not isinstance(nombre, str):
            raise DatosInvalidosError("El nombre del servicio no puede estar vacío.")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise DatosInvalidosError(f"La tarifa por hora debe ser positiva: {tarifa_hora}.")
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self._disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool):
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion_horas: float):
        """Valida reglas específicas del servicio antes de reservar."""
        pass

    @abstractmethod
    def calcular_costo(self, duracion_horas: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        """
        Método sobrecargado mediante parámetros opcionales (impuesto y descuento)
        para calcular el costo total del servicio.
        """
        pass

    def _aplicar_ajustes(self, subtotal: float, impuesto: float, descuento: float) -> float:
        """Aplica descuentos e impuestos validando que no existan cálculos inconsistentes."""
        if not (0 <= descuento < 1):
            raise CalculoInconsistenteError(f"Descuento fuera de rango (0 a <1): {descuento}")
        if impuesto < 0 or impuesto > 0.5:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango (0 a 0.5): {impuesto}")
        con_descuento = subtotal * (1 - descuento)
        total = con_descuento * (1 + impuesto)
        if total < 0:
            raise CalculoInconsistenteError("El costo final no puede ser negativo.")
        return round(total, 2)


class ReservaSala(Servicio):
    """Servicio especializado: Reserva de salas de reuniones o capacitación."""

    def __init__(self, servicio_id: str, nombre: str, tarifa_hora: float, capacidad: int, disponible: bool = True):
        super().__init__(servicio_id, nombre, tarifa_hora, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatosInvalidosError(f"Capacidad de sala inválida: {capacidad}.")
        self._capacidad = capacidad

    def validar_parametros(self, duracion_horas: float):
        if not isinstance(duracion_horas, (int, float)) or duracion_horas < 1 or duracion_horas > 12:
            raise DatosInvalidosError("La reserva de sala debe durar entre 1 y 12 horas.")

    def calcular_costo(self, duracion_horas: float, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion_horas)
        subtotal = self.tarifa_hora * duracion_horas
        return self._aplicar_ajustes(subtotal, impuesto, descuento)

    def describir(self) -> str:
        return f"Sala[{self.id}] '{self.nombre}' | Capacidad: {self._capacidad} pers. | ${self.tarifa_hora}/h"


class AlquilerEquipo(Servicio):
    """Servicio especializado: Alquiler de equipos tecnológicos."""

    def __init__(self, servicio_id: str, nombre: str, tarifa_hora: float, stock: int, disponible: bool = True):
        super().__init__(servicio_id, nombre, tarifa_hora, disponible)
        if not isinstance(stock, int) or stock < 0:
            raise DatosInvalidosError(f"Stock de equipo inválido: {stock}.")
        self._stock = stock

    def validar_parametros(self, duracion_horas: float):
        if self._stock <= 0:
            raise ServicioNoDisponibleError(f"No hay unidades disponibles para '{self.nombre}'.")
        if not isinstance(duracion_horas, (int, float)) or duracion_horas < 2:
            raise DatosInvalidosError("El alquiler de equipos requiere mínimo 2 horas.")

    def calcular_costo(self, duracion_horas: float, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion_horas)
        # Incluye cargo fijo de seguro de equipo ($10.000)
        subtotal = (self.tarifa_hora * duracion_horas) + 10000
        return self._aplicar_ajustes(subtotal, impuesto, descuento)

    def describir(self) -> str:
        return f"Equipo[{self.id}] '{self.nombre}' | Stock: {self._stock} | ${self.tarifa_hora}/h"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado: Consultorías y asesorías técnicas."""

    def __init__(self, servicio_id: str, nombre: str, tarifa_hora: float, especialidad: str, disponible: bool = True):
        super().__init__(servicio_id, nombre, tarifa_hora, disponible)
        if not especialidad or not isinstance(especialidad, str):
            raise DatosInvalidosError("La especialidad de la asesoría es obligatoria.")
        self._especialidad = especialidad.strip()

    def validar_parametros(self, duracion_horas: float):
        if not isinstance(duracion_horas, (int, float)) or duracion_horas <= 0 or duracion_horas > 8:
            raise DatosInvalidosError("La asesoría especializada debe durar entre 1 y 8 horas.")

    def calcular_costo(self, duracion_horas: float, impuesto: float = 0.0, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion_horas)
        subtotal = self.tarifa_hora * duracion_horas
        return self._aplicar_ajustes(subtotal, impuesto, descuento)

    def describir(self) -> str:
        return f"Asesoría[{self.id}] '{self.nombre}' ({self._especialidad}) | ${self.tarifa_hora}/h"


# =====================================================================
# MÓDULO 4: CLASE RESERVA Y GESTOR INTEGRAL (Sin Base de Datos)
# (Ideal para rama: feature/reservas)
# =====================================================================
class Reserva(EntidadSistema):
    """Integra Cliente, Servicio, duración y estado con manejo avanzado de excepciones."""

    def __init__(self, reserva_id: str, cliente: Cliente, servicio: Servicio, duracion_horas: float):
        super().__init__(reserva_id)
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Se requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Se requiere una instancia válida de Servicio.")
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = duracion_horas
        self._estado = "PENDIENTE"
        self._costo_total = 0.0

    @property
    def estado(self) -> str:
        return self._estado

    def confirmar(self):
        if self._estado != "PENDIENTE":
            raise ReservaInvalidaError(f"No se puede confirmar una reserva en estado '{self._estado}'.")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self._servicio.nombre}' no está disponible.")
        try:
            self._servicio.validar_parametros(self._duracion_horas)
        except ErrorSoftwareFJ as err:
            # Encadenamiento de excepciones (raise ... from ...)
            raise ReservaInvalidaError(f"Fallo al confirmar la reserva {self.id}.") from err
        self._estado = "CONFIRMADA"
        logging.info(f"Reserva {self.id} confirmada para {self._cliente.nombre}.")

    def cancelar(self):
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError(f"La reserva {self.id} ya se encuentra cancelada.")
        if self._estado == "PROCESADA":
            raise ReservaInvalidaError(f"No se puede cancelar la reserva {self.id} porque ya fue procesada.")
        self._estado = "CANCELADA"
        logging.info(f"Reserva {self.id} cancelada correctamente.")

    def procesar(self, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        if self._estado != "CONFIRMADA":
            raise ReservaInvalidaError(f"Solo se pueden procesar reservas CONFIRMADAS (estado actual: {self._estado}).")
        try:
            self._costo_total = self._servicio.calcular_costo(
                self._duracion_horas, impuesto=impuesto, descuento=descuento
            )
        except ErrorSoftwareFJ as err:
            # Encadenamiento de excepciones para conservar la causa raíz
            raise ReservaInvalidaError(f"Error al procesar el pago de la reserva {self.id}.") from err
        self._estado = "PROCESADA"
        logging.info(f"Reserva {self.id} procesada. Costo total: ${self._costo_total:,.2f}")
        return self._costo_total

    def describir(self) -> str:
        return (
            f"Reserva[{self.id}] | {self._cliente.nombre} -> {self._servicio.nombre} "
            f"| {self._duracion_horas}h | Estado: {self._estado} | Total: ${self._costo_total:,.2f}"
        )


class GestorSoftwareFJ:
    """Gestiona clientes, servicios y reservas en memoria usando listas internas."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente_id, nombre, correo, telefono):
        try:
            cliente = Cliente(cliente_id, nombre, correo, telefono)
        except ErrorSoftwareFJ as e:
            logging.error(f"[Registro Cliente Fallido] {e}")
            print(f"❌ Error registrando cliente: {e}")
            return None
        else:
            # Uso de try/except/else: solo se ejecuta si no hubo excepciones
            self.clientes.append(cliente)
            logging.info(f"Cliente registrado: {cliente.describir()}")
            print(f"✅ Registrado: {cliente.describir()}")
            return cliente

    def registrar_servicio(self, servicio_clase, *args, **kwargs):
        try:
            servicio = servicio_clase(*args, **kwargs)
        except (ErrorSoftwareFJ, TypeError) as e:
            logging.error(f"[Registro Servicio Fallido] {e}")
            print(f"❌ Error creando servicio: {e}")
            return None
        else:
            self.servicios.append(servicio)
            logging.info(f"Servicio registrado: {servicio.describir()}")
            print(f"✅ Creado: {servicio.describir()}")
            return servicio

    def ejecutar_reserva(self, reserva_id, cliente, servicio, duracion, impuesto=0.19, descuento=0.0, cancelar=False):
        reserva = None
        try:
            reserva = Reserva(reserva_id, cliente, servicio, duracion)
            if cancelar:
                reserva.cancelar()
                print(f"⚠️ {reserva.describir()}")
            else:
                reserva.confirmar()
                reserva.procesar(impuesto=impuesto, descuento=descuento)
                print(f"✅ {reserva.describir()}")
            self.reservas.append(reserva)
        except ErrorSoftwareFJ as e:
            causa = f" | Causa original: {e.__cause__}" if e.__cause__ else ""
            logging.error(f"[Reserva Fallida {reserva_id}] {e}{causa}")
            print(f"❌ Error en reserva {reserva_id}: {e}{causa}")
        finally:
            # Uso de try/except/finally: siempre deja trazabilidad de cierre
            logging.info(f"Finalizó intento de operación para reserva {reserva_id}.")


# =====================================================================
# MÓDULO 5: SIMULACIÓN DE 12 OPERACIONES COMPLETAS (Válidas e Inválidas)
# (Ideal para rama: feature/simulaciones)
# =====================================================================
def ejecutar_simulaciones():
    print("=== INICIANDO SISTEMA INTEGRAL SOFTWARE FJ ===\n")
    logging.info("Inicio de ejecución de simulaciones en Software FJ.")
    sistema = GestorSoftwareFJ()

    # 1. Registro válido de cliente 1
    c1 = sistema.registrar_cliente("CL-01", "Keith Rivaldo", "keith@softwarefj.com", "3001234567")
    # 2. Registro válido de cliente 2
    c2 = sistema.registrar_cliente("CL-02", "Laura Gómez", "laura@empresa.co", "3109876543")
    # 3. Registro INVÁLIDO de cliente (correo mal formado)
    sistema.registrar_cliente("CL-03", "Pedro", "pedro-sin-arroba", "3001112233")
    # 4. Registro INVÁLIDO de cliente (teléfono con letras)
    sistema.registrar_cliente("CL-04", "Ana Torres", "ana@mail.com", "ABC1234")

    # 5. Creación válida de Sala
    s1 = sistema.registrar_servicio(ReservaSala, "SR-01", "Sala Innovación", 80000, capacidad=20)
    # 6. Creación válida de Equipo
    s2 = sistema.registrar_servicio(AlquilerEquipo, "EQ-01", "Portátil Workstation", 35000, stock=5)
    # 7. Creación válida de Asesoría (no disponible para probar error)
    s3 = sistema.registrar_servicio(
        AsesoriaEspecializada, "AS-01", "Arquitectura Cloud", 150000, especialidad="AWS", disponible=False
    )
    # 8. Creación INVÁLIDA de Servicio (tarifa negativa)
    sistema.registrar_servicio(ReservaSala, "SR-02", "Sala Error", -50000, capacidad=10)

    # 9. Reserva EXITOSA de Sala (con sobrecarga de descuento 10%)
    sistema.ejecutar_reserva("RES-01", c1, s1, duracion=4, impuesto=0.19, descuento=0.10)
    # 10. Reserva EXITOSA de Equipo (con parámetros por defecto)
    sistema.ejecutar_reserva("RES-02", c2, s2, duracion=5)
    # 11. Reserva FALLIDA por servicio no disponible
    sistema.ejecutar_reserva("RES-03", c1, s3, duracion=3)
    # 12. Reserva FALLIDA por cálculo inconsistente (descuento >= 100%, encadenamiento)
    sistema.ejecutar_reserva("RES-04", c2, s1, duracion=2, impuesto=0.19, descuento=1.5)
    # 13. Reserva CANCELADA correctamente
    sistema.ejecutar_reserva("RES-05", c1, s2, duracion=3, cancelar=True)

    print("\n=== SISTEMA FINALIZADO DE FORMA ESTABLE (Revisar 'software_fj.log') ===")
    logging.info("Fin de simulaciones. El sistema mantuvo estabilidad total.")


if __name__ == "__main__":
    ejecutar_simulaciones()