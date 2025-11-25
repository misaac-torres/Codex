"""FastAPI surface for the GD backend logic."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import catalogs, config, metrics, projects, suggestions
from .models import Catalogs, Dependency, Project


class DependencyPayload(BaseModel):
    equipo: str = Field(..., description="Nombre de la célula / tren / CoE")
    codigo: str = Field(..., pattern="^[PL]$", description="Flag P/L")
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


STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="GD Excel API", version="1.0.0", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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


@app.get("/docs", include_in_schema=False)
def custom_docs() -> HTMLResponse:
    hero_html = """
    <header class="gd-hero">
      <div class="gd-hero__badge">GDv1 heritage</div>
      <h1>Gestión de Demanda Experience</h1>
      <p>
        Explora y prueba la API que trae la esencia de la interfaz GDv1 a un flujo moderno.
        Lanza entornos de prueba, captura métricas y conecta dependencias desde un solo lugar.
      </p>
      <div class="gd-hero__actions">
        <a class="gd-btn" href="#swagger-ui">Ir al catálogo de endpoints</a>
        <a class="gd-link" href="/health">Verificar estado inmediato</a>
      </div>
    </header>
    """

    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>GD Experience | Telefónica</title>
        <link rel="stylesheet" type="text/css" href="/static/swagger-custom.css">
        <link rel="icon" type="image/svg+xml" href="/static/telefonica-favicon.svg" />
    </head>
    <body>
        {hero_html}
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
        <script>
        const ui = SwaggerUIBundle({{
            url: '{app.openapi_url}',
            dom_id: '#swagger-ui',
            layout: 'StandaloneLayout',
            docExpansion: 'list',
            defaultModelsExpandDepth: -1,
            displayRequestDuration: true,
            persistAuthorization: true,
            deepLinking: true,
            filter: true,
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
        }});
        window.ui = ui;
        </script>
    </body>
    </html>"""

    return HTMLResponse(html)


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
