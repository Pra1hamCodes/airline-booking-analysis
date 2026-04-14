import { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { Landing } from "./pages/Landing";
import { AuthPage } from "./pages/AuthPage";
import { Dashboard } from "./pages/Dashboard";
import { RoutesPage } from "./pages/RoutesPage";
import { ForecastPage } from "./pages/ForecastPage";
import { AlertsPage } from "./pages/AlertsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { Layout } from "./components/Layout";
import { CursorGlow } from "./components/CursorGlow";
import { MorphBackground } from "./components/MorphBackground";
import { FlyingPlanes } from "./components/FlyingPlanes";
import { useAuth } from "./stores/auth";

function Protected({ children }: { children: JSX.Element }) {
  const user = useAuth((s) => s.user);
  const token = localStorage.getItem("access_token");
  if (!token && !user) return <Navigate to="/auth" replace />;
  return children;
}

export default function App() {
  const fetchMe = useAuth((s) => s.fetchMe);
  useEffect(() => { if (localStorage.getItem("access_token")) fetchMe(); }, [fetchMe]);

  return (
    <>
      <MorphBackground />
      <FlyingPlanes count={7} />
      <CursorGlow />
      <AnimatePresence mode="wait">
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route element={<Protected><Layout /></Protected>}>
          <Route path="/app" element={<Dashboard />} />
          <Route path="/app/routes" element={<RoutesPage />} />
          <Route path="/app/forecast" element={<ForecastPage />} />
          <Route path="/app/alerts" element={<AlertsPage />} />
          <Route path="/app/reports" element={<ReportsPage />} />
        </Route>
      </Routes>
      </AnimatePresence>
    </>
  );
}
