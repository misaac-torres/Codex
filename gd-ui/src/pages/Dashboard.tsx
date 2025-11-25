import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

function Card({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white p-4 shadow-sm border">
      <div className="text-xs text-slate-500">{title}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const [catalogs, setCatalogs] = useState<any>(null);
  const [scope, setScope] = useState<"all" | "area" | "celula">("all");
  const [filter, setFilter] = useState<string>("");
  const [metricsData, setMetricsData] = useState<any>(null);
  const [err, setErr] = useState<string>("");

  useEffect(() => {
    api.catalogs().then(setCatalogs).catch((e) => setErr(String(e)));
  }, []);

  useEffect(() => {
    api
      .metrics(scope, scope === "all" ? undefined : filter || undefined)
      .then(setMetricsData)
      .catch((e) => setErr(String(e)));
  }, [scope, filter]);

  const filterOptions = useMemo(() => {
    if (!catalogs) return [] as string[];
    if (scope === "area") return catalogs.area_tren_coe ?? [];
    if (scope === "celula") return catalogs.celulas_dep ?? [];
    return [] as string[];
  }, [catalogs, scope]);

  if (err) return <div className="rounded-xl border bg-white p-4 text-red-600">Error: {err}</div>;
  if (!metricsData) return <div className="text-slate-600">Cargando…</div>;

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <div className="text-xs text-slate-500">Scope</div>
            <select
              className="mt-1 rounded-xl border px-3 py-2"
              value={scope}
              onChange={(e) => {
                setScope(e.target.value as any);
                setFilter("");
              }}
            >
              <option value="all">Todo</option>
              <option value="area">Área/Tren/CoE</option>
              <option value="celula">Célula</option>
            </select>
          </div>

          {scope !== "all" && (
            <div>
              <div className="text-xs text-slate-500">Filtro</div>
              <select
                className="mt-1 rounded-xl border px-3 py-2"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                <option value="">Selecciona…</option>
                {filterOptions.map((x: string) => (
                  <option key={x} value={x}>
                    {x}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="ml-auto text-sm text-slate-500">
            Cobertura P/Total: <span className="font-semibold text-slate-900">{metricsData.cobertura_pct?.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Card title="Proyectos" value={`${metricsData.total_projects ?? 0}`} />
        <Card title="Dependencias" value={`${Math.round(metricsData.total_dep ?? 0)}`} />
        <Card title="Pendientes (P)" value={`${Math.round(metricsData.total_P ?? 0)}`} />
        <Card title="Negociadas (L)" value={`${Math.round(metricsData.total_L ?? 0)}`} />
        <Card title="Avance promedio" value={`${((metricsData.avg_avance ?? 0) * 100).toFixed(0)}%`} />
      </div>
    </div>
  );
}
