const API_BASE = (import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000").replace(/\/$/, "");

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return (await res.json()) as T;
}

export const api = {
  health: () => req<{ status: string; paths: string }>("/health"),
  catalogs: () => req<any>("/catalogs"),
  metrics: (scope: string, filter_value?: string) => {
    const u = new URL(`${API_BASE}/metrics`);
    u.searchParams.set("scope", scope);
    if (filter_value) u.searchParams.set("filter_value", filter_value);
    return req<any>(u.pathname + "?" + u.searchParams.toString());
  },
  listProjects: (q?: string) => {
    const u = new URL(`${API_BASE}/projects`);
    if (q) u.searchParams.set("q", q);
    return req<{ count: number; items: string[] }>(u.pathname + (u.searchParams.toString() ? `?${u.searchParams}` : ""));
  },
  getProject: (nombre: string) => req<any>(`/projects/${encodeURIComponent(nombre)}`),
  updateProjectRow: (row: number, payload: any) => req<any>(`/projects/${row}`, { method: "PUT", body: JSON.stringify(payload) }),
  team: (equipo: string) => req<any>(`/teams/${encodeURIComponent(equipo)}`),
  sendSuggestion: (payload: { usuario: string; texto: string }) => req(`/suggestions`, { method: "POST", body: JSON.stringify(payload) }),
  listSuggestions: (limit = 5) => req<any>(`/suggestions?limit=${limit}`),
};
