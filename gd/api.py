"""FastAPI surface for the GD backend logic."""
from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import catalogs, config, metrics, projects, suggestions
from .models import Dependency, Project, Catalogs


class DependencyPayload(BaseModel):
    equipo: str = Field(..., description="Nombre de la célula / tren / CoE")
    codigo: str = Field(..., regex="^[PL]$", description="Flag P/L")
    descripcion: str = ""

    def to_model(self) -> Dependency:
        return Dependency(
            equipo=self.equipo,
            codigo=self.codigo,
            descripcion=self.descripcion,
        )


class ProjectPayload(BaseModel):
    nombre: str
    estado: Optional[str] = None
    q_radicado: Optional[str] = None
    priorizado: Optional[str] = None
    responsable: Optional[str] = None
    area_solicitante: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_estimada_cierre: Optional[str] = None
    linea_base: Optional[float] = None
    linea_base_q_gestion: Optional[float] = None
    avance: Optional[float] = None
    estimado_avance: Optional[float] = None
    contribucion: Optional[float] = None
    iniciativa: Optional[str] = None
    dependencias: List[DependencyPayload] = Field(default_factory=list)

    def to_model(self) -> Project:
        return Project(
            nombre=self.nombre,
            estado=self.estado,
            q_radicado=self.q_radicado,
            priorizado=self.priorizado,
            responsable=self.responsable,
            area_solicitante=self.area_solicitante,
            fecha_inicio=self.fecha_inicio,
            fecha_estimada_cierre=self.fecha_estimada_cierre,
            linea_base=self.linea_base,
            linea_base_q_gestion=self.linea_base_q_gestion,
            avance=self.avance,
            estimado_avance=self.estimado_avance,
            contribucion=self.contribucion,
            iniciativa=self.iniciativa,
        )

    def dependency_models(self) -> List[Dependency]:
        return [d.to_model() for d in self.dependencias]


class UpdatePayload(BaseModel):
    avance: Optional[float] = None
    estimado: Optional[float] = Field(None, description="Nuevo estimado de avance")
    dependencias: List[DependencyPayload] = Field(default_factory=list)

    def dependency_models(self) -> List[Dependency]:
        return [d.to_model() for d in self.dependencias]


class SuggestionPayload(BaseModel):
    usuario: str = ""
    texto: str


app = FastAPI(title="GD Excel API", version="1.0.0")

try:
    _catalogs = catalogs.load_catalogs()
except Exception as exc:  # pragma: no cover - defensive bootstrap
    print("⚠️ No se pudieron cargar catálogos al iniciar la API:", exc)
    _catalogs = Catalogs()


def _require_dep_mapping():
    if not _catalogs.dependency_mapping:
        raise HTTPException(status_code=500, detail="No dependency mapping loaded from 'Datos'.")
    return _catalogs.dependency_mapping


@app.get("/health")
def health():
    return {"status": "ok", "paths": config.describe_active_paths()}


@app.get("/catalogs")
def get_catalogs():
    return _catalogs.__dict__


@app.post("/projects")
def create_project(payload: ProjectPayload):
    dep_mapping = _require_dep_mapping()
    dep_models = payload.dependency_models()
    row, proj_id = projects.write_project_with_dependencies(payload.to_model(), dep_models, dep_mapping)
    return {"row": row, "id": proj_id}


@app.get("/projects/{nombre}")
def get_project(nombre: str):
    dep_mapping = _require_dep_mapping()
    return projects.summarize_by_proyecto(nombre, dep_mapping)


@app.patch("/projects/{row}")
@app.put("/projects/{row}")
def update_project(row: int, payload: UpdatePayload):
    dep_mapping = _require_dep_mapping()
    dep_models = payload.dependency_models()
    return projects.update_project_row_and_dependencies(row, payload.avance, payload.estimado, dep_models, dep_mapping)


@app.get("/metrics")
def get_metrics(scope: str = "all", filter_value: Optional[str] = None):
    return metrics.compute_metrics(
        scope=scope,
        filter_value=filter_value,
        dep_mapping=_catalogs.dependency_mapping,
        celula_tren_map=_catalogs.celula_tren_map,
    )


@app.post("/suggestions")
def send_suggestion(payload: SuggestionPayload):
    suggestions.append_suggestion(payload.usuario, payload.texto)
    return {"status": "ok"}
