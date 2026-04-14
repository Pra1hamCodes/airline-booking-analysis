import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from "recharts";
import { Plane, Wallet, Flame, Route as RouteIcon } from "lucide-react";
import { Tilt } from "@/components/Tilt";

function KPI({ label, value, delay = 0, Icon, accent }: { label: string; value: string | number; delay?: number; Icon: any; accent: string }) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
      <Tilt className="card card-hover hoverable overflow-hidden relative">
        <div className="absolute -top-6 -right-6 h-24 w-24 rounded-full blur-2xl opacity-40" style={{ background: accent }} />
        <div className="flex items-start justify-between relative z-10">
          <div>
            <div className="text-white/50 text-xs uppercase tracking-wider">{label}</div>
            <div className="text-3xl font-display font-bold mt-2 gradient-text">{value}</div>
          </div>
          <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 grid place-items-center">
            <Icon size={18} className="text-accent" />
          </div>
        </div>
      </Tilt>
    </motion.div>
  );
}

export function Dashboard() {
  const { data: summary } = useQuery({
    queryKey: ["insights"], queryFn: async () => (await api.get("/api/v1/insights/summary")).data,
  });
  const insights = summary?.insights || summary;
  const { data: trendsData } = useQuery({
    queryKey: ["trends"], queryFn: async () => (await api.get("/api/v1/prices/trends")).data,
  });
  const trendRows = (() => {
    const rows = trendsData?.trends || [];
    const byDate: Record<string, { date: string; sum: number; n: number }> = {};
    for (const r of rows) {
      if (!r.date) continue;
      if (!byDate[r.date]) byDate[r.date] = { date: r.date, sum: 0, n: 0 };
      byDate[r.date].sum += r.price; byDate[r.date].n += 1;
    }
    return Object.values(byDate).sort((a, b) => a.date.localeCompare(b.date))
      .map((r) => ({ date: r.date.slice(5), avg_price: Math.round(r.sum / r.n) }));
  })();

  const routesData = (insights?.popular_routes || []).slice(0, 8).map((r: any) => ({
    name: `${r.origin.slice(0,3)}→${r.destination.slice(0,3)}`,
    demand: Number((r.demand_score * 100).toFixed(1)),
    price: Math.round(r.price),
  }));

  return (
    <div className="space-y-6" style={{ perspective: 1400 }}>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPI label="Total Flights" value={insights?.total_flights ?? 0} delay={0.0} Icon={Plane} accent="rgba(45,126,247,0.6)" />
        <KPI label="Avg Price (AUD)" value={`$${insights?.avg_price?.toFixed(0) ?? 0}`} delay={0.06} Icon={Wallet} accent="rgba(34,211,238,0.6)" />
        <KPI label="Peak Demand" value={insights?.peak_demand_score?.toFixed(2) ?? "—"} delay={0.12} Icon={Flame} accent="rgba(217,70,239,0.6)" />
        <KPI label="Routes" value={insights?.popular_routes?.length ?? 0} delay={0.18} Icon={RouteIcon} accent="rgba(16,185,129,0.6)" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-display text-lg">Top Routes by Demand</h3>
            <div className="text-xs text-white/40">demand × 100</div>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={routesData}>
              <defs>
                <linearGradient id="bar-grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22D3EE" />
                  <stop offset="100%" stopColor="#2D7EF7" />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1f2937" vertical={false} />
              <XAxis dataKey="name" stroke="#888" fontSize={11} />
              <YAxis stroke="#888" fontSize={11} />
              <Tooltip contentStyle={{ background: "#0A0F1E", border: "1px solid #374151", borderRadius: 12 }} cursor={{ fill: "rgba(255,255,255,0.04)" }} />
              <Bar dataKey="demand" fill="url(#bar-grad)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }} className="card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-display text-lg">Price Trend (30d)</h3>
            <div className="text-xs text-white/40">AUD, network avg</div>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={trendRows}>
              <defs>
                <linearGradient id="line-grad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#2D7EF7" />
                  <stop offset="100%" stopColor="#D946EF" />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1f2937" vertical={false} />
              <XAxis dataKey="date" stroke="#888" fontSize={11} />
              <YAxis stroke="#888" fontSize={11} />
              <Tooltip contentStyle={{ background: "#0A0F1E", border: "1px solid #374151", borderRadius: 12 }} />
              <Line type="monotone" dataKey="avg_price" stroke="url(#line-grad)" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="card">
        <h3 className="font-display text-lg mb-4">Airline Performance</h3>
        <div className="grid md:grid-cols-4 gap-3">
          {(insights?.airline_stats || []).map((a: any, i: number) => (
            <motion.div key={a.airline} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ delay: i * 0.06 }}
              className="glass rounded-xl p-4 hoverable hover:border-primary/40 transition">
              <div className="text-sm font-medium">{a.airline}</div>
              <div className="text-2xl font-display mt-2 gradient-text">${a.price.toFixed(0)}</div>
              <div className="text-xs text-white/50 mt-1">demand {a.demand_score.toFixed(2)}</div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
