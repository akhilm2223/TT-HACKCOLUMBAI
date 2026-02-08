import { PingPongScene3D } from "./scene/PingPongScene";

export function Hero3D({ onNext }: { onNext: () => void }) {
  return (
    <div
      style={{
        position: "relative",
        height: "100vh",
        width: "100%",
        background: "#050506",
        overflow: "hidden",
      }}
    >
      {/* Subtle background glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(700px 320px at 50% 35%, rgba(255,0,60,0.10), transparent 60%)," +
            "radial-gradient(900px 520px at 50% 70%, rgba(255,255,255,0.04), transparent 60%)",
          pointerEvents: "none",
        }}
      />

      {/* 3D STAGE (smaller, clipped, background) */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "60%",
          transform: "translate(-50%, -50%) scale(0.98)",
          width: "min(1100px, 92vw)",
          height: "min(560px, 62vh)",
          borderRadius: 26,
          overflow: "hidden",
          opacity: 0.34, // <-- background feel
          filter: "blur(0.6px)",
          boxShadow: "0 50px 140px rgba(0,0,0,0.75)",
          border: "1px solid rgba(255,255,255,0.06)",
          pointerEvents: "none",
        }}
      >
        <PingPongScene3D />

        {/* cinematic fade/vignette so 3D blends into UI */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(to top, rgba(5,5,6,0.0) 40%, rgba(5,5,6,0.85) 85%, rgba(5,5,6,1) 100%)," +
              "radial-gradient(70% 60% at 50% 60%, rgba(0,0,0,0.0), rgba(0,0,0,0.75) 70%)",
            pointerEvents: "none",
          }}
        />
      </div>

      {/* UI overlay */}
      <div style={{ position: "absolute", inset: 0 }}>
        {/* Top center brand */}
        <div
  style={{
    position: "absolute",
    top: 22,
    left: "50%",
    transform: "translateX(-50%)",
    fontSize: 28,                 // bigger
    fontWeight: 900,
    letterSpacing: "0.10em",
    color: "rgba(255,255,255,0.96)",
  }}
>
  Break Point
</div>

        {/* Top right pill */}
        <div
          style={{
            position: "absolute",
            top: 22,
            right: 36,
            border: "1px solid rgba(255,0,60,0.55)",
            color: "rgba(255,0,60,0.95)",
            padding: "10px 14px",
            borderRadius: 999,
            fontSize: 12,
            letterSpacing: "0.15em",
            fontWeight: 700,
            background: "rgba(0,0,0,0.15)",
            backdropFilter: "blur(8px)",
          }}
        >
          LIVE ANALYSIS
        </div>

        {/* Center content */}
        <div
          style={{
            position: "absolute",
            top: 140,
            left: 0,
            right: 0,
            textAlign: "center",
            padding: "0 18px",
          }}
        >
          {/* Score smaller */}
          <div
            style={{
              fontSize: 84,
              fontWeight: 900,
              opacity: 0.92,
              lineHeight: 1,
              color: "rgba(255,255,255,0.94)",
            }}
          >
            10 <span style={{ opacity: 0.22 }}>–</span>{" "}
            <span style={{ opacity: 0.50 }}>9</span>
          </div>

          {/* Break point badge */}
          <div
            style={{
              display: "inline-flex",
              marginTop: 10,
              padding: "8px 14px",
              borderRadius: 999,
              background: "rgba(255,0,60,0.92)",
              color: "rgba(255,255,255,0.95)",
              fontWeight: 900,
              letterSpacing: "0.22em",
              fontSize: 11,
            }}
          >
            BREAK POINT
          </div>

          {/* Product one-liner (judge-friendly) */}
          

          {/* Micro-metrics (optional but makes it look premium) */}
          
        </div>

        {/* Bottom hint */}
        <div
          onClick={onNext}
          style={{
            position: "absolute",
            bottom: 28,
            left: 0,
            right: 0,
            textAlign: "center",
            fontSize: 12,
            letterSpacing: "0.35em",
            opacity: 0.42,
            cursor: "pointer",
            userSelect: "none",
          }}
        >
          SCROLL TO ANALYZE
        </div>
      </div>
    </div>
  );
}

function Metric({
  title,
  value,
  accent,
}: {
  title: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div
      style={{
        padding: "10px 14px",
        borderRadius: 14,
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
        minWidth: 175,
        textAlign: "left",
        backdropFilter: "blur(10px)",
      }}
    >
      <div
        style={{
          fontSize: 11,
          letterSpacing: "0.18em",
          color: "rgba(255,255,255,0.45)",
          fontWeight: 700,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontSize: 16,
          fontWeight: 900,
          marginTop: 4,
          color: accent ? "rgba(255,0,60,0.95)" : "rgba(255,255,255,0.90)",
        }}
      >
        {value}
      </div>
    </div>
  );
}
