import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Team() {
  const [catalogs, setCatalogs] = useState<any>(null);
  const [team, setTeam] = useState("");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api
      .catalogs()
      .then((c) => {
        setCatalogs(c);
        setTeam(c.celulas_dep?.[0] ?? "");
      })
      .catch((e) => setErr(String(e)));
  }, []);

  async function load() {
    try {
      setData(await api.team(team));
    } catch (e: any) {
      setErr(String(e));
    }
  }

  if (err) return <div className="rounded-xl border bg-white p-4 text-red-600">Error: {err}</div>;
  if (!catalogs) return <div className="text-slate-600">Cargando…</div>;

  return (
    <div className="space-y-3">
      <div className="rounded-2xl border bg-white p-4 shadow-sm flex flex-wrap items-end gap-3">
        <div>
          <div className="text-xs text-slate-500">Célula</div>
          <select className="mt-1 rounded-xl border px-3 py-2" value={team} onChange={(e) => setTeam(e.target.value)}>
            {catalogs.celulas_dep.map((c: string) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
        <button className="rounded-xl px-4 py-2 bg-black text-white" onClick={load}>
          Cargar
        </button>
      </div>

      {data && data.found && (
        <div className="rounded-2xl border bg-white p-4 shadow-sm">
          <div className="flex flex-wrap justify-between gap-2">
            <div className="font-semibold">{data.equipo}</div>
            <div className="text-sm text-slate-600">
              Total: <b>{data.total}</b> · P: <b>{data.pendientes}</b> · L: <b>{data.negociadas}</b>
            </div>
          </div>

          <div className="mt-3 overflow-auto rounded-xl border">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left">
                <tr>
                  <th className="p-3 w-[90px]">Fila</th>
                  <th className="p-3 w-[120px]">Q</th>
                  <th className="p-3">Proyecto</th>
                  <th className="p-3 w-[90px]">Flag</th>
                </tr>
              </thead>
              <tbody>
                {(data.rows ?? []).map((r: any) => (
                  <tr key={r.fila} className="border-t">
                    <td className="p-3">{r.fila}</td>
                    <td className="p-3">{r.Q_RADICADO}</td>
                    <td className="p-3">{r.PROYECTO}</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-1 rounded-lg text-xs ${
                          r.FLAG === "P" ? "bg-red-100 text-red-800" : "bg-emerald-100 text-emerald-800"
                        }`}
                      >
                        {r.FLAG}
                      </span>
                    </td>
                  </tr>
                ))}
                {!data.rows?.length && (
                  <tr>
                    <td className="p-4 text-slate-500" colSpan={4}>
                      Sin registros.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
