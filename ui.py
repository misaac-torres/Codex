# ui.py — GD Front (Streamlit)
import os
import requests
import pandas as pd
import streamlit as st

API_BASE = os.getenv("GD_API_BASE", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="GD · Dependencias", layout="wide")

# ----------------------------
# Helpers
# ----------------------------
def api_get(path: str, params=None):
    r = requests.get(f"{API_BASE}{path}", params=params, timeout=30)
    if not r.ok:
        raise RuntimeError(f"GET {path} -> {r.status_code}: {r.text}")
    return r.json()


def api_post(path: str, payload: dict):
    r = requests.post(f"{API_BASE}{path}", json=payload, timeout=60)
    if not r.ok:
        raise RuntimeError(f"POST {path} -> {r.status_code}: {r.text}")
    return r.json()


def api_put(path: str, payload: dict):
    r = requests.put(f"{API_BASE}{path}", json=payload, timeout=60)
    if not r.ok:
        raise RuntimeError(f"PUT {path} -> {r.status_code}: {r.text}")
    return r.json()


def pct(x):
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return "—"


# ----------------------------
# Header
# ----------------------------
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("## GD · Dependencias")
with col2:
    st.caption(f"API: {API_BASE}")

# ----------------------------
# Bootstrap catalogs + health
# ----------------------------
with st.spinner("Cargando configuración..."):
    health = api_get("/health")
    catalogs = api_get("/catalogs")

st.info(health.get("paths", ""))

area_tren_coe = catalogs.get("area_tren_coe", [])
celulas_dep = catalogs.get("celulas_dep", [])
estados = catalogs.get("estados", [])
responsables = catalogs.get("responsables", [])
iniciativas = catalogs.get("iniciativas", [])

# ----------------------------
# Sidebar filters (metrics)
# ----------------------------
st.sidebar.header("Filtros de métricas")
scope = st.sidebar.selectbox("Scope", ["all", "area", "celula"], index=0)

filter_value = None
if scope == "area":
    filter_value = st.sidebar.selectbox("Área/Tren/CoE", area_tren_coe if area_tren_coe else ["(vacío)"])
elif scope == "celula":
    filter_value = st.sidebar.selectbox("Célula", celulas_dep if celulas_dep else ["(vacío)"])

# ----------------------------
# Dashboard metrics
# ----------------------------
with st.spinner("Cargando métricas..."):
    metrics = api_get("/metrics", params={"scope": scope, "filter_value": filter_value})

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Proyectos", metrics.get("total_projects", 0))
m2.metric("Dependencias", int(metrics.get("total_dep", 0)))
m3.metric("Pendientes (P)", int(metrics.get("total_P", 0)))
m4.metric("Negociadas (L)", int(metrics.get("total_L", 0)))
m5.metric("Cobertura P/Total", pct(metrics.get("cobertura_pct", 0)))

st.divider()

# ----------------------------
# Project Explorer
# ----------------------------
st.markdown("### Explorador de Proyectos")

left, right = st.columns([2, 3], gap="large")

with left:
    q = st.text_input("Buscar proyecto (contiene)", "")
    with st.spinner("Cargando lista..."):
        proj_list = api_get("/projects", params={"q": q if q else None}).get("items", [])

    if not proj_list:
        st.warning("No hay proyectos (o tu búsqueda quedó vacía).")
        st.stop()

    selected = st.selectbox("Selecciona proyecto", proj_list)

    st.markdown("#### Acciones")
    usuario = st.text_input("Tu usuario (para sugerencias)", "")
    sug = st.text_area("Sugerencia / mejora", height=90, placeholder="Escribe aquí…")
    if st.button("Enviar sugerencia", use_container_width=True):
        api_post("/suggestions", {"usuario": usuario, "texto": sug})
        st.success("Sugerencia enviada.")

    with st.expander("Últimas sugerencias", expanded=False):
        try:
            last = api_get("/suggestions", params={"limit": 5})
            st.dataframe(pd.DataFrame(last), use_container_width=True, hide_index=True)
        except Exception as e:
            st.caption(f"No disponible: {e}")

with right:
    with st.spinner("Cargando detalle del proyecto..."):
        detail = api_get(f"/projects/{selected}")

    if not detail.get("found", True):
        st.error(detail.get("msg", "No encontrado"))
        st.stop()

    top = st.columns(6)
    top[0].metric("Fila", detail.get("fila"))
    top[1].metric("Q", detail.get("Q_RADICADO", "—"))
    top[2].metric("Dep (calc)", detail.get("total_dep", 0))
    top[3].metric("P", detail.get("pendientes", 0))
    top[4].metric("L", detail.get("negociadas", 0))
    top[5].metric("% Pendientes", pct(detail.get("pct_pendientes", 0)))

    st.caption("Nota: también se muestran totales/coverage que vienen del Excel (campos agregados).")

    xl = st.columns(4)
    xl[0].metric("Dep (Excel)", detail.get("total_dep_xl", 0))
    xl[1].metric("L (Excel)", detail.get("total_L_xl", 0))
    xl[2].metric("P (Excel)", detail.get("total_P_xl", 0))
    xl[3].metric("Cubrimiento (Excel)", pct(float(detail.get("cub_xl", 0)) * 100))

    st.markdown("#### Dependencias")
    detalles = detail.get("detalles", [])
    df = pd.DataFrame(detalles) if detalles else pd.DataFrame(columns=["equipo", "FLAG", "descripcion"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Editor rápido (avance/estimado + dependencias)")
    fila = detail.get("fila")
    av = st.number_input("Avance (0..1)", min_value=0.0, max_value=1.0, value=float(detail.get("avance", 0.0) or 0.0), step=0.01)
    est = st.number_input(
        "Estimado (0..1)",
        min_value=0.0,
        max_value=1.0,
        value=float(detail.get("estimado", 0.0) or 0.0),
        step=0.01,
    )

    # Data editor para dependencias
    if df.empty:
        df = pd.DataFrame([{"equipo": "", "FLAG": "P", "descripcion": ""}])

    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "equipo": st.column_config.SelectboxColumn("equipo", options=celulas_dep),
            "FLAG": st.column_config.SelectboxColumn("FLAG", options=["P", "L"]),
            "descripcion": st.column_config.TextColumn("descripcion"),
        },
        key="deps_editor",
    )

    if st.button("Guardar cambios en Excel", type="primary", use_container_width=True):
        payload = {
            "avance": av,
            "estimado": est,
            "dependencias": [
                {
                    "equipo": str(r.get("equipo", "")).strip(),
                    "codigo": str(r.get("FLAG", "")).strip(),
                    "descripcion": str(r.get("descripcion", "") or ""),
                }
                for _, r in edited.iterrows()
                if str(r.get("equipo", "")).strip()
            ],
        }
        res = api_put(f"/projects/{int(fila)}", payload)
        st.success(
            f"Guardado. %Cumpl: {res.get('pct_cumpl', 0):.2f}% | Var vs LB (pp): {res.get('var_vs_lb_pp', 0):.2f}"
        )

st.divider()

# ----------------------------
# Team / Célula view
# ----------------------------
st.markdown("### Vista por célula (resumen de dependencias)")
team = st.selectbox("Célula", celulas_dep if celulas_dep else ["(vacío)"], index=0)
if st.button("Ver resumen de célula", use_container_width=True):
    data = api_get(f"/teams/{team}")
    if not data.get("found", True):
        st.error(data.get("msg", "No encontrado"))
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", data.get("total", 0))
        c2.metric("Pendientes (P)", data.get("pendientes", 0))
        c3.metric("Negociadas (L)", data.get("negociadas", 0))
        c4.metric("% Pendientes", pct(data.get("pct_pendientes", 0)))
        st.dataframe(pd.DataFrame(data.get("rows", [])), use_container_width=True, hide_index=True)
