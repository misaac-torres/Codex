import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Projects from "./pages/Projects";
import Team from "./pages/Team";
import Suggestions from "./pages/Suggestions";

const Link = ({ to, label }: { to: string; label: string }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `px-3 py-2 rounded-lg text-sm ${isActive ? "bg-black text-white" : "text-slate-700 hover:bg-slate-100"}`
    }
  >
    {label}
  </NavLink>
);

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-10 border-b bg-white">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div className="font-semibold">GD · Gestión de Dependencias TI</div>
          <nav className="flex gap-2">
            <Link to="/" label="Dashboard" />
            <Link to="/projects" label="Proyectos" />
            <Link to="/teams" label="Células" />
            <Link to="/suggestions" label="Sugerencias" />
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/teams" element={<Team />} />
          <Route path="/suggestions" element={<Suggestions />} />
        </Routes>
      </main>
    </div>
  );
}
