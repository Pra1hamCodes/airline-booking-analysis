import { useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { FileSpreadsheet, FileText, Download, Table } from "lucide-react";
import { Tilt } from "@/components/Tilt";

export function ReportsPage() {
  const [loading, setLoading] = useState<string | null>(null);

  const download = async (path: string, filename: string) => {
    setLoading(path);
    const token = localStorage.getItem("access_token");
    const r = await fetch(path, { headers: { Authorization: `Bearer ${token}` } });
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
    setLoading(null);
  };

  const generatePdf = async () => {
    setLoading("pdf");
    const today = new Date().toISOString().slice(0, 10);
    const weekAgo = new Date(Date.now() - 7 * 864e5).toISOString().slice(0, 10);
    const r = await api.post("/api/v1/export/pdf-report", {
      date_from: weekAgo, date_to: today, include_forecast: true,
    });
    if (r.data.pdf_base64) {
      const bin = atob(r.data.pdf_base64);
      const arr = Uint8Array.from(bin, (c) => c.charCodeAt(0));
      const url = URL.createObjectURL(new Blob([arr], { type: "application/pdf" }));
      const a = document.createElement("a"); a.href = url; a.download = "report.pdf"; a.click();
    }
    setLoading(null);
  };

  const cards = [
    { label: "CSV Export", desc: "Raw flight data, 5000 rows max", Icon: Table, accent: "from-success/20 to-success/5",
      action: () => download("/api/v1/export/csv", "flights.csv"), key: "/api/v1/export/csv" },
    { label: "Excel Report", desc: "Multi-sheet: Overview · Routes · Flights", Icon: FileSpreadsheet, accent: "from-primary/20 to-primary/5",
      action: () => download("/api/v1/export/excel", "report.xlsx"), key: "/api/v1/export/excel" },
    { label: "PDF Briefing", desc: "Executive summary · last 7 days · with forecast", Icon: FileText, accent: "from-magenta/20 to-magenta/5",
      action: generatePdf, key: "pdf" },
  ];

  return (
    <div className="grid md:grid-cols-3 gap-5" style={{ perspective: 1400 }}>
      {cards.map((c, i) => (
        <motion.div key={c.key}
          initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
          <Tilt className={`card card-hover h-full hoverable bg-gradient-to-br ${c.accent} overflow-hidden`}>
            <div className="h-12 w-12 rounded-xl glass grid place-items-center mb-4">
              <c.Icon size={22} className="text-accent" />
            </div>
            <h3 className="font-display text-xl">{c.label}</h3>
            <p className="text-white/50 text-sm mt-1 mb-6">{c.desc}</p>
            <button onClick={c.action} disabled={loading === c.key}
              className="btn-primary w-full flex items-center justify-center gap-2">
              <Download size={14} /> {loading === c.key ? "Generating..." : "Download"}
            </button>
          </Tilt>
        </motion.div>
      ))}
    </div>
  );
}
