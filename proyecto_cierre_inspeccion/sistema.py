import shutil
import json
from datetime import datetime
from clases import OrdenInspeccion, Empleado, Sismografo, Estado, MotivoFueraServicio, MotivoTipo


class SistemaInspeccion:
    def __init__(self, path_ordenes, path_sismografos, path_empleados):
        self.path_ordenes = path_ordenes
        self.path_sismografos = path_sismografos
        self.path_empleados = path_empleados

        shutil.copyfile("data/ordenes_default.json", self.path_ordenes)
        shutil.copyfile("data/sismografos_default.json", self.path_sismografos)

        self.ordenes = self._cargar_ordenes()
        self.sismografos = self._cargar_sismografos()
        self.empleados = self._cargar_empleados()

    def _cargar_ordenes(self):
        with open(self.path_ordenes, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return [OrdenInspeccion(
            id=o["id"],
            fechaHoraGeneracion=datetime.fromisoformat(o["fechaHoraGeneracion"]),
            fechaHoraFinalizacion=datetime.fromisoformat(o["fechaHoraFinalizacion"]),
            fechaHoraCierre=datetime.fromisoformat(o["fechaHoraCierre"]) if o["fechaHoraCierre"] else None,
            estado=o["estado"],
            observacionCierre=o["observacionCierre"],
            esCerrada=o["esCerrada"],
            sismografoAsignado=o["sismografoAsignado"],
            responsableInspeccion=o["responsableInspeccion"],
            nombreEstacion=o["nombreEstacion"]
        ) for o in datos]

    def _guardar_ordenes(self):
        with open(self.path_ordenes, 'w', encoding='utf-8') as f:
            json.dump([self._orden_a_dict(o) for o in self.ordenes], f, indent=2, default=str)

    def _orden_a_dict(self, orden):
        return {
            "id": orden.id,
            "fechaHoraGeneracion": orden.fechaHoraGeneracion.isoformat(),
            "fechaHoraFinalizacion": orden.fechaHoraFinalizacion.isoformat(),
            "fechaHoraCierre": orden.fechaHoraCierre.isoformat() if orden.fechaHoraCierre else None,
            "estado": orden.estado,
            "observacionCierre": orden.observacionCierre,
            "esCerrada": orden.esCerrada,
            "sismografoAsignado": orden.sismografoAsignado,
            "responsableInspeccion": orden.responsableInspeccion,
            "nombreEstacion": orden.nombreEstacion
        }

    def _cargar_sismografos(self):
        with open(self.path_sismografos, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return {s["nroSerie"]: Sismografo(
            nroSerie=s["nroSerie"],
            estadoActual=Estado(s["estadoActual"]),
            motivosFueraServicio=[
                MotivoFueraServicio(
                    comentario=m["comentario"],
                    motivoTipo=MotivoTipo(m["motivoTipo"])
                ) for m in s["motivosFueraServicio"]
            ]
        ) for s in datos}

    def _guardar_sismografos(self):
        with open(self.path_sismografos, 'w', encoding='utf-8') as f:
            json.dump([self._sismografo_a_dict(s) for s in self.sismografos.values()], f, indent=2)

    def _sismografo_a_dict(self, sismografo):
        return {
            "nroSerie": sismografo.nroSerie,
            "estadoActual": sismografo.estadoActual.nombre,
            "motivosFueraServicio": [
                {
                    "comentario": m.comentario,
                    "motivoTipo": m.motivoTipo.descripcion
                } for m in sismografo.motivosFueraServicio
            ]
        }

    def _cargar_empleados(self):
        with open(self.path_empleados, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return {e["email"]: Empleado(e["email"], e["rol"]) for e in datos}

    def get_ordenes_finalizadas(self):
        return [o for o in self.ordenes if not o.esCerrada and o.estado == "realizada"]

    def get_orden_por_id(self, orden_id):
        return next((o for o in self.ordenes if o.id == orden_id), None)

    def get_sismografo(self, nro_serie):
        return self.sismografos.get(nro_serie)

    def cerrar_orden(self, orden_id, observacion, motivos_fuera_servicio):
        orden = self.get_orden_por_id(orden_id)
        if not orden:
            raise ValueError("Orden no encontrada")

        if orden.esCerrada:
            raise ValueError("La orden ya está cerrada")

        orden.cerrarOrden(observacion)

        sismografo = self.get_sismografo(orden.sismografoAsignado)
        if motivos_fuera_servicio:
            motivos = [
                MotivoFueraServicio(comentario=m["comentario"], motivoTipo=MotivoTipo(m["motivoTipo"]))
                for m in motivos_fuera_servicio
            ]
            sismografo.ponerFueraDeServicio(motivos)

        self._guardar_ordenes()
        self._guardar_sismografos()
