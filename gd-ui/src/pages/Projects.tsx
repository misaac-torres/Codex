import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

type DepRow = { equipo: string; FLAG: "P" | "L"; descripcion: string };

export default function Projects() {
  const [catalogs, setCatalogs] = useState<any>(null);
  const [q, setQ] = useState("");
  const [list, setList] = useState<string[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [detail, setDetail] = useState<any>(null);
  const [deps, setDeps] = useState<DepRow[]>([]);
  const [avance, setAvance] = useState<number>(0);
  const [estimado, setEstimado] = useState<number>(0);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.catalogs().then(setCatalogs).catch((e) => setErr(String(e)));
  }, []);

  useEffect(() => {
    api
      .listProjects(q || undefined)
      .then((r) => {
        setList(r.items ?? []);
        if (!selected && r.items?.length) setSelected(r.items[0]);
      })
      .catch((e) => setErr(String(e)));
  }, [q]);

  useEffect(() => {
    if (!selected) return;
    setBusy(true);
    api
      .getProject(selected)
      .then((d) => {
        setDetail(d);
        setDeps(d.detalles ?? []);
        setAvance(d.avance ?? 0);
        setEstimado(d.estimado ?? 0);
      })
      .catch((e) => setErr(String(e)))
      .finally(() => setBusy(false));
  }, [selected]);

  const celulas = useMemo(() => catalogs?.celulas_dep ?? [], [catalogs]);

  async function save() {
    if (!detail?.fila) return;
    setBusy(true);
    try {
      await api.updateProjectRow(detail.fila, {
        avance,
        estimado,
        dependencias: deps.map((d) => ({ equipo: d.equipo, codigo: d.FLAG, descripcion: d.descripcion })),
      });
      const d2 = await api.getProject(selected);
      setDetail(d2);
      setDeps(d2.detalles ?? []);
    } catch (e: any) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  if (err) return <div className="rounded-xl border bg-white p-4 text-red-600">Error: {err}</div>;
  if (!catalogs) return <div className="text-slate-600">Cargando…</div>;

  return (
    <div className="grid gap-4 lg:grid-cols-[340px_1fr]">
      <aside className="rounded-2xl border bg-white p-4 shadow-sm">
        <div className="text-sm font-semibold">Proyectos</div>
        <input
          className="mt-2 w-full rounded-xl border px-3 py-2"
          placeholder="Buscar…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <div className="mt-3 max-h-[60vh] overflow-auto space-y-1">
          {list.map((name) => (
            <button
              key={name}
              className={`w-full text-left px-3 py-2 rounded-xl text-sm ${
                name === selected ? "bg-slate-900 text-white" : "hover:bg-slate-100"
              }`}
              onClick={() => setSelected(name)}
            >
              {name}
            </button>
          ))}
        </div>
      </aside>

      <section className="rounded-2xl border bg-white p-4 shadow-sm">
        {!detail ? (
          <div className="text-slate-600">Selecciona un proyecto…</div>
        ) : (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-xs text-slate-500">Proyecto</div>
                <div className="text-xl font-semibold">{detail.proyecto}</div>
                <div className="text-sm text-slate-500">Fila: {detail.fila} · Q: {detail.Q_RADICADO ?? "—"}</div>
              </div>
              <div className="flex gap-2">
                <button
                  className="rounded-xl px-4 py-2 border hover:bg-slate-50"
                  onClick={() =>
                    api.getProject(selected).then((d) => {
                      setDetail(d);
                      setDeps(d.detalles ?? []);
                    })
                  }
                  disabled={busy}
                >
                  Refrescar
                </button>
                <button
                  className="rounded-xl px-4 py-2 bg-black text-white hover:opacity-90"
                  onClick={save}
                  disabled={busy}
                >
                  Guardar
                </button>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-xl border p-3">
                <div className="text-xs text-slate-500">Avance (0..1)</div>
                <input
                  className="mt-1 w-full rounded-lg border px-3 py-2"
                  type="number"
                  step="0.01"
                  min={0}
                  max={1}
                  value={avance}
                  onChange={(e) => setAvance(Number(e.target.value))}
                />
              </div>
              <div className="rounded-xl border p-3">
                <div className="text-xs text-slate-500">Estimado (0..1)</div>
                <input
                  className="mt-1 w-full rounded-lg border px-3 py-2"
                  type="number"
                  step="0.01"
                  min={0}
                  max={1}
                  value={estimado}
                  onChange={(e) => setEstimado(Number(e.target.value))}
                />
              </div>
              <div className="rounded-xl border p-3">
                <div className="text-xs text-slate-500">Pendientes</div>
                <div className="mt-1 text-2xl font-semibold">
                  {detail.pendientes ?? 0} / {detail.total_dep ?? 0}
                </div>
                <div className="text-sm text-slate-500">{(detail.pct_pendientes ?? 0).toFixed(1)}%</div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <div className="text-sm font-semibold">Dependencias (P/L)</div>
                <button
                  className="text-sm rounded-xl border px-3 py-2 hover:bg-slate-50"
                  onClick={() => setDeps((d) => [...d, { equipo: celulas[0] ?? "", FLAG: "P", descripcion: "" }])}
                >
                  + Agregar
                </button>
              </div>

              <div className="mt-2 overflow-auto rounded-xl border">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr className="text-left">
                      <th className="p-3 w-[240px]">Equipo</th>
                      <th className="p-3 w-[90px]">Flag</th>
                      <th className="p-3">Descripción</th>
                      <th className="p-3 w-[70px]"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {deps.map((r, idx) => (
                      <tr key={idx} className="border-t">
                        <td className="p-2">
                          <select
                            className="w-full rounded-lg border px-2 py-2"
                            value={r.equipo}
                            onChange={(e) =>
                              setDeps((d) => d.map((x, i) => (i === idx ? { ...x, equipo: e.target.value } : x)))
                            }
                          >
                            <option value="">Selecciona…</option>
                            {celulas.map((c: string) => (
                              <option key={c} value={c}>
                                {c}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="p-2">
                          <select
                            className="w-full rounded-lg border px-2 py-2"
                            value={r.FLAG}
                            onChange={(e) =>
                              setDeps((d) => d.map((x, i) => (i === idx ? { ...x, FLAG: e.target.value as any } : x)))
                            }
                          >
                            <option value="P">P</option>
                            <option value="L">L</option>
                          </select>
                        </td>
                        <td className="p-2">
                          <input
                            className="w-full rounded-lg border px-3 py-2"
                            value={r.descripcion}
                            onChange={(e) =>
                              setDeps((d) => d.map((x, i) => (i === idx ? { ...x, descripcion: e.target.value } : x)))
                            }
                          />
                        </td>
                        <td className="p-2">
                          <button
                            className="rounded-lg px-2 py-2 hover:bg-slate-100"
                            onClick={() => setDeps((d) => d.filter((_, i) => i !== idx))}
                            title="Eliminar"
                          >
                            ✕
                          </button>
                        </td>
                      </tr>
                    ))}
                    {!deps.length && (
                      <tr>
                        <td className="p-4 text-slate-500" colSpan={4}>
                          Sin dependencias registradas.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              <div className="mt-2 text-xs text-slate-500">
                Tip UX: si esto lo usará operación, el valor está en ver rápido “bloqueos P” y resolverlos, no en leer endpoints.
              </div>
            </div>

            {busy && <div className="text-slate-500">Procesando…</div>}
          </div>
        )}
      </section>
    </div>
  );
}
