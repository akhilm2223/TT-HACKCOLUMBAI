import { useState } from "react";

const WHITE = "rgba(255,255,255,0.95)";

export function CorrectionSection() {
  return (
    <section
      id="correction"
      style={{
        height: "100vh",
        width: "100%",
        background: "#000000",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 24px 80px 24px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "radial-gradient(900px 400px at 30% 40%, rgba(255,255,255,0.02), transparent 60%)",
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "min(1300px, 96vw)", position: "relative" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 45 }}>
          <div style={{ fontSize: 44, fontWeight: 900, color: "#ffffff" }}>
            Visual Correction
          </div>
          <div style={{ marginTop: 10, fontSize: 16, color: "rgba(255,255,255,0.50)" }}>
            See exactly how to fix your shot
          </div>
        </div>

        {/* Content */}
        <div style={{ width: "100%", maxWidth: "800px", margin: "0 auto" }}>
          <div
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1.5px solid rgba(255,255,255,0.10)",
              borderRadius: 20,
              padding: 32,
              boxShadow: "0 4px 24px rgba(0,0,0,0.20)",
            }}
          >
            <CorrectedCourt />
          </div>
        </div>
      </div>
    </section>
  );
}

function CorrectedCourt() {
  const [isHovered, setIsHovered] = useState(false);
  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        background: "linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(0,0,0,1) 100%)",
        borderRadius: 14,
        border: isHovered ? "1.5px solid rgba(255,255,255,0.35)" : "1.5px solid rgba(255,255,255,0.10)",
        height: 370,
        position: "relative",
        overflow: "hidden",
        cursor: "pointer",
        transition: "border-color 0.3s ease",
      }}
    >
      {/* Net */}
      <div style={{ position: "absolute", left: 0, right: 0, top: "50%", height: 2, background: "rgba(255,255,255,0.15)", transform: "translateY(-50%)" }} />

      {/* Court lines */}
      <svg width="100%" height="100%" style={{ position: "absolute", inset: 0 }} viewBox="0 0 100 100" preserveAspectRatio="none">
        <path d="M 10,15 L 90,15 L 85,85 L 15,85 Z" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="0.3" />
        <path d="M 30,15 L 70,15 L 68,50 L 32,50 Z" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="0.3" />
        <path d="M 32,50 L 68,50 L 70,85 L 30,85 Z" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="0.3" />
        {isHovered && (
          <path d="M 50,70 Q 48,55 50,40 Q 52,25 50,20" fill="none" stroke="rgba(255,255,255,0.50)" strokeWidth="0.8" strokeDasharray="2,2"
            style={{ opacity: 0, animation: "fadeInPath 0.5s ease-out forwards" }} />
        )}
      </svg>

      {/* Ball */}
      {isHovered ? (
        <div style={{
          position: "absolute", width: 14, height: 14, borderRadius: 999,
          background: WHITE, boxShadow: "0 0 20px rgba(255,255,255,0.50)",
          transform: "translate(-50%, -50%)", zIndex: 10,
          animation: "ballTrajectory 2s ease-in-out infinite",
        }} />
      ) : (
        <div style={{
          position: "absolute", left: "50%", top: "45%", width: 14, height: 14,
          borderRadius: 999, background: WHITE, boxShadow: "0 0 20px rgba(255,255,255,0.40)",
          transform: "translate(-50%, -50%)", zIndex: 10,
        }} />
      )}

      {/* Corrected zone */}
      <div style={{
        position: "absolute", left: "50%", bottom: "25%", transform: "translateX(-50%)",
        width: 60, height: 80,
        background: "rgba(255,255,255,0.10)", border: `2px solid rgba(255,255,255,${isHovered ? '0.60' : '0.30'})`,
        borderRadius: "50% 50% 40% 40%", zIndex: 5, transition: "all 0.3s ease",
        opacity: isHovered ? 1 : 0.6,
      }} />

      {/* Player */}
      <div style={{
        position: "absolute", left: "50%", bottom: "28%", transform: "translateX(-50%)",
        width: 40, height: 50,
        background: "rgba(255,255,255,0.20)", borderRadius: "50% 50% 40% 40%", zIndex: 6,
      }} />

      <style>{`
        @keyframes ballTrajectory { 0% { left: 50%; top: 70%; } 25% { left: 48%; top: 55%; } 50% { left: 50%; top: 40%; } 75% { left: 52%; top: 25%; } 100% { left: 50%; top: 20%; } }
        @keyframes fadeInPath { from { opacity: 0; } to { opacity: 1; } }
      `}</style>
    </div>
  );
}
