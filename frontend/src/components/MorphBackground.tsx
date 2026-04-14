export function MorphBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-40" />
      <div className="absolute left-[10%] top-[15%] h-[520px] w-[520px] rounded-full blur-[120px] opacity-40 animate-blob-1"
           style={{ background: "radial-gradient(circle,#2D7EF7,transparent 60%)" }} />
      <div className="absolute right-[5%] top-[30%] h-[480px] w-[480px] rounded-full blur-[120px] opacity-35 animate-blob-2"
           style={{ background: "radial-gradient(circle,#22D3EE,transparent 60%)" }} />
      <div className="absolute left-[40%] bottom-[5%] h-[560px] w-[560px] rounded-full blur-[140px] opacity-30 animate-blob-3"
           style={{ background: "radial-gradient(circle,#D946EF,transparent 60%)" }} />
    </div>
  );
}
