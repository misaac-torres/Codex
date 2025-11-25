"""Data models shared across the backend modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Dependency:
    equipo: str
    codigo: str
    descripcion: str = ""


@dataclass
class Project:
    nombre: str
    estado: Optional[str] = None
    q_radicado: Optional[str] = None
    priorizado: Optional[str] = None
    responsable: Optional[str] = None
    area_solicitante: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_estimada_cierre: Optional[str] = None
    linea_base: float | None = None
    linea_base_q_gestion: float | None = None
    avance: float | None = None
    estimado_avance: float | None = None
    contribucion: float | None = None
    iniciativa: Optional[str] = None

    def to_row_mapping(self):
        return {
            "NOMBRE_PROYECTO": self.nombre,
            "ESTADO_PROYECTO": self.estado,
            "Q_RADICADO": self.q_radicado,
            "PRIORIZADO": self.priorizado,
            "RESPONSABLE_PROYECTO": self.responsable,
            "AREA_SOLICITANTE": self.area_solicitante,
            "FECHA_INICIO": self.fecha_inicio,
            "FECHA_ESTIMADA_CIERRE": self.fecha_estimada_cierre,
            "LINEA_BASE": self.linea_base,
            "LINEA_BASE_Q_GESTION": self.linea_base_q_gestion,
            "AVANCE": self.avance,
            "ESTIMADO_AVANCE": self.estimado_avance,
            "CONTRIBUCION": self.contribucion,
            "INICIATIVA_ESTRATEGICA": self.iniciativa,
        }


@dataclass
class Catalogs:
    estados: List[str] = field(default_factory=list)
    q_rad: List[str] = field(default_factory=list)
    responsables: List[str] = field(default_factory=list)
    areas: List[str] = field(default_factory=list)
    area_tren_coe: List[str] = field(default_factory=list)
    celulas_dep: List[str] = field(default_factory=list)
    iniciativas: List[str] = field(default_factory=list)
    dependency_mapping: dict = field(default_factory=dict)
    celula_tren_map: dict = field(default_factory=dict)
