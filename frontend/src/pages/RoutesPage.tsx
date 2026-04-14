import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { ArrowUpRight, ArrowDownRight, Minus, Plane } from "lucide-react";

export function RoutesPage() {
  const { data } = useQuery({
    queryKey: ["routes"], queryFn: async () => (await api.get("/api/v1/routes/?per_page=50")).data,
  });
  const routes = data?.routes || [];

  const trendIcon = (t: string) => {
    if (t === "rising" || t === "up") return <ArrowUpRight size={14} className="text-success" />;
    if (t === "falling" || t === "down") return <ArrowDownRight size={14} className="text-danger" />;
    return <Minus size={14} className="text-white/40" />;
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="font-display text-xl">All Routes</h3>
          <p className="text-white/40 text-xs mt-1">{routes.length} routes tracked</p>
        </div>
        <div className="glass rounded-full px-3 py-1.5 text-xs flex items-center gap-2">
          <Plane size={12} className="text-accent" /> Australia network
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-white/40 text-left text-xs uppercase tracking-wider">
            <tr>
              <th className="py-3 font-medium">Route</th>
              <th className="font-medium">Distance</th>
              <th className="font-medium">Avg 7d</th>
              <th className="font-medium">Avg 30d</th>
              <th className="font-medium">Demand</th>
              <th className="font-medium">Trend</th>
            </tr>
          </thead>
          <tbody>
            {routes.map((r: any, i: number) => (
              <motion.tr key={r.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: Math.min(i * 0.015, 0.3) }}
                whileHover={{ backgroundColor: "rgba(45,126,247,0.06)" }}
                className="border-t border-white/5 hoverable">
                <td className="py-3 font-medium">
                  <span className="text-white/90">{r.origin}</span>
                  <span className="text-white/30 mx-2">→</span>
                  <span className="text-white/90">{r.destination}</span>
                </td>
                <td className="text-white/60">{r.distance_km} km</td>
                <td className="font-medium">${r.avg_price_7d?.toFixed(0) || "—"}</td>
                <td className="text-white/70">${r.avg_price_30d?.toFixed(0) || "—"}</td>
                <td>
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-16 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-primary to-accent"
                        style={{ width: `${Math.min((r.avg_demand_7d || 0) * 100, 100)}%` }} />
                    </div>
                    <span className="text-xs text-white/50">{r.avg_demand_7d?.toFixed(2) || "—"}</span>
                  </div>
                </td>
                <td>
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs glass ${
                    r.demand_trend === "rising" ? "text-success" :
                    r.demand_trend === "falling" ? "text-danger" : "text-white/50"
                  }`}>
                    {trendIcon(r.demand_trend)} {r.demand_trend}
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
