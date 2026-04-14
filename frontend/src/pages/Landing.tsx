import { motion, useScroll, useTransform } from "framer-motion";
import { Link } from "react-router-dom";
import { useRef } from "react";
import { AustraliaGlobe } from "@/components/AustraliaGlobe";
import { Tilt } from "@/components/Tilt";
import { Plane, TrendingUp, Bell, FileBarChart, Sparkles, Zap, LineChart, ShieldCheck } from "lucide-react";

const features = [
  { icon: LineChart, title: "Live Price Signals", desc: "5,400+ snapshots across 30 Australian routes refreshed every 6h." },
  { icon: TrendingUp, title: "14-Day Forecasts", desc: "ARIMA + polynomial models project price bands out two weeks." },
  { icon: Bell, title: "Threshold Alerts", desc: "Ping when a route breaks your price floor or demand spikes." },
  { icon: FileBarChart, title: "PDF / CSV / Excel", desc: "Board-ready reports in one click, scheduled or on-demand." },
  { icon: ShieldCheck, title: "JWT Secured", desc: "Per-user alert rules. No leaked dashboards." },
  { icon: Zap, title: "Instant Insights", desc: "Server-side aggregation. No client-heavy crunching." },
];

const stats = [
  { k: "30", v: "Routes", sub: "Sydney → Darwin & beyond" },
  { k: "4", v: "Airlines", sub: "Qantas, Virgin, Jetstar, Tiger" },
  { k: "5.4K+", v: "Snapshots", sub: "60-day history" },
  { k: "1.6K", v: "Forecasts", sub: "14-day ARIMA projections" },
];

export function Landing() {
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ["start start", "end start"] });
  const yGlobe = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const opHero = useTransform(scrollYProgress, [0, 1], [1, 0.15]);
  const scaleHero = useTransform(scrollYProgress, [0, 1], [1, 0.9]);

  return (
    <div className="relative">
      {/* HERO */}
      <section ref={heroRef} className="relative min-h-screen overflow-hidden">
        <motion.div style={{ y: yGlobe, opacity: opHero }} className="absolute inset-0 opacity-70">
          <AustraliaGlobe />
        </motion.div>
        <motion.div style={{ opacity: opHero, scale: scaleHero }}
          className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6 text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}
            className="glass rounded-full px-4 py-1.5 mb-6 text-sm flex items-center gap-2">
            <Sparkles size={14} className="text-accent" /> Live Australian aviation market intelligence
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}
            className="font-display text-6xl md:text-8xl font-bold leading-[1.05] tracking-tight">
            <span className="gradient-text" style={{ backgroundSize: "200% 100%", animation: "gradient-x 6s ease infinite" }}>
              Airline Demand,
            </span>
            <br />
            <span className="text-white">Decoded.</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3, duration: 0.8 }}
            className="mt-6 text-lg md:text-xl text-white/60 max-w-2xl">
            Real-time price tracking, demand forecasting, and route intelligence for Australian hostel operators. Built on live data across 6 cities and 4 carriers.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
            className="mt-10 flex gap-4 flex-wrap justify-center">
            <Link to="/auth" className="btn-primary px-6 py-3 text-base flex items-center gap-2">
              <Plane size={16} /> Launch Platform
            </Link>
            <Link to="/auth?mode=login" className="btn-ghost px-6 py-3 text-base">Sign In</Link>
          </motion.div>
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.2 }}
            className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/40 text-xs">
            <span>scroll</span>
            <motion.div animate={{ y: [0, 8, 0] }} transition={{ repeat: Infinity, duration: 1.6 }}
              className="h-8 w-[1px] bg-gradient-to-b from-white/50 to-transparent" />
          </motion.div>
        </motion.div>
      </section>

      {/* STATS BAR */}
      <section className="relative py-16 px-6 max-w-6xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((s, i) => (
            <motion.div key={s.v}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ delay: i * 0.08, duration: 0.6 }}
              className="card text-center">
              <div className="text-4xl font-display font-bold gradient-text">{s.k}</div>
              <div className="mt-1 text-white/80 font-medium">{s.v}</div>
              <div className="text-xs text-white/40 mt-1">{s.sub}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* FEATURES */}
      <section className="relative py-24 px-6 max-w-6xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="text-center mb-14">
          <div className="text-accent text-sm tracking-widest uppercase">Features</div>
          <h2 className="font-display text-4xl md:text-5xl font-bold mt-3">
            Everything you need to <span className="gradient-text">price smarter</span>.
          </h2>
        </motion.div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f, i) => (
            <motion.div key={f.title}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ delay: i * 0.06, duration: 0.5 }}>
              <Tilt className="card card-hover h-full hoverable">
                <div className="h-11 w-11 rounded-xl grid place-items-center ring-glow bg-primary/10 mb-4">
                  <f.icon size={20} className="text-accent" />
                </div>
                <h3 className="font-display text-lg mb-1">{f.title}</h3>
                <p className="text-white/60 text-sm leading-relaxed">{f.desc}</p>
              </Tilt>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="relative py-24 px-6">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }} transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto text-center card ring-glow py-14">
          <h2 className="font-display text-4xl md:text-5xl font-bold">
            Ready to see the <span className="gradient-text">market move?</span>
          </h2>
          <p className="text-white/60 mt-4 max-w-xl mx-auto">
            Create a free account, pick your routes, set alert thresholds, and let the data work.
          </p>
          <div className="mt-8 flex justify-center gap-3 flex-wrap">
            <Link to="/auth" className="btn-primary px-6 py-3">Get Started</Link>
            <Link to="/auth?mode=login" className="btn-ghost px-6 py-3">I have an account</Link>
          </div>
        </motion.div>
        <div className="text-center text-white/30 text-xs mt-10">
          Built with Flask · React · Three.js · Framer Motion
        </div>
      </section>
    </div>
  );
}
