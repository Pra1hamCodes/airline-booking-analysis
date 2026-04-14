import { Link, NavLink, Outlet, useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { LayoutDashboard, Route, TrendingUp, Bell, FileText, LogOut, Plane } from "lucide-react";
import { useAuth } from "@/stores/auth";

const nav = [
  { to: "/app", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/app/routes", label: "Routes", icon: Route },
  { to: "/app/forecast", label: "Forecast", icon: TrendingUp },
  { to: "/app/alerts", label: "Alerts", icon: Bell },
  { to: "/app/reports", label: "Reports", icon: FileText },
];

const titles: Record<string, string> = {
  "/app": "Dashboard",
  "/app/routes": "Routes",
  "/app/forecast": "Forecast",
  "/app/alerts": "Alerts",
  "/app/reports": "Reports",
};

export function Layout() {
  const nav2 = useNavigate();
  const loc = useLocation();
  const logout = useAuth((s) => s.logout);
  const user = useAuth((s) => s.user);
  const pageTitle = titles[loc.pathname] || "Market Intelligence";

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 glass border-r border-white/5 p-5 flex flex-col sticky top-0 h-screen">
        <Link to="/" className="flex items-center gap-2 text-xl font-display font-bold mb-10 hoverable group">
          <motion.div whileHover={{ rotate: 20 }} className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary to-accent grid place-items-center">
            <Plane size={18} className="text-white" />
          </motion.div>
          <span className="gradient-text">AirDemand</span>
        </Link>
        <nav className="flex flex-col gap-1 flex-1">
          {nav.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.end}
              className={({ isActive }) =>
                `relative flex items-center gap-3 px-3 py-2.5 rounded-xl transition group hoverable ${isActive ? "text-white" : "text-white/60 hover:text-white hover:bg-white/5"}`
              }>
              {({ isActive }) => (
                <>
                  {isActive && (
                    <motion.div layoutId="nav-pill" transition={{ type: "spring", stiffness: 400, damping: 32 }}
                      className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary/25 to-accent/15 border border-primary/30 -z-0" />
                  )}
                  <n.icon size={18} className={`relative z-10 ${isActive ? "text-accent" : ""}`} />
                  <span className="relative z-10 text-sm font-medium">{n.label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="text-xs text-white/40 mb-2 px-2 truncate">{user?.email}</div>
          <button onClick={() => { logout(); nav2("/"); }}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-white/70 hover:text-danger hover:bg-danger/10 transition hoverable text-sm">
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 p-8 relative">
        <div className="flex justify-between items-center mb-8">
          <motion.h1 key={pageTitle} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
            className="font-display text-3xl font-bold">
            <span className="gradient-text">{pageTitle}</span>
          </motion.h1>
          <div className="flex items-center gap-3">
            <motion.div animate={{ opacity: [0.4, 1, 0.4] }} transition={{ repeat: Infinity, duration: 2 }}
              className="h-2 w-2 rounded-full bg-success" />
            <span className="text-xs text-white/50">Live data</span>
          </div>
        </div>
        <motion.div key={loc.pathname}
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -14 }}
          transition={{ duration: 0.35, ease: "easeOut" }}>
          <Outlet />
        </motion.div>
      </main>
    </div>
  );
}
