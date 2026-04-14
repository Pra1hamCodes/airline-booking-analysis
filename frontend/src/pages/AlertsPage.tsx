import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import { useState } from "react";
import { Bell, Trash2, AlertTriangle } from "lucide-react";

export function AlertsPage() {
  const qc = useQueryClient();
  const { register, handleSubmit, reset } = useForm();
  const [err, setErr] = useState("");

  const { data: routesResp } = useQuery({
    queryKey: ["all-routes-alerts"],
    queryFn: async () => (await api.get("/api/v1/routes/?per_page=100&sort_by=demand_score")).data,
  });
  const routeOptions: string[] = (routesResp?.routes || []).map((r: any) => `${r.origin}-${r.destination}`);

  const { data } = useQuery({ queryKey: ["alerts"], queryFn: async () => (await api.get("/api/v1/alerts/")).data });

  const create = useMutation({
    mutationFn: async (d: any) => (await api.post("/api/v1/alerts/", d)).data,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["alerts"] }); reset(); setErr(""); },
    onError: (e: any) => {
      const msg = e.response?.data?.error || "Failed to create alert";
      const fields = e.response?.data?.messages;
      setErr(fields ? `${msg}: ${JSON.stringify(fields)}` : msg);
    },
  });
  const del = useMutation({
    mutationFn: async (id: string) => api.delete(`/api/v1/alerts/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const onSubmit = (d: any) => {
    setErr("");
    const threshold = parseFloat(d.threshold_value);
    if (isNaN(threshold) || threshold < 0) { setErr("Threshold must be a non-negative number"); return; }
    if (!d.route) { setErr("Select a route"); return; }
    create.mutate({ route: d.route, condition: d.condition, threshold_value: threshold });
  };

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="card">
        <div className="flex items-center gap-3 mb-5">
          <div className="h-10 w-10 rounded-xl bg-primary/15 border border-primary/30 grid place-items-center">
            <Bell size={18} className="text-accent" />
          </div>
          <h3 className="font-display text-lg">Create Alert</h3>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <select {...register("route", { required: true })} className="input w-full hoverable" defaultValue="">
            <option value="" disabled>Select a route</option>
            {routeOptions.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          <select {...register("condition")} className="input w-full hoverable">
            <option value="price_below">Price below</option>
            <option value="price_above">Price above</option>
            <option value="demand_spike">Demand spike</option>
          </select>
          <input
            {...register("threshold_value", { required: true, min: 0 })}
            placeholder="Threshold (e.g. 150 for price, 0.8 for demand)"
            type="number" step="0.01" min="0"
            className="input w-full"
          />
          <AnimatePresence>
            {err && (
              <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                className="flex items-center gap-2 text-danger text-sm bg-danger/10 border border-danger/30 rounded-lg px-3 py-2">
                <AlertTriangle size={14} /> {err}
              </motion.div>
            )}
          </AnimatePresence>
          <button type="submit" disabled={create.isPending} className="btn-primary w-full">
            {create.isPending ? "Creating..." : "Create Alert"}
          </button>
        </form>
      </motion.div>

      <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="card">
        <div className="flex justify-between items-center mb-5">
          <h3 className="font-display text-lg">Active Alerts</h3>
          <span className="glass rounded-full px-2.5 py-0.5 text-xs">{data?.alerts?.length || 0}</span>
        </div>
        <div className="space-y-2">
          <AnimatePresence>
            {(data?.alerts || []).map((a: any) => (
              <motion.div key={a.id}
                layout
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 0.9 }}
                className="flex justify-between items-center p-3 rounded-xl glass hoverable hover:border-primary/40 transition">
                <div>
                  <div className="font-medium">{a.route}</div>
                  <div className="text-xs text-white/50 mt-0.5">
                    <span className="text-accent">{a.condition.replace("_", " ")}</span> @ {a.threshold_value}
                  </div>
                </div>
                <button onClick={() => del.mutate(a.id)}
                  className="p-2 rounded-lg text-white/40 hover:text-danger hover:bg-danger/10 transition hoverable">
                  <Trash2 size={14} />
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
          {!data?.alerts?.length && <div className="text-white/40 text-sm text-center py-8">No alerts yet. Create one to get notified.</div>}
        </div>
      </motion.div>
    </div>
  );
}
