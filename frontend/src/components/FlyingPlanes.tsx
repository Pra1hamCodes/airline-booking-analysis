import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Plane } from "lucide-react";

type Flight = {
  id: number;
  top: number;        // vh
  duration: number;   // seconds
  delay: number;
  size: number;       // px
  angle: number;      // deg — slight diagonal
  direction: 1 | -1;  // 1 = L→R, -1 = R→L
  opacity: number;
};

const rand = (a: number, b: number) => a + Math.random() * (b - a);

function makeFlight(id: number): Flight {
  const direction: 1 | -1 = Math.random() < 0.5 ? 1 : -1;
  return {
    id,
    top: rand(5, 85),
    duration: rand(14, 26),
    delay: rand(0, 8),
    size: rand(14, 22),
    angle: rand(-12, 12),
    direction,
    opacity: rand(0.25, 0.55),
  };
}

export function FlyingPlanes({ count = 6 }: { count?: number }) {
  const [flights, setFlights] = useState<Flight[]>([]);

  useEffect(() => {
    setFlights(Array.from({ length: count }, (_, i) => makeFlight(i)));
  }, [count]);

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-[5] overflow-hidden">
      {flights.map((f) => {
        const rotation = f.direction === 1 ? 45 + f.angle : 225 + f.angle;
        const fromX = f.direction === 1 ? "-10vw" : "110vw";
        const toX = f.direction === 1 ? "110vw" : "-10vw";
        return (
          <motion.div
            key={f.id}
            className="absolute"
            style={{ top: `${f.top}vh`, left: 0, opacity: f.opacity }}
            initial={{ x: fromX, y: 0 }}
            animate={{ x: toX, y: [0, -12, 8, -4, 0] }}
            transition={{
              x: { duration: f.duration, delay: f.delay, repeat: Infinity, ease: "linear", repeatDelay: rand(2, 6) },
              y: { duration: f.duration, delay: f.delay, repeat: Infinity, ease: "easeInOut" },
            }}
            onAnimationComplete={() =>
              setFlights((prev) => prev.map((p) => (p.id === f.id ? makeFlight(f.id) : p)))
            }
          >
            <div className="relative flex items-center" style={{ transform: `rotate(${rotation}deg)` }}>
              {/* contrail */}
              <div
                className="absolute right-full mr-1 h-[1.5px] rounded-full"
                style={{
                  width: `${f.size * 8}px`,
                  background: `linear-gradient(to left, rgba(34,211,238,${f.opacity}), transparent)`,
                }}
              />
              <Plane
                size={f.size}
                className="text-accent drop-shadow-[0_0_6px_rgba(34,211,238,0.6)]"
                fill="currentColor"
              />
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
