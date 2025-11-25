import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Suggestions() {
  const [usuario, setUsuario] = useState("");
  const [texto, setTexto] = useState("");
  const [list, setList] = useState<any[]>([]);
  const [err, setErr] = useState("");

  async function refresh() {
    try {
      setList(await api.listSuggestions(10));
    } catch (e: any) {
      setErr(String(e));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function send() {
    try {
      await api.sendSuggestion({ usuario, texto });
      setTexto("");
      await refresh();
    } catch (e: any) {
      setErr(String(e));
    }
  }

  if (err) return <div className="rounded-xl border bg-white p-4 text-red-600">Error: {err}</div>;

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
      <div className="rounded-2xl border bg-white p-4 shadow-sm space-y-3">
        <div className="text-sm font-semibold">Nueva sugerencia</div>
        <input
          className="w-full rounded-xl border px-3 py-2"
          placeholder="Usuario"
          value={usuario}
          onChange={(e) => setUsuario(e.target.value)}
        />
        <textarea
          className="w-full rounded-xl border px-3 py-2 min-h-[140px]"
          placeholder="¿Qué mejorarías del flujo?"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
        />
        <button className="rounded-xl px-4 py-2 bg-black text-white" onClick={send} disabled={!texto.trim()}>
          Enviar
        </button>
      </div>

      <div className="rounded-2xl border bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="text-sm font-semibold">Últimas sugerencias</div>
          <button className="rounded-xl border px-3 py-2 hover:bg-slate-50" onClick={refresh}>
            Refrescar
          </button>
        </div>
        <div className="mt-3 space-y-2">
          {list.map((s, i) => (
            <div key={i} className="rounded-xl border p-3">
              <div className="text-xs text-slate-500">{s.usuario || "—"}</div>
              <div className="mt-1 text-sm">{s.texto}</div>
            </div>
          ))}
          {!list.length && <div className="text-slate-500">Aún no hay sugerencias.</div>}
        </div>
      </div>
    </div>
  );
}
