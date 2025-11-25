const apiBase = '';

function setStatus(statusEl, text, state) {
  statusEl.textContent = text;
  statusEl.className = `status status--${state}`;
}

function parseDependencies(raw) {
  if (!raw.trim()) return [];
  return raw
    .split(/\n|;/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [equipo = '', codigo = '', descripcion = ''] = line.split('|');
      return { equipo: equipo.trim(), codigo: codigo.trim().toUpperCase(), descripcion: descripcion.trim() };
    })
    .filter((d) => d.equipo && (d.codigo === 'P' || d.codigo === 'L'));
}

function renderJson(el, data) {
  el.textContent = JSON.stringify(data, null, 2);
}

async function fetchJson(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function renderCatalogs(catalogs) {
  const grid = document.getElementById('catalog-grid');
  grid.innerHTML = '';
  const entries = Object.entries(catalogs.dependency_mapping || {});
  if (!entries.length) {
    grid.innerHTML = '<p class="muted">No hay dependencias cargadas desde la hoja Datos.</p>';
    return;
  }
  entries.forEach(([equipo, desc]) => {
    const tile = document.createElement('div');
    tile.className = 'tile';
    tile.innerHTML = `<p class="label">Dependencia</p><h3>${equipo}</h3><p class="muted">${desc || 'Sin descripción'}</p>`;
    grid.appendChild(tile);
  });
}

function renderProject(data) {
  const el = document.getElementById('project-result');
  if (!data.found) {
    el.innerHTML = `<p class="muted">${data.msg || 'Proyecto no encontrado.'}</p>`;
    return;
  }
  const deps = (data.detalles || [])
    .map((d) => `<li><strong>${d.equipo}</strong>: ${d.FLAG} — ${d.descripcion || 'Sin detalle'}</li>`) 
    .join('');
  el.innerHTML = `
    <div class="chips">
      <span class="chip">Fila ${data.fila}</span>
      <span class="chip">Q ${data.Q_RADICADO ?? 'N/D'}</span>
      <span class="chip">Avance ${data.avance}%</span>
      <span class="chip">Estimado ${data.estimado}%</span>
    </div>
    <p class="muted">Dependencias (${data.total_dep}):</p>
    <ul>${deps}</ul>
  `;
}

function renderMetrics(data) {
  const el = document.getElementById('metrics-result');
  if (!data || !data.metrics) {
    el.innerHTML = '<p class="muted">Sin métricas disponibles.</p>';
    return;
  }
  const list = data.metrics
    .map((row) => {
      const name = row.nombre ?? row.scope ?? 'Total';
      return `<div class="tile"><h3>${name}</h3><p class="muted">Cubrimiento: ${(row.cubrimiento || 0).toFixed(2)}% · Pendientes: ${row.pendientes ?? 0}</p></div>`;
    })
    .join('');
  el.innerHTML = `<div class="grid">${list}</div>`;
}

function attachHandlers() {
  const healthBtn = document.getElementById('btn-health');
  const healthStatus = document.querySelector('#health-panel .status');
  const healthJson = document.getElementById('health-json');

  healthBtn.addEventListener('click', async () => {
    setStatus(healthStatus, 'Verificando...', 'idle');
    healthJson.textContent = '';
    try {
      const data = await fetchJson(`${apiBase}/health`);
      setStatus(healthStatus, 'Backend OK', 'ok');
      renderJson(healthJson, data);
    } catch (err) {
      setStatus(healthStatus, 'Error al consultar', 'error');
      healthJson.textContent = err.message;
    }
  });

  document.getElementById('btn-load-catalogs').addEventListener('click', async () => {
    const jsonBox = document.getElementById('catalog-json');
    jsonBox.textContent = 'Cargando...';
    try {
      const data = await fetchJson(`${apiBase}/catalogs`);
      renderJson(jsonBox, data);
      renderCatalogs(data);
    } catch (err) {
      jsonBox.textContent = err.message;
    }
  });

  document.getElementById('btn-fetch-project').addEventListener('click', async () => {
    const name = document.getElementById('project-name').value.trim();
    if (!name) return;
    const result = document.getElementById('project-result');
    result.innerHTML = '<p class="muted">Buscando…</p>';
    try {
      const data = await fetchJson(`${apiBase}/projects/${encodeURIComponent(name)}`);
      renderProject(data);
    } catch (err) {
      result.innerHTML = `<p class="muted">${err.message}</p>`;
    }
  });

  document.getElementById('update-form').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const row = document.getElementById('update-row').value;
    const avance = document.getElementById('update-avance').value;
    const estimado = document.getElementById('update-estimado').value;
    const deps = parseDependencies(document.getElementById('update-deps').value);
    const body = {
      avance: avance ? Number(avance) : null,
      estimado: estimado ? Number(estimado) : null,
      dependencias: deps,
    };
    const target = document.getElementById('update-response');
    target.textContent = 'Actualizando…';
    try {
      const data = await fetchJson(`${apiBase}/projects/${row}`, { method: 'PATCH', body: JSON.stringify(body) });
      renderJson(target, data);
    } catch (err) {
      target.textContent = err.message;
    }
  });

  document.getElementById('create-form').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const body = {
      nombre: document.getElementById('create-nombre').value.trim(),
      responsable: document.getElementById('create-responsable').value || null,
      estado: document.getElementById('create-estado').value || null,
      q_radicado: document.getElementById('create-q').value || null,
      dependencias: parseDependencies(document.getElementById('create-deps').value),
    };
    const target = document.getElementById('create-response');
    target.textContent = 'Enviando…';
    try {
      const data = await fetchJson(`${apiBase}/projects`, { method: 'POST', body: JSON.stringify(body) });
      renderJson(target, data);
    } catch (err) {
      target.textContent = err.message;
    }
  });

  document.getElementById('btn-metrics').addEventListener('click', async () => {
    const scope = document.getElementById('metrics-scope').value;
    const filter = document.getElementById('metrics-filter').value.trim();
    const target = document.getElementById('metrics-result');
    target.innerHTML = '<p class="muted">Calculando…</p>';
    const url = new URL(`${apiBase}/metrics`, window.location.origin);
    url.searchParams.set('scope', scope);
    if (filter) url.searchParams.set('filter_value', filter);
    try {
      const data = await fetchJson(url.toString());
      renderMetrics(data);
    } catch (err) {
      target.innerHTML = `<p class="muted">${err.message}</p>`;
    }
  });

  document.getElementById('suggest-form').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const body = {
      usuario: document.getElementById('suggest-usuario').value,
      texto: document.getElementById('suggest-texto').value,
    };
    const target = document.getElementById('suggest-result');
    target.innerHTML = '<p class="muted">Enviando…</p>';
    try {
      await fetchJson(`${apiBase}/suggestions`, { method: 'POST', body: JSON.stringify(body) });
      target.innerHTML = '<p class="muted">Sugerencia guardada correctamente.</p>';
    } catch (err) {
      target.innerHTML = `<p class="muted">${err.message}</p>`;
    }
  });

  // cargas iniciales
  healthBtn.click();
  document.getElementById('btn-load-catalogs').click();
  document.getElementById('btn-metrics').click();
}

document.addEventListener('DOMContentLoaded', attachHandlers);
