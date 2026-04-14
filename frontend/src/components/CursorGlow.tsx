import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

export function CursorGlow() {
  const [active, setActive] = useState(false);
  const dot = useRef({ x: -100, y: -100 });
  const ring = useRef({ x: -100, y: -100 });
  const dotEl = useRef<HTMLDivElement>(null);
  const ringEl = useRef<HTMLDivElement>(null);
  const glowEl = useRef<HTMLDivElement>(null);
  const [hovering, setHovering] = useState(false);

  useEffect(() => {
    const move = (e: MouseEvent) => {
      dot.current.x = e.clientX;
      dot.current.y = e.clientY;
      setActive(true);
    };
    const over = (e: MouseEvent) => {
      const t = e.target as HTMLElement;
      setHovering(!!t.closest("a,button,[role=button],input,select,textarea,.hoverable"));
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseover", over);
    let raf = 0;
    const tick = () => {
      ring.current.x += (dot.current.x - ring.current.x) * 0.18;
      ring.current.y += (dot.current.y - ring.current.y) * 0.18;
      if (dotEl.current) dotEl.current.style.transform = `translate(${dot.current.x}px, ${dot.current.y}px)`;
      if (ringEl.current) ringEl.current.style.transform = `translate(${ring.current.x}px, ${ring.current.y}px)`;
      if (glowEl.current) glowEl.current.style.transform = `translate(${ring.current.x}px, ${ring.current.y}px)`;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => { cancelAnimationFrame(raf); window.removeEventListener("mousemove", move); window.removeEventListener("mouseover", over); };
  }, []);

  if (!active) return null;
  return (
    <>
      <div ref={glowEl} className="pointer-events-none fixed top-0 left-0 z-[60] -ml-[150px] -mt-[150px] h-[300px] w-[300px] rounded-full blur-3xl opacity-30"
           style={{ background: "radial-gradient(circle, rgba(45,126,247,0.6), rgba(34,211,238,0.25) 40%, transparent 70%)" }} />
      <motion.div ref={ringEl} animate={{ scale: hovering ? 1.6 : 1, opacity: hovering ? 0.9 : 0.6 }}
           className="pointer-events-none fixed top-0 left-0 z-[70] -ml-4 -mt-4 h-8 w-8 rounded-full border border-accent mix-blend-difference" />
      <motion.div ref={dotEl} animate={{ scale: hovering ? 0.4 : 1 }}
           className="pointer-events-none fixed top-0 left-0 z-[70] -ml-1 -mt-1 h-2 w-2 rounded-full bg-white mix-blend-difference" />
    </>
  );
}
