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
# Serve the Telefónica-themed Swagger assets (CSS + SVG favicon) alongside the API.
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


@app.get("/", response_class=HTMLResponse)
def landing_page():
    primary = "#00a9e0"  # Telefónica blue
    navy = "#0b1e3d"
    gradient = "linear-gradient(135deg, #0b1e3d 0%, #032d60 40%, #00a9e0 100%)"

    highlight_cards = [
        {
            "title": "Carga de proyectos",
            "body": "Envía un proyecto con dependencias en un solo POST y obtén el ID generado",
            "endpoint": "/projects",
        },
        {
            "title": "Resumen ejecutivo",
            "body": "Consulta el estado consolidado de un proyecto y sus dependencias con una sola llamada",
            "endpoint": "/projects/{nombre}",
        },
        {
            "title": "Seguimiento continuo",
            "body": "Actualiza avance y estimados directamente sobre la fila del Excel",
            "endpoint": "/projects/{row}",
        },
        {
            "title": "Métricas",
            "body": "Obtén KPIs agregados por célula, tren o CoE basados en los catálogos activos",
            "endpoint": "/metrics",
        },
    ]

    stats = {
        "dependencias": len(_catalogs.dependency_mapping),
        "celulas": len(_catalogs.celula_tren_map),
        "catalogos": len(_catalogs.__dict__),
    }

    cards_html = "".join(
        f"""
        <div class='card'>
            <p class='eyebrow'>Endpoint</p>
            <h3>{card['title']}</h3>
            <p>{card['body']}</p>
            <div class='endpoint'>{card['endpoint']}</div>
        </div>
        """
        for card in highlight_cards
    )

    stats_html = "".join(
        f"""
        <div class='stat'>
            <div class='stat-value'>{value}</div>
            <div class='stat-label'>{label}</div>
        </div>
        """
        for label, value in stats.items()
    )

    return f"""
    <!DOCTYPE html>
    <html lang='es'>
    <head>
        <meta charset='UTF-8' />
        <meta name='viewport' content='width=device-width, initial-scale=1.0' />
        <title>GD API · Front de usuario</title>
        <style>
            :root {{
                --primary: {primary};
                --navy: {navy};
            }}
            * {{ box-sizing: border-box; font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif; }}
            body {{ margin: 0; color: #0f172a; background: #f5f7fb; }}
            header {{ background: {gradient}; color: #f8fafc; padding: 64px 24px 80px; }}
            .content {{ max-width: 1100px; margin: 0 auto; }}
            h1 {{ font-size: 40px; margin: 0 0 12px; letter-spacing: -0.5px; }}
            p.lead {{ font-size: 18px; max-width: 720px; line-height: 1.6; margin: 0 0 24px; color: #e2e8f0; }}
            .pill {{ display: inline-block; padding: 10px 14px; border-radius: 12px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); color: #e2e8f0; margin-bottom: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 12px; }}
            .actions {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}
            .button {{ display: inline-flex; gap: 8px; align-items: center; background: #ffffff; color: var(--navy); padding: 12px 16px; border-radius: 12px; border: none; font-weight: 700; text-decoration: none; box-shadow: 0 20px 40px rgba(0,0,0,0.12); transition: transform 150ms ease, box-shadow 150ms ease; }}
            .button.secondary {{ background: rgba(255,255,255,0.16); color: #f8fafc; border: 1px solid rgba(255,255,255,0.35); box-shadow: none; }}
            .button:hover {{ transform: translateY(-2px); box-shadow: 0 16px 32px rgba(0,0,0,0.18); }}
            .grid {{ display: grid; gap: 18px; margin-top: -52px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); padding: 0 24px 60px; }}
            .card {{ background: #ffffff; border-radius: 16px; padding: 20px; box-shadow: 0 12px 30px rgba(9,20,66,0.08); border: 1px solid #e2e8f0; }}
            .card h3 {{ margin: 8px 0 8px; color: var(--navy); }}
            .card p {{ margin: 0 0 12px; line-height: 1.5; color: #334155; }}
            .eyebrow {{ text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700; font-size: 12px; color: var(--primary); margin: 0; }}
            .endpoint {{ background: #0b1e3d; color: #e0f2fe; padding: 10px 12px; border-radius: 10px; font-family: "JetBrains Mono", "SFMono-Regular", ui-monospace, monospace; font-size: 13px; letter-spacing: -0.2px; display: inline-block; }}
            .section {{ background: #ffffff; margin: 0 24px 32px; padding: 22px 20px; border-radius: 16px; box-shadow: 0 12px 30px rgba(9,20,66,0.05); border: 1px solid #e2e8f0; }}
            .section h2 {{ margin: 0 0 14px; color: var(--navy); }}
            .section p {{ margin: 0 0 10px; color: #334155; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-top: 12px; }}
            .stat {{ background: linear-gradient(145deg, rgba(0,169,224,0.1), rgba(11,30,61,0.08)); border: 1px solid rgba(0,169,224,0.25); border-radius: 12px; padding: 14px 16px; }}
            .stat-value {{ font-weight: 800; font-size: 24px; color: var(--navy); }}
            .stat-label {{ color: #0f172a; opacity: 0.7; text-transform: capitalize; }}
            footer {{ text-align: center; padding: 24px; color: #475569; font-size: 14px; }}
            @media (max-width: 720px) {{
                header {{ padding: 48px 20px 70px; }}
                h1 {{ font-size: 32px; }}
                .grid {{ margin-top: -44px; }}
                .actions {{ flex-direction: column; align-items: flex-start; }}
            }}
        </style>
    </head>
    <body>
        <header>
            <div class='content'>
                <div class='pill'>Front de usuario · Telefónica</div>
                <h1>Gestiona el flujo GD con un solo clic</h1>
                <p class='lead'>Lanza el backend heredado de GDv1, consume catálogos y actualiza proyectos directamente desde Swagger UI. Todo con el estilo corporativo y una experiencia limpia para equipos ágiles.</p>
                <div class='actions'>
                    <a class='button' href='/docs'>Ir a Swagger UI</a>
                    <a class='button secondary' href='/health'>Ver estado inmediato</a>
                </div>
            </div>
        </header>

        <section class='grid'>
            {cards_html}
        </section>

        <section class='section content'>
            <h2>Despliegue en un clic</h2>
            <p>Ejecuta <code>./deploy_test_env.sh</code> para preparar dependencias, levantar el servidor y abrir Swagger UI. La página de inicio permanece disponible en <code>/</code> para guiar a cualquier usuario.</p>
            <div class='stats'>
                {stats_html}
            </div>
        </section>

        <footer>
            Inspirado en el legado de GDv1, optimizado para experiencias rápidas y profesionales.
        </footer>
    </body>
    </html>
    """

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
