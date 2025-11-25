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
            "title": "Alta de proyectos",
            "body": "Registrar iniciativas con dependencias P/L por célula, tren o CoE en un único POST.",
            "endpoint": "/projects",
        },
        {
            "title": "Consulta y edición",
            "body": "Consultar el estado consolidado y actualizar avances o estimados por fila del Excel.",
            "endpoint": "/projects/{row}",
        },
        {
            "title": "Métricas",
            "body": "KPIs agregados por catálogo activo, con cobertura L/P y avance promedio.",
            "endpoint": "/metrics",
        },
        {
            "title": "Sugerencias",
            "body": "Captura feedback para la hoja `Sugerencias` desde cualquier integración.",
            "endpoint": "/suggestions",
        },
    ]

    legacy_tabs = [
        {"title": "Consulta / edición", "copy": "Cobertura de dependencias y actualización de avance."},
        {"title": "Métricas", "copy": "Visión agregada por Tren y Célula, con gráfico L/P."},
        {"title": "Mesa Expertos", "copy": "Priorización de proyectos por contribución y dependencias."},
        {"title": "Mesa PO Sync", "copy": "Evaluación ágil con rating 1–5 para proyectos priorizados."},
        {"title": "Feedback", "copy": "Panel conectado a la hoja Sugerencias para mejoras y bugs."},
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

    tabs_html = "".join(
        f"""
        <div class='tab'>
            <div class='tab-title'>{tab['title']}</div>
            <div class='tab-copy'>{tab['copy']}</div>
        </div>
        """
        for tab in legacy_tabs
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

    html = """
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
            header {{ background: {gradient}; color: #f8fafc; padding: 64px 24px 88px; }}
            .content {{ max-width: 1180px; margin: 0 auto; }}
            h1 {{ font-size: 40px; margin: 0 0 12px; letter-spacing: -0.5px; }}
            p.lead {{ font-size: 18px; max-width: 780px; line-height: 1.6; margin: 0 0 24px; color: #e2e8f0; }}
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
            .tabs {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 10px; }}
            .tab {{ border: 1px dashed #cbd5e1; border-radius: 14px; padding: 12px 14px; background: #f8fafc; }}
            .tab-title {{ font-weight: 700; color: var(--navy); margin-bottom: 6px; }}
            .tab-copy {{ color: #334155; line-height: 1.4; }}
            .chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
            .chip {{ background: rgba(11,30,61,0.08); color: #0b1e3d; padding: 8px 10px; border-radius: 12px; font-weight: 600; font-size: 13px; border: 1px solid rgba(0,169,224,0.35); }}
            footer {{ text-align: center; padding: 24px; color: #475569; font-size: 14px; }}
            .form-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; margin-top: 14px; }}
            .form-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; box-shadow: 0 12px 30px rgba(9,20,66,0.05); }}
            .form-card h3 {{ margin-top: 0; color: var(--navy); margin-bottom: 10px; }}
            .form-card label {{ display: block; font-weight: 600; margin: 10px 0 6px; color: #0f172a; }}
            .form-card input, .form-card textarea, .form-card select {{ width: 100%; padding: 10px; border-radius: 10px; border: 1px solid #cbd5e1; font-size: 14px; font-family: inherit; background: #fff; }}
            .form-card textarea {{ min-height: 80px; resize: vertical; }}
            .form-card button {{ margin-top: 12px; background: var(--primary); color: white; border: none; padding: 10px 12px; border-radius: 10px; font-weight: 700; cursor: pointer; width: 100%; box-shadow: 0 8px 20px rgba(0,169,224,0.25); }}
            .form-card button:hover {{ background: #008bc0; }}
            .result {{ background: #0b1e3d; color: #e0f2fe; border-radius: 12px; padding: 10px 12px; font-family: "JetBrains Mono", "SFMono-Regular", ui-monospace, monospace; font-size: 13px; margin-top: 12px; white-space: pre-wrap; max-height: 220px; overflow: auto; }}
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
                <h1>Codex · GD_v1 — Gestión de Dependencias TI</h1>
                <p class='lead'>Hereda la experiencia del notebook GDv1 con un front listo para operar: registra dependencias P/L por célula, consulta métricas y prioriza proyectos desde Swagger UI o cualquier cliente HTTP.</p>
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
            <h2>Flujo funcional heredado</h2>
            <p>Los capítulos del notebook original viven como endpoints que puedes consumir desde tu UI o scripts de automatización.</p>
            <div class='tabs'>
                {tabs_html}
            </div>
            <div class='chips'>
                <div class='chip'>Alta de proyectos</div>
                <div class='chip'>Consulta / edición</div>
                <div class='chip'>Métricas agregadas</div>
                <div class='chip'>Mesa de Expertos</div>
                <div class='chip'>Mesa PO Sync</div>
                <div class='chip'>Feedback y sugerencias</div>
            </div>
        </section>

        <section class='section content'>
            <h2>Panel interactivo (modo local)</h2>
            <p>Opera la API como en el front legado: prueba altas, consultas y métricas sin salir de la landing. Los formularios llaman al backend que corre en este mismo puerto (8000 por defecto).</p>
            <div class='form-grid'>
                <div class='form-card'>
                    <h3>Alta de proyecto</h3>
                    <form id='create-project-form'>
                        <label for='proj-nombre'>Nombre</label>
                        <input id='proj-nombre' name='nombre' placeholder='Nombre del proyecto' required />
                        <label for='proj-responsable'>Responsable</label>
                        <input id='proj-responsable' name='responsable' placeholder='Responsable (opcional)' />
                        <label for='proj-avance'>Avance</label>
                        <input id='proj-avance' name='avance' type='number' step='0.1' placeholder='Ej: 25' />
                        <label for='proj-deps'>Dependencias (JSON)</label>
                        <textarea id='proj-deps' name='dependencias' placeholder='Ejemplo: [{"equipo": "Célula A", "codigo": "P"}]'></textarea>
                        <button type='submit'>Registrar proyecto</button>
                    </form>
                    <pre class='result' id='create-project-result'>Esperando envío…</pre>
                </div>

                <div class='form-card'>
                    <h3>Consulta / edición</h3>
                    <form id='get-project-form'>
                        <label for='get-nombre'>Nombre del proyecto</label>
                        <input id='get-nombre' name='nombre' placeholder='Coincide con la columna Proyecto TI' required />
                        <button type='submit'>Consultar</button>
                    </form>
                    <form id='update-project-form'>
                        <label for='update-row'>Fila Excel</label>
                        <input id='update-row' name='row' type='number' min='2' placeholder='Número de fila en ProyectosTI' required />
                        <label for='update-avance'>Avance (%)</label>
                        <input id='update-avance' name='avance' type='number' step='0.1' placeholder='Ej: 50' />
                        <label for='update-estimado'>Estimado (%)</label>
                        <input id='update-estimado' name='estimado' type='number' step='0.1' placeholder='Nuevo estimado' />
                        <label for='update-deps'>Dependencias (JSON)</label>
                        <textarea id='update-deps' name='dependencias' placeholder='Opcional: [{"equipo": "Célula B", "codigo": "L"}]'></textarea>
                        <button type='submit'>Actualizar fila</button>
                    </form>
                    <pre class='result' id='project-result'>Esperando consulta…</pre>
                </div>

                <div class='form-card'>
                    <h3>Métricas rápidas</h3>
                    <form id='metrics-form'>
                        <label for='metrics-scope'>Scope</label>
                        <select id='metrics-scope' name='scope'>
                            <option value='all'>all</option>
                            <option value='tren'>tren</option>
                            <option value='celula'>celula</option>
                        </select>
                        <label for='metrics-filter'>Filtro (opcional)</label>
                        <input id='metrics-filter' name='filter_value' placeholder='Nombre de tren o célula' />
                        <button type='submit'>Obtener métricas</button>
                    </form>
                    <pre class='result' id='metrics-result'>Esperando consulta…</pre>
                </div>

                <div class='form-card'>
                    <h3>Sugerencias</h3>
                    <form id='suggestion-form'>
                        <label for='sug-usuario'>Usuario</label>
                        <input id='sug-usuario' name='usuario' placeholder='Opcional' />
                        <label for='sug-texto'>Mensaje</label>
                        <textarea id='sug-texto' name='texto' required placeholder='Comparte tu feedback como en la hoja Sugerencias'></textarea>
                        <button type='submit'>Enviar sugerencia</button>
                    </form>
                    <pre class='result' id='suggestion-result'>Esperando envío…</pre>
                </div>
            </div>
        </section>

        <section class='section content'>
            <h2>Despliegue en un clic</h2>
            <p>Ejecuta <code>./deploy_test_env.sh</code> para preparar dependencias, levantar el servidor y abrir Swagger UI. Si sólo necesitas el front de usuario, <code>./deploy_user_front.sh</code> sirve la landing y la documentación con branding Telefónica.</p>
            <p>Para mantener compatibilidad con el Excel corporativo puedes exportar las mismas hojas (<code>ProyectosTI</code>, <code>Datos</code>, <code>Sugerencias</code>) y apuntar la variable de entorno <code>GD_EXCEL_PATH</code> al archivo vigente.</p>
            <div class='stats'>
                {stats_html}
            </div>
        </section>

        <footer>
            Inspirado en el legado de GDv1, optimizado para experiencias rápidas y profesionales.
        </footer>

        <script>
            async function submitJson(event, buildPayload, endpoint, method = 'POST', resultId = '') {
                event.preventDefault();
                const resultEl = document.getElementById(resultId);
                try {
                    const payload = buildPayload();
                    const response = await fetch(endpoint, {
                        method,
                        headers: { 'Content-Type': 'application/json' },
                        body: method === 'GET' ? undefined : JSON.stringify(payload),
                    });
                    const data = await response.json();
                    resultEl.textContent = JSON.stringify(data, null, 2);
                } catch (err) {
                    resultEl.textContent = 'Error: ' + err;
                }
            }

            document.getElementById('create-project-form').addEventListener('submit', (event) => submitJson(
                event,
                () => {
                    let dependencias = [];
                    const rawDeps = document.getElementById('proj-deps').value.trim();
                    if (rawDeps) {
                        dependencias = JSON.parse(rawDeps);
                    }
                    return {
                        nombre: document.getElementById('proj-nombre').value,
                        responsable: document.getElementById('proj-responsable').value || null,
                        avance: document.getElementById('proj-avance').value || null,
                        dependencias,
                    };
                },
                '/projects',
                'POST',
                'create-project-result'
            ));

            document.getElementById('get-project-form').addEventListener('submit', async (event) => {
                event.preventDefault();
                const nombre = document.getElementById('get-nombre').value;
                const resultEl = document.getElementById('project-result');
                try {
                    const resp = await fetch(`/projects/${encodeURIComponent(nombre)}`);
                    const data = await resp.json();
                    resultEl.textContent = JSON.stringify(data, null, 2);
                } catch (err) {
                    resultEl.textContent = 'Error: ' + err;
                }
            });

            document.getElementById('update-project-form').addEventListener('submit', (event) => submitJson(
                event,
                () => {
                    let dependencias = [];
                    const rawDeps = document.getElementById('update-deps').value.trim();
                    if (rawDeps) { dependencias = JSON.parse(rawDeps); }
                    return {
                        avance: document.getElementById('update-avance').value || null,
                        estimado: document.getElementById('update-estimado').value || null,
                        dependencias,
                    };
                },
                `/projects/${document.getElementById('update-row').value}`,
                'PATCH',
                'project-result'
            ));

            document.getElementById('metrics-form').addEventListener('submit', async (event) => {
                event.preventDefault();
                const scope = document.getElementById('metrics-scope').value;
                const filter = document.getElementById('metrics-filter').value;
                const params = new URLSearchParams({ scope });
                if (filter) params.append('filter_value', filter);
                const resultEl = document.getElementById('metrics-result');
                try {
                    const resp = await fetch(`/metrics?${params.toString()}`);
                    const data = await resp.json();
                    resultEl.textContent = JSON.stringify(data, null, 2);
                } catch (err) {
                    resultEl.textContent = 'Error: ' + err;
                }
            });

            document.getElementById('suggestion-form').addEventListener('submit', (event) => submitJson(
                event,
                () => ({
                    usuario: document.getElementById('sug-usuario').value,
                    texto: document.getElementById('sug-texto').value,
                }),
                '/suggestions',
                'POST',
                'suggestion-result'
            ));
        </script>
    </body>
    </html>
    """

    replacements = {
        "primary": primary,
        "navy": navy,
        "gradient": gradient,
        "cards_html": cards_html,
        "tabs_html": tabs_html,
        "stats_html": stats_html,
    }

    for key, value in replacements.items():
        html = html.replace(f"{{{key}}}", value)

    return html

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


@app.get("/projects")
def list_projects(q: Optional[str] = None):
    names = projects.get_all_project_names()
    if q:
        qn = q.strip().lower()
        names = [n for n in names if qn in n.lower()]
    return {"count": len(names), "items": names}


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


@app.get("/teams/{equipo}")
def get_team_summary(equipo: str):
    dep_mapping = _require_dep_mapping()
    return projects.summarize_by_equipo(equipo, dep_mapping)


@app.get("/suggestions")
def list_suggestions(limit: int = 5):
    return suggestions.get_last_suggestions(limit=limit)
