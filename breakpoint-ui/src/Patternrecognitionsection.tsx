import { useEffect, useRef, useState } from "react";
import type { Shot, Court } from "./lib/matchData";
import { MATCHES, analyzeMatch, totalShots } from "./lib/matchData";
import { MiniCoach } from "./MiniCoach";

/* ── colour tokens ─────────────────────────────────────────────── */
const C = {
  white: "rgba(255,255,255,0.95)",
  dim: "rgba(255,255,255,0.50)",
  muted: "rgba(255,255,255,0.35)",
  faint: "rgba(255,255,255,0.20)",
  ghost: "rgba(255,255,255,0.08)",
  panel: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.10)",
  blue: "rgba(96,165,250,0.85)",
  blueDim: "rgba(96,165,250,0.45)",
  blueBand: "rgba(96,165,250,0.10)",
  red: "rgba(248,113,113,0.80)",
  redDim: "rgba(248,113,113,0.35)",
  green: "rgba(74,222,128,0.80)",
  greenDim: "rgba(74,222,128,0.15)",
  amber: "rgba(255,180,60,0.80)",
  amberDim: "rgba(255,180,60,0.12)",
  danger: "rgba(220,80,60,0.85)",
  table: "#1a5c3a",
  tableLine: "rgba(255,255,255,0.65)",
};


/* ══════════════════════════════════════════════════════════════════
   MAIN EXPORT
   ══════════════════════════════════════════════════════════════════ */
export function PatternRecognitionSection() {
  const [isVisible, setIsVisible] = useState(false);
  const [selected, setSelected] = useState(0);
  const [activeTab, setActiveTab] = useState<"new" | "past">("past");
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting && entry.intersectionRatio >= 0.15) setIsVisible(true); },
      { threshold: [0.15] },
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  const m = MATCHES[selected];
  const insights = analyzeMatch(m);

  const anim = (delay: number) => ({
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? "translateY(0)" : "translateY(20px)",
    transition: `all 0.6s cubic-bezier(.2,.9,.2,1) ${delay}s`,
  });

  return (
    <section
      ref={sectionRef}
      id="pattern-recognition"
      style={{ width: "100%", background: "#000", padding: "80px 24px 100px", position: "relative", overflow: "hidden" }}
    >
      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: "radial-gradient(900px 400px at 30% 20%, rgba(96,165,250,0.03), transparent 60%)," +
          "radial-gradient(800px 500px at 70% 60%, rgba(248,113,113,0.02), transparent 60%)",
      }} />

      <div style={{ width: "min(1400px, 96vw)", margin: "0 auto", position: "relative" }}>

        {/* ── header ─────────────────────────────────── */}
        <div style={{ textAlign: "center", marginBottom: 36, ...anim(0) }}>
          <div style={{ fontSize: 44, fontWeight: 900, color: "#fff", lineHeight: 1.1 }}>Match Intelligence</div>
          <div style={{ marginTop: 10, fontSize: 16, color: C.dim }}>
            Turn every game into insights, every insight into wins
          </div>
          <div style={{ marginTop: 6, fontSize: 12, color: C.muted, letterSpacing: "0.03em" }}>
            {totalShots} shots &middot; {MATCHES.length} matches analyzed
          </div>
        </div>

        {/* ── tab bar ────────────────────────────────── */}
        <div style={{
          display: "flex", gap: 12, marginBottom: 32,
          borderBottom: `2px solid ${C.ghost}`, paddingBottom: 2, ...anim(0.05),
        }}>
          {(["new", "past"] as const).map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              all: "unset", cursor: "pointer", fontSize: 14, fontWeight: 800,
              letterSpacing: "0.02em", textTransform: "uppercase" as const,
              color: activeTab === tab ? "#fff" : C.dim,
              padding: "12px 24px", marginBottom: -2,
              borderBottom: activeTab === tab ? "3px solid #fff" : "3px solid transparent",
              transition: "all 0.25s ease",
            }}>
              {tab === "new" ? "New Analysis" : "Past Match Analytics"}
            </button>
          ))}
        </div>

        {activeTab === "new" ? (
          <div style={{ textAlign: "center", padding: "80px 20px", ...anim(0.1) }}>
            <div style={{
              width: 80, height: 80, margin: "0 auto 20px", borderRadius: "50%",
              background: C.panel, border: `2px dashed ${C.faint}`,
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32, color: C.dim,
            }}>+</div>
            <div style={{ fontSize: 24, fontWeight: 800, color: "#fff", marginBottom: 8 }}>No New Analysis</div>
            <div style={{ fontSize: 14, color: C.dim, maxWidth: 400, margin: "0 auto" }}>
              Upload and analyze a new match to see real-time insights
            </div>
          </div>
        ) : (
          <>
            {/* ── match selector ─────────────────────── */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 28, ...anim(0.08) }}>
              {MATCHES.map((match, i) => {
                const mi = analyzeMatch(match);
                return (
                  <button key={match.id} onClick={() => { setSelected(i); }} style={{
                    all: "unset", cursor: "pointer",
                    background: selected === i ? C.ghost : C.panel,
                    border: selected === i ? `1.5px solid ${C.white}` : `1.5px solid ${C.border}`,
                    borderRadius: 14, padding: "18px 14px", textAlign: "center",
                    transition: "all 0.25s ease",
                    boxShadow: selected === i ? "0 0 20px rgba(255,255,255,0.06)" : "none",
                  }}>
                    <div style={{ fontSize: 14, fontWeight: 800, color: selected === i ? "#fff" : C.dim, marginBottom: 4 }}>
                      {match.label}
                    </div>
                    <div style={{ fontSize: 11, color: C.muted }}>{match.date} &middot; {match.time}</div>
                    <div style={{ fontSize: 11, color: C.faint, marginTop: 4 }}>
                      {match.shots_count} shots &middot; 1 rally
                    </div>
                    <div style={{
                      marginTop: 6, fontSize: 11, fontWeight: 700,
                      color: mi.winPct >= 50 ? C.green : mi.winPct > 0 ? C.amber : C.danger,
                    }}>
                      {mi.winPct}% win rate
                    </div>
                  </button>
                );
              })}
            </div>

            {/* ── ROW 1: Court + Stats side by side ──── */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24, ...anim(0.15) }}>
              {/* LEFT: Large court for selected match */}
              <div style={{
                background: C.panel, border: `1.5px solid ${C.border}`, borderRadius: 20, padding: 20,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
                  <div>
                    <span style={{ fontSize: 10, letterSpacing: "0.12em", color: C.muted, fontWeight: 700, textTransform: "uppercase" }}>
                      Shot Placement &middot; {m.label}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: 14 }}>
                    <LegendDot color={C.blue} label="You" />
                    <LegendDot color={C.red} label="Opponent" />
                  </div>
                </div>
                <CourtSVG shots={m.shots} court={m.court} />
                <div style={{ marginTop: 10, fontSize: 11, color: C.dim, textAlign: "center" }}>
                  {insights.selfFar > 0 && insights.selfNear === 0
                    ? "All your shots land deep \u2014 add short game to surprise opponent"
                    : insights.selfNear > 0 && insights.selfFar === 0
                      ? "All your shots land short \u2014 push deeper to control the rally"
                      : `${insights.selfFar} deep shots, ${insights.selfNear} short shots`
                  }
                </div>
              </div>

              {/* RIGHT: Match stats panel */}
              <div style={{
                background: C.panel, border: `1.5px solid ${C.border}`, borderRadius: 20, padding: 24,
              }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                  <div>
                    <div style={{ fontSize: 17, fontWeight: 800, color: "#fff" }}>Recording {m.id}</div>
                    <div style={{ fontSize: 12, color: C.dim, marginTop: 2 }}>{m.date} at {m.time} &middot; {m.duration}</div>
                  </div>
                  <div style={{
                    fontSize: 10, letterSpacing: "0.12em", fontWeight: 800, padding: "5px 12px",
                    borderRadius: 999, textTransform: "uppercase",
                    background: insights.winPct >= 50 ? C.greenDim : C.amberDim,
                    color: insights.winPct >= 50 ? C.green : C.amber,
                  }}>
                    {insights.winPct}% wins
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 14 }}>
                  <NumCard label="Shots" value={m.shots_count} />
                  <NumCard label="Rally" value={1} />
                  <NumCard label="Avg Rally" value={`${m.avgRally}s`} />
                  <NumCard label="Forehand" value={`${m.forehand}%`} color={C.blue} />
                  <NumCard label="Backhand" value={`${m.backhand}%`} color={m.backhand > 0 ? C.red : C.muted} />
                  <NumCard label="Aggression" value={m.aggression.toFixed(2)}
                    color={m.aggression < 0.35 ? C.danger : m.aggression < 0.45 ? C.amber : C.green}
                    sub={m.aggression < 0.45 ? "Optimal: 0.45\u20130.65" : undefined} />
                </div>

                <MetricBar label="Footwork Drop" value={m.footworkDrop} max={50} suffix="%" warn />
                <MetricBar label="Arm Speed" value={m.avgArmSpeed} max={12} suffix=" px/f" />
                <MetricBar label="Foot Speed" value={m.avgFootSpeed} max={8} suffix=" px/s" />

                <div style={{
                  marginTop: 12, padding: "10px 14px",
                  background: "rgba(255,140,60,0.06)", border: "1px solid rgba(255,140,60,0.20)", borderRadius: 10,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                    <span style={{ fontSize: 14, color: C.amber }}>!</span>
                    <span style={{ fontSize: 9, letterSpacing: "0.12em", color: "rgba(255,140,60,0.85)", fontWeight: 700 }}>
                      PRESSURE MOMENT
                    </span>
                  </div>
                  <div style={{ fontSize: 11, color: "rgba(255,255,255,0.65)", lineHeight: 1.4 }}>{m.pressureMoment}</div>
                </div>

                <div style={{ marginTop: 14, display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 10, color: C.muted, letterSpacing: "0.08em", fontWeight: 600 }}>AI CONFIDENCE</span>
                  <div style={{ flex: 1, height: 4, borderRadius: 2, background: C.ghost, overflow: "hidden" }}>
                    <div style={{ width: `${m.coaching.confidence * 100}%`, height: "100%", borderRadius: 2, background: C.white, transition: "width 0.6s ease" }} />
                  </div>
                  <span style={{ fontSize: 13, fontWeight: 800, color: C.white }}>{Math.round(m.coaching.confidence * 100)}%</span>
                </div>
              </div>
            </div>

            {/* ── ROW 2: Interactive AI Coach ─────────── */}
            <div style={{
              background: C.panel, border: `1.5px solid ${C.border}`, borderRadius: 20,
              padding: 28, ...anim(0.35),
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
                <div style={{
                  width: 40, height: 40, borderRadius: 999,
                  background: "linear-gradient(135deg, rgba(96,165,250,0.9), rgba(74,222,128,0.7))",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 15, fontWeight: 900, color: "#000",
                }}>AI</div>
                <div>
                  <div style={{ fontSize: 16, fontWeight: 800, color: "#fff" }}>Your AI Coach</div>
                  <div style={{ fontSize: 10, color: C.muted, letterSpacing: "0.1em" }}>ASK ANYTHING ABOUT {m.label.toUpperCase()}</div>
                </div>
              </div>
              <MiniCoach match={m} />
            </div>
          </>
        )}
      </div>
    </section>
  );
}

/* ══════════════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ══════════════════════════════════════════════════════════════════ */

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
      <div style={{ width: 8, height: 8, borderRadius: 999, background: color }} />
      <span style={{ fontSize: 11, color: C.dim }}>{label}</span>
    </div>
  );
}


function NumCard({ label, value, color, sub }: { label: string; value: string | number; color?: string; sub?: string }) {
  return (
    <div style={{ background: C.panel, border: `1px solid ${C.ghost}`, borderRadius: 10, padding: "10px 8px", textAlign: "center" }}>
      <div style={{ fontSize: 20, fontWeight: 900, color: color || "#fff", marginBottom: 2 }}>{value}</div>
      <div style={{ fontSize: 9, color: C.muted, letterSpacing: "0.05em", textTransform: "uppercase" }}>{label}</div>
      {sub && <div style={{ fontSize: 8, color: C.amber, marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

function MetricBar({ label, value, max, suffix, warn }: { label: string; value: number; max: number; suffix: string; warn?: boolean }) {
  const pct = Math.min((value / max) * 100, 100);
  const color = warn ? C.danger : C.white;
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ fontSize: 11, color: C.dim }}>{label}</span>
        <span style={{ fontSize: 12, fontWeight: 700, color }}>{value}{suffix}</span>
      </div>
      <div style={{ height: 4, borderRadius: 2, background: C.ghost, overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", borderRadius: 2, background: color, transition: "width 0.6s ease" }} />
      </div>
    </div>
  );
}

/* ── Court SVG (green table tennis table) ────────────────────── */
function CourtSVG({ shots }: { shots: Shot[]; court: Court }) {
  const W = 400, H = 260;
  const pad = 8;
  const tW = W - pad * 2, tH = H - pad * 2;
  const netY = pad + tH / 2;

  const selfShots = shots.filter(s => s.player === "self");
  const oppShots = shots.filter(s => s.player === "opponent");

  /* position a shot within its half, using zone for left/center/right */
  function getPos(s: Shot, idx: number, total: number, topHalf: boolean) {
    const zone = s.landing.zone;
    const seed = ((s.shot_id * 7 + 3) % 11) / 11;

    /* X: place in left / center / right third */
    let xBase = 0.50;
    if (zone.includes("left")) xBase = 0.18;
    else if (zone.includes("right")) xBase = 0.82;
    const xJitter = (seed - 0.5) * 0.10;
    const x = pad + Math.max(0.06, Math.min(0.94, xBase + xJitter)) * tW;

    /* Y: evenly spread within the half, with margin from net & edge */
    const margin = 16;
    const yMin = topHalf ? pad + margin : netY + margin;
    const yMax = topHalf ? netY - margin : pad + tH - margin;
    const range = yMax - yMin;
    const y = total > 1 ? yMin + (idx / (total - 1)) * range : yMin + range / 2;
    const yJit = (seed - 0.5) * 6;

    return { cx: x, cy: y + yJit };
  }

  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", display: "block", borderRadius: 8 }}>
      <rect width={W} height={H} fill="#0a0a0a" rx={8} />
      <rect x={pad} y={pad} width={tW} height={tH} rx={4} fill={C.table} />
      <rect x={pad} y={pad} width={tW} height={tH} rx={4} fill="none" stroke={C.tableLine} strokeWidth={2} />
      {/* net */}
      <line x1={pad} y1={netY} x2={pad + tW} y2={netY} stroke="rgba(255,255,255,0.85)" strokeWidth={2.5} />
      <line x1={pad} y1={netY} x2={pad + tW} y2={netY} stroke="rgba(255,255,255,0.15)" strokeWidth={6} />
      {/* center line */}
      <line x1={pad + tW / 2} y1={pad} x2={pad + tW / 2} y2={pad + tH} stroke={C.tableLine} strokeWidth={1} />
      {/* zone grid */}
      <line x1={pad + tW / 3} y1={pad} x2={pad + tW / 3} y2={pad + tH} stroke="rgba(255,255,255,0.12)" strokeWidth={0.5} strokeDasharray="4 4" />
      <line x1={pad + (tW * 2) / 3} y1={pad} x2={pad + (tW * 2) / 3} y2={pad + tH} stroke="rgba(255,255,255,0.12)" strokeWidth={0.5} strokeDasharray="4 4" />
      {/* side labels */}
      <text x={pad + tW / 2} y={netY - 8} textAnchor="middle" fill="rgba(255,255,255,0.30)" fontSize={10} fontWeight={600}>OPPONENT SIDE</text>
      <text x={pad + tW / 2} y={netY + 16} textAnchor="middle" fill="rgba(255,255,255,0.30)" fontSize={10} fontWeight={600}>YOUR SIDE</text>
      {/* self shots → top half (your shots land on opponent's side) */}
      {selfShots.map((s, i) => {
        const { cx, cy } = getPos(s, i, selfShots.length, true);
        return (
          <g key={s.shot_id}>
            <circle cx={cx} cy={cy} r={10} fill="rgba(96,165,250,0.3)" opacity={0}>
              <animate attributeName="opacity" from="0" to="0.6" dur="0.5s" fill="freeze" begin={`${s.shot_id * 0.05}s`} />
            </circle>
            <circle cx={cx} cy={cy} r={6} fill="rgba(96,165,250,1)" stroke="#000" strokeWidth={1.5} opacity={0}>
              <animate attributeName="opacity" from="0" to="1" dur="0.3s" fill="freeze" begin={`${s.shot_id * 0.05}s`} />
            </circle>
          </g>
        );
      })}
      {/* opponent shots → bottom half (their shots land on your side) */}
      {oppShots.map((s, i) => {
        const { cx, cy } = getPos(s, i, oppShots.length, false);
        return (
          <g key={s.shot_id}>
            <circle cx={cx} cy={cy} r={10} fill="rgba(248,113,113,0.3)" opacity={0}>
              <animate attributeName="opacity" from="0" to="0.6" dur="0.5s" fill="freeze" begin={`${s.shot_id * 0.05}s`} />
            </circle>
            <circle cx={cx} cy={cy} r={6} fill="rgba(248,113,113,1)" stroke="#000" strokeWidth={1.5} opacity={0}>
              <animate attributeName="opacity" from="0" to="1" dur="0.3s" fill="freeze" begin={`${s.shot_id * 0.05}s`} />
            </circle>
          </g>
        );
      })}
    </svg>
  );
}


