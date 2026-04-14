import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Area, ComposedChart } from "recharts";
import { TrendingUp } from "lucide-react";

export function ForecastPage() {
  const [route, setRoute] = useState("Sydney-Melbourne");
  const { data: routesResp } = useQuery({
    queryKey: ["all-routes-forecast"],
    queryFn: async () => (await api.get("/api/v1/routes/?per_page=100&sort_by=demand_score")).data,
  });
  const allRoutes: string[] = (routesResp?.routes || []).map((r: any) => `${r.origin}-${r.destination}`);
  const { data } = useQuery({
    queryKey: ["forecast", route],
    queryFn: async () => (await api.get(`/api/v1/prices/forecast?route=${encodeURIComponent(route)}`)).data,
    enabled: !!route,
  });

  const forecast = data?.forecast || [];
  const nextPrice = forecast[0]?.predicted_price;
  const endPrice = forecast.at(-1)?.predicted_price;
  const delta = nextPrice && endPrice ? (((endPrice - nextPrice) / nextPrice) * 100).toFixed(1) : null;

  return (
    <div className="space-y-4">
      <div className="grid md:grid-cols-3 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
          <div className="text-white/50 text-xs uppercase tracking-wider">Selected Route</div>
          <div className="font-display text-xl mt-2">{route.replace("-", " → ")}</div>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }} className="card">
          <div className="text-white/50 text-xs uppercase tracking-wider">Tomorrow's Price</div>
          <div className="font-display text-3xl mt-2 gradient-text">${nextPrice?.toFixed(0) || "—"}</div>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.16 }} className="card">
          <div className="text-white/50 text-xs uppercase tracking-wider">14-day Change</div>
          <div className={`font-display text-3xl mt-2 flex items-center gap-2 ${delta && +delta >= 0 ? "text-success" : "text-danger"}`}>
            <TrendingUp size={22} /> {delta ? `${delta}%` : "—"}
          </div>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
        <div className="flex justify-between items-center mb-5">
          <div>
            <h3 className="font-display text-lg">14-Day Price Forecast</h3>
            <p className="text-white/40 text-xs mt-0.5">95% confidence band · ARIMA(1,1,1) / polynomial fallback</p>
          </div>
          <select value={route} onChange={(e) => setRoute(e.target.value)} className="input hoverable">
            {allRoutes.length === 0 && <option>Sydney-Melbourne</option>}
            {allRoutes.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <ResponsiveContainer width="100%" height={420}>
          <ComposedChart data={forecast}>
            <defs>
              <linearGradient id="band" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2D7EF7" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#2D7EF7" stopOpacity={0.02} />
              </linearGradient>
              <linearGradient id="pred-line" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#22D3EE" />
                <stop offset="100%" stopColor="#D946EF" />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#1f2937" vertical={false} />
            <XAxis dataKey="date" stroke="#888" fontSize={11} />
            <YAxis stroke="#888" fontSize={11} />
            <Tooltip contentStyle={{ background: "#0A0F1E", border: "1px solid #374151", borderRadius: 12 }} />
            <Area type="monotone" dataKey="upper_bound" stroke="none" fill="url(#band)" />
            <Area type="monotone" dataKey="lower_bound" stroke="none" fill="#0A0F1E" fillOpacity={1} />
            <Line type="monotone" dataKey="predicted_price" stroke="url(#pred-line)" strokeWidth={3} dot={{ r: 3, fill: "#22D3EE" }} />
          </ComposedChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );
}
