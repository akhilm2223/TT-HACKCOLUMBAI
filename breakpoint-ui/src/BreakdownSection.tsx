import { useEffect, useMemo, useState } from "react";

type Props = {
  activeRally: number | null; // becomes 7 only when section lands
};

export function BreakdownSection({ activeRally }: Props) {
  const rallies = useMemo(() => Array.from({ length: 8 }, (_, i) => i + 1), []);

  // when we land (activeRally === 7), restart the whole "enter" animation
  const [enterKey, setEnterKey] = useState(0);
  useEffect(() => {
    if (activeRally === 7) setEnterKey((k) => k + 1);
  }, [activeRally]);

  const animateIn = activeRally === 7;

  return (
    <section
      id="breakdown"
      style={{
        height: "100vh",
        width: "100%",
        background: "#050506",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 24px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* subtle background */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(800px 420px at 50% 35%, rgba(255,255,255,0.04), transparent 55%)," +
            "radial-gradient(900px 520px at 60% 70%, rgba(255,0,60,0.06), transparent 60%)",
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "min(1200px, 96vw)" }}>
        {/* Heading */}
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 56, fontWeight: 800, color: "rgba(255,255,255,0.92)" }}>
            The Breakdown
          </div>
          <div style={{ marginTop: 10, fontSize: 18, color: "rgba(255,255,255,0.55)" }}>
            Click Rally 7 to see where pressure changed everything
          </div>
        </div>

        {/* Timeline */}
        <div style={{ marginTop: 70 }}>
          <div
            key={enterKey}
            style={{
              position: "relative",
              display: "grid",
              gridTemplateRows: "22px 40px 26px",
              gap: 12,
            }}
          >
            {/* Row 1: Rally labels */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(8, 1fr)",
                columnGap: 14,
                alignItems: "end",
                color: "rgba(255,255,255,0.38)",
                fontSize: 14,
                textAlign: "center",
              }}
            >
              {rallies.map((r) => {
                const fromRightDelay = (8 - r) * 90;
                return (
                  <div
                    key={r}
                    className={animateIn ? "bp-dot-enter" : ""}
                    style={{
                      opacity: animateIn ? 0 : 1,
                      transform: animateIn ? "translateX(18px)" : "none",
                      animationDelay: `${fromRightDelay}ms`,
                    }}
                  >
                    Rally {r}
                  </div>
                );
              })}
            </div>

            {/* Row 2: Line + Nodes (perfectly aligned) */}
            <div style={{ position: "relative", height: 40 }}>
              {/* Base line */}
              <div
                style={{
                  position: "absolute",
                  left: 0,
                  right: 0,
                  top: "50%",
                  transform: "translateY(-50%)",
                  height: 2,
                  background: "rgba(255,255,255,0.10)",
                }}
              />

              {/* Animated line draw */}
              <div
                className={animateIn ? "bp-line-draw" : ""}
                style={{
                  position: "absolute",
                  left: 0,
                  right: 0,
                  top: "50%",
                  transform: "translateY(-50%) scaleX(0)",
                  transformOrigin: "left center",
                  height: 2,
                  background: "rgba(255,255,255,0.22)",
                }}
              />

              {/* Nodes */}
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  display: "grid",
                  gridTemplateColumns: "repeat(8, 1fr)",
                  columnGap: 14,
                  alignItems: "center",
                }}
              >
                {rallies.map((r) => {
                  const fromRightDelay = (8 - r) * 90;
                  const isR7 = r === 7;
                  const highlightDelay = 900;

                  return (
                    <div key={r} style={{ position: "relative", display: "flex", justifyContent: "center" }}>
                      {/* gray node */}
                      <div
                        className={animateIn ? "bp-node-enter" : ""}
                        style={{
                          width: 14,
                          height: 14,
                          borderRadius: 999,
                          background: "rgba(255,255,255,0.25)",
                          opacity: animateIn ? 0 : 1,
                          transform: animateIn ? "translateX(18px) scale(0.92)" : "none",
                          animationDelay: `${fromRightDelay + 120}ms`,
                        }}
                      />

                      {/* red overlay for Rally 7 (appears later) - FIXED POSITIONING */}
                      {isR7 && (
                        <div
                          className={animateIn ? "bp-r7-reveal" : ""}
                          style={{
                            position: "absolute",
                            top: "50%",
                            left: "50%",
                            transform: "translate(-50%, -50%)",
                            width: 18,
                            height: 18,
                            borderRadius: 999,
                            background: "rgba(255,0,60,0.95)",
                            boxShadow: "0 0 0 10px rgba(255,0,60,0.12), 0 0 40px rgba(255,0,60,0.40)",
                            opacity: 0,
                            animationDelay: `${highlightDelay}ms`,
                          }}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Row 3: Bottom labels */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(8, 1fr)",
                columnGap: 14,
                alignItems: "start",
                textAlign: "center",
                fontSize: 12,
                letterSpacing: "0.16em",
                textTransform: "uppercase",
                minHeight: 26,
              }}
            >
              {rallies.map((r) => {
                const fromRightDelay = (8 - r) * 90;
                const isR7 = r === 7;
                const highlightDelay = 900;

                if (isR7) {
                  return (
                    <div
                      key={r}
                      className={animateIn ? "bp-label-reveal" : ""}
                      style={{
                        color: "rgba(255,0,60,0.85)",
                        opacity: 0,
                        transform: "translateY(4px)",
                        animationDelay: `${highlightDelay + 120}ms`,
                      }}
                    >
                      PRESSURE SPIKE
                    </div>
                  );
                }

                if (r === 8) {
                  return (
                    <div
                      key={r}
                      className={animateIn ? "bp-label-enter" : ""}
                      style={{
                        color: "rgba(255,255,255,0.28)",
                        opacity: animateIn ? 0 : 1,
                        transform: animateIn ? "translateY(4px)" : "none",
                        animationDelay: `${fromRightDelay + 160}ms`,
                      }}
                    >
                      LOSS
                    </div>
                  );
                }

                return <div key={r} />;
              })}
            </div>
          </div>
        </div>

        {/* Bottom hint (like page 1) */}
        <div
          style={{
            position: "absolute",
            bottom: 28,
            left: 0,
            right: 0,
            textAlign: "center",
            fontSize: 12,
            letterSpacing: "0.35em",
            opacity: 0.42,
            userSelect: "none",
            color: "rgba(255,255,255,0.45)",
          }}
        >
          SCROLL TO ANALYZE <span style={{ opacity: 0.8 }}>↓</span>
        </div>
      </div>

      {/* CSS animations */}
      <style>
        {`
          .bp-line-draw {
            animation: bpLineDraw 720ms cubic-bezier(.2,.9,.2,1) forwards;
          }
          @keyframes bpLineDraw {
            from { transform: translateY(-50%) scaleX(0); opacity: 0.0; }
            to   { transform: translateY(-50%) scaleX(1); opacity: 1.0; }
          }

          .bp-dot-enter {
            animation: bpEnter 520ms cubic-bezier(.2,.9,.2,1) forwards;
          }
          .bp-node-enter {
            animation: bpEnter 520ms cubic-bezier(.2,.9,.2,1) forwards;
          }
          .bp-label-enter {
            animation: bpLabelEnter 520ms cubic-bezier(.2,.9,.2,1) forwards;
          }

          @keyframes bpEnter {
            from { opacity: 0; transform: translateX(18px) scale(0.92); }
            to   { opacity: 1; transform: translateX(0) scale(1); }
          }

          @keyframes bpLabelEnter {
            from { opacity: 0; transform: translateY(6px); }
            to   { opacity: 1; transform: translateY(0); }
          }

          .bp-r7-reveal {
            animation: bpR7Reveal 540ms cubic-bezier(.2,.9,.2,1) forwards;
          }
          @keyframes bpR7Reveal {
            0%   { opacity: 0; transform: translate(-50%, -50%) scale(0.75); }
            60%  { opacity: 1; transform: translate(-50%, -50%) scale(1.08); }
            100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
          }

          .bp-label-reveal {
            animation: bpLabelEnter 520ms cubic-bezier(.2,.9,.2,1) forwards;
          }
        `}
      </style>
    </section>
  );
}