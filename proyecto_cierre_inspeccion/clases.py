from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Estado:
    nombre: str


@dataclass
class MotivoTipo:
    descripcion: str

    def getDescripcion(self):
        return self.descripcion


@dataclass
class MotivoFueraServicio:
    comentario: str
    motivoTipo: MotivoTipo


@dataclass
class Empleado:
    email: str
    rol: str

    def esResponsableDeInspeccion(self):
        return self.rol == "RI"


@dataclass
class Sismografo:
    nroSerie: str
    estadoActual: Estado
    motivosFueraServicio: List[MotivoFueraServicio] = field(default_factory=list)

    def ponerFueraDeServicio(self, nuevos_motivos: List[MotivoFueraServicio]):
        self.estadoActual = Estado("fuera de servicio")
        self.motivosFueraServicio.extend(nuevos_motivos)

    def setEstadoActual(self, nuevo_estado: str):
        self.estadoActual = Estado(nuevo_estado)


@dataclass
class OrdenInspeccion:
    id: int
    fechaHoraGeneracion: datetime
    fechaHoraFinalizacion: datetime
    fechaHoraCierre: Optional[datetime]
    estado: str
    observacionCierre: Optional[str]
    esCerrada: bool
    sismografoAsignado: str
    responsableInspeccion: str
    nombreEstacion: str

    def cerrarOrden(self, observacion: str):
        self.fechaHoraCierre = datetime.now()
        self.observacionCierre = observacion
        self.esCerrada = True
        self.estado = "cerrada"
