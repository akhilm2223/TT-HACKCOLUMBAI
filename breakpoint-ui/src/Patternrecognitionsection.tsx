import { useEffect, useRef, useState } from "react";

<<<<<<< HEAD
const WHITE = "rgba(255,255,255,0.95)";

// Real match data from analysis pipeline
const MATCHES = [
  {
    id: "224148",
    label: "Match 1",
    time: "10:41 PM",
    date: "Feb 7",
    duration: "1:31",
    shots: 22,
    rallies: 17,
    footworkDrop: 25,
    aggression: 0.27,
    forehand: 36.4,
    backhand: 22.7,
    avgRally: 1.19,
    avgArmSpeed: 3.79,
    avgFootSpeed: 5.04,
    style: "passive",
    coaching: {
      headline: "You're playing too passively; time to attack.",
      advice: "Step in and drive after pushing.",
      mentalCue: "Breathe, step, drive.",
      finding: "You primarily pushed the ball, with a low aggression index.",
      evidence: "Aggression index is 0.27. Forehand 36.4%, backhand 22.7%.",
      strategy: "After your push, immediately step forward and prepare a forehand drive.",
      mentalIssue: "Hesitation after pushing leads to passive play.",
      confidence: 0.85,
    },
  },
  {
    id: "153355",
    label: "Match 2",
    time: "3:33 PM",
    date: "Feb 7",
    duration: "0:26",
    shots: 10,
    rallies: 4,
    footworkDrop: 29,
    aggression: 0.36,
    forehand: 30.0,
    backhand: 0,
    avgRally: 1.04,
    avgArmSpeed: 5.69,
    avgFootSpeed: 2.67,
    style: "passive",
    coaching: {
      headline: "Predictable push placement makes it easy for your opponent.",
      advice: "Mix up your push placement and prepare to attack.",
      mentalCue: "Breathe, shift, attack!",
      finding: "You primarily pushed the ball to the opponent's left side.",
      evidence: "7 out of 10 shots landed in the near_left zone.",
      strategy: "Vary your push placement to include the opponent's right side.",
      mentalIssue: "Hesitation after pushing, leading to a passive stance.",
      confidence: 0.80,
    },
  },
  {
    id: "192747",
    label: "Match 3",
    time: "7:27 PM",
    date: "Feb 7",
    duration: "0:16",
    shots: 6,
    rallies: 3,
    footworkDrop: 27,
    aggression: 0.41,
    forehand: 16.7,
    backhand: 0,
    avgRally: 0.96,
    avgArmSpeed: 8.99,
    avgFootSpeed: 4.87,
    style: "passive",
    coaching: {
      headline: "Too passive — take control of the rally.",
      advice: "Prepare a forehand drive after every push.",
      mentalCue: "Breathe, step, drive.",
      finding: "Frequently pushing with limited forehand drives observed.",
      evidence: "16.7% forehand usage across 6 shots.",
      strategy: "After your push, step forward and prepare a forehand drive.",
      mentalIssue: "Hesitation after pushing leads to passive play.",
      confidence: 0.75,
    },
  },
  {
    id: "134224",
    label: "Match 4",
    time: "1:42 PM",
    date: "Feb 7",
    duration: "0:16",
    shots: 6,
    rallies: 3,
    footworkDrop: 35,
    aggression: 0.39,
    forehand: 66.7,
    backhand: 0,
    avgRally: 0.89,
    avgArmSpeed: 7.17,
    avgFootSpeed: 5.7,
    style: "passive",
    coaching: {
      headline: "100% pushes — no variation in shot selection.",
      advice: "Step in and drive after your push.",
      mentalCue: "Push, Breathe, Step, Drive",
      finding: "100% of your shots were pushes.",
      evidence: "All shots recorded were pushes. Forehand 66.7%.",
      strategy: "After your push, step forward and prepare a forehand drive.",
      mentalIssue: "Hesitation after pushing, leading to a passive stance.",
      confidence: 0.75,
    },
  },
];

export function PatternRecognitionSection() {
  const [isVisible, setIsVisible] = useState(false);
  const [selected, setSelected] = useState(0);
=======
export function PatternRecognitionSection() {
  const [isVisible, setIsVisible] = useState(false);
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
<<<<<<< HEAD
        if (entry.isIntersecting && entry.intersectionRatio >= 0.3) setIsVisible(true);
      },
      { threshold: [0.3] }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  const m = MATCHES[selected];

=======
        if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
          setIsVisible(true);
        }
      },
      { threshold: [0.5] }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
  return (
    <section
      ref={sectionRef}
      id="pattern-recognition"
      style={{
<<<<<<< HEAD
        minHeight: "100vh",
        width: "100%",
        background: "#000000",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "50px 24px 70px 24px",
=======
        height: "100vh",
        width: "100%",
        background: "#050506",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 24px 80px 24px",
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
        position: "relative",
        overflow: "hidden",
      }}
    >
<<<<<<< HEAD
      {/* Subtle bg glow */}
=======
      {/* Background glow */}
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
<<<<<<< HEAD
            "radial-gradient(900px 400px at 30% 40%, rgba(255,255,255,0.02), transparent 60%)," +
            "radial-gradient(800px 500px at 70% 60%, rgba(255,255,255,0.01), transparent 60%)",
=======
            "radial-gradient(900px 400px at 30% 40%, rgba(255,100,50,0.06), transparent 60%)," +
            "radial-gradient(800px 500px at 70% 60%, rgba(50,150,255,0.06), transparent 60%)",
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "min(1400px, 96vw)", position: "relative" }}>
        {/* Header */}
<<<<<<< HEAD
        <div
          style={{
            textAlign: "center",
            marginBottom: 36,
            opacity: isVisible ? 1 : 0,
            transform: isVisible ? "translateY(0)" : "translateY(20px)",
            transition: "all 0.6s cubic-bezier(.2,.9,.2,1)",
          }}
        >
          <div style={{ fontSize: 44, fontWeight: 900, color: "#ffffff" }}>
            Your Winning Edge
          </div>
          <div style={{ marginTop: 8, fontSize: 16, color: "rgba(255,255,255,0.50)" }}>
            We find what's holding you back and fix it
          </div>
        </div>

        {/* Match selector cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 28 }}>
          {MATCHES.map((match, i) => (
            <button
              key={match.id}
              onClick={() => setSelected(i)}
              style={{
                all: "unset",
                cursor: "pointer",
                background: selected === i ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.03)",
                border: selected === i ? `1.5px solid ${WHITE}` : "1.5px solid rgba(255,255,255,0.10)",
                borderRadius: 14,
                padding: "16px 14px",
                textAlign: "center",
                transition: "all 0.25s ease",
                boxShadow: selected === i
                  ? `0 0 20px rgba(255,255,255,0.08)`
                  : "0 2px 8px rgba(0,0,0,0.20)",
                opacity: isVisible ? 1 : 0,
                transform: isVisible ? "translateY(0)" : "translateY(16px)",
                transitionDelay: `${i * 80}ms`,
              }}
            >
              <div style={{ fontSize: 13, fontWeight: 700, color: selected === i ? "#ffffff" : "rgba(255,255,255,0.70)", marginBottom: 3 }}>
                {match.label}
              </div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.45)" }}>
                {match.date} · {match.time}
              </div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", marginTop: 2 }}>
                {match.shots} shots · {match.rallies} rallies
              </div>
            </button>
          ))}
        </div>

        {/* Main content grid */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          {/* LEFT: Match Stats */}
          <div
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1.5px solid rgba(255,255,255,0.10)",
              borderRadius: 20,
              padding: 26,
              boxShadow: "0 4px 24px rgba(0,0,0,0.20)",
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? "translateY(0)" : "translateY(20px)",
              transition: "all 0.6s cubic-bezier(.2,.9,.2,1) 0.15s",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
              <div>
                <div style={{ fontSize: 17, fontWeight: 800, color: "#ffffff" }}>
                  Recording {m.id}
                </div>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.45)", marginTop: 2 }}>
                  {m.date} at {m.time} · {m.duration}
                </div>
              </div>
              <div
                style={{
                  fontSize: 10,
                  letterSpacing: "0.15em",
                  color: WHITE,
                  fontWeight: 800,
                  padding: "5px 12px",
                  borderRadius: 999,
                  background: "rgba(255,255,255,0.08)",
                  textTransform: "uppercase",
                }}
              >
                {m.style}
              </div>
            </div>

            {/* Stat grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, marginBottom: 16 }}>
              <StatCard label="Total Shots" value={String(m.shots)} accent />
              <StatCard label="Rallies" value={String(m.rallies)} accent />
              <StatCard label="Avg Rally" value={`${m.avgRally}s`} />
              <StatCard label="Forehand %" value={`${m.forehand}%`} accent />
              <StatCard label="Backhand %" value={`${m.backhand}%`} />
              <StatCard label="Aggression" value={m.aggression.toFixed(2)} accent={m.aggression < 0.35} warn={m.aggression < 0.35} />
            </div>

            {/* Metric bars */}
            <MetricBar label="Footwork Drop" value={m.footworkDrop} max={50} warn suffix="%" />
            <MetricBar label="Arm Speed" value={m.avgArmSpeed} max={12} suffix=" px/f" />
            <MetricBar label="Foot Speed" value={m.avgFootSpeed} max={8} suffix=" px/s" />

            {/* Confidence bar */}
            <div style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.40)", letterSpacing: "0.08em", fontWeight: 600 }}>
                AI CONFIDENCE
              </div>
              <div style={{ flex: 1, height: 4, borderRadius: 2, background: "rgba(255,255,255,0.10)", overflow: "hidden" }}>
                <div style={{ width: `${m.coaching.confidence * 100}%`, height: "100%", borderRadius: 2, background: WHITE, transition: "width 0.6s ease" }} />
              </div>
              <div style={{ fontSize: 13, fontWeight: 800, color: WHITE }}>
                {Math.round(m.coaching.confidence * 100)}%
              </div>
            </div>
          </div>

          {/* RIGHT: AI Coaching */}
          <div
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1.5px solid rgba(255,255,255,0.10)",
              borderRadius: 20,
              padding: 26,
              boxShadow: "0 4px 24px rgba(0,0,0,0.20)",
              display: "flex",
              flexDirection: "column",
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? "translateY(0)" : "translateY(20px)",
              transition: "all 0.6s cubic-bezier(.2,.9,.2,1) 0.25s",
            }}
          >
            {/* Coach header */}
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
              <div style={{
                width: 34, height: 34, borderRadius: 999,
                background: "linear-gradient(135deg, rgba(255,255,255,0.85), rgba(200,200,200,0.85))",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 14, fontWeight: 900, color: "#000",
              }}>
                AI
              </div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#ffffff" }}>Your AI Coach</div>
                <div style={{ fontSize: 9, color: "rgba(255,255,255,0.40)", letterSpacing: "0.1em" }}>
                  HERE TO MAKE YOU WIN
                </div>
              </div>
            </div>

            {/* Headline */}
            <div style={{ fontSize: 18, fontWeight: 800, color: "#ffffff", lineHeight: 1.35, marginBottom: 16 }}>
              "{m.coaching.headline}"
            </div>

            {/* Key finding */}
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 9, letterSpacing: "0.15em", color: "rgba(255,255,255,0.60)", fontWeight: 700, marginBottom: 5 }}>THE PROBLEM</div>
              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.70)", lineHeight: 1.5 }}>{m.coaching.finding}</div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.40)", marginTop: 3, fontStyle: "italic" }}>{m.coaching.evidence}</div>
            </div>

            {/* Strategy */}
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 9, letterSpacing: "0.15em", color: "rgba(255,255,255,0.60)", fontWeight: 700, marginBottom: 5 }}>YOUR FIX</div>
              <div style={{
                fontSize: 13, color: "#ffffff", lineHeight: 1.5,
                padding: "10px 14px", background: "rgba(255,255,255,0.08)",
                border: `1px solid rgba(255,255,255,0.15)`, borderRadius: 10,
              }}>
                {m.coaching.strategy}
              </div>
            </div>

            {/* Mental pattern */}
            <div style={{ marginBottom: 14 }}>
              <div style={{ fontSize: 9, letterSpacing: "0.15em", color: "rgba(255,255,255,0.40)", fontWeight: 700, marginBottom: 5 }}>MENTAL BLOCK</div>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.55)", lineHeight: 1.5 }}>{m.coaching.mentalIssue}</div>
            </div>

            {/* Mantra */}
            <div style={{ marginTop: "auto" }}>
              <div style={{
                padding: "12px 18px", borderRadius: 12,
                background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.10)",
                textAlign: "center",
              }}>
                <div style={{ fontSize: 9, letterSpacing: "0.2em", color: "rgba(255,255,255,0.35)", marginBottom: 5 }}>SAY THIS BEFORE SERVING</div>
                <div style={{ fontSize: 16, fontWeight: 900, color: WHITE, letterSpacing: "0.04em" }}>
                  "{m.coaching.mentalCue}"
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Summary bar */}
        <div style={{ marginTop: 20, display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
          <SummaryCard label="Matches Analyzed" value="4" sub="by our AI" />
          <SummaryCard label="Shots Tracked" value="44" sub="every single one" accent />
          <SummaryCard label="Your Weakness" value="Passive" sub="but we'll fix it" warn />
          <SummaryCard label="Improvement" value="29%" sub="footwork to fix" />
        </div>
      </div>
=======
        <div 
          className={isVisible ? "pr-header-enter" : ""}
          style={{ 
            textAlign: "center", 
            marginBottom: 50,
            opacity: isVisible ? 1 : 0,
            transform: isVisible ? "translateY(0)" : "translateY(20px)",
          }}
        >
          <div style={{ fontSize: 52, fontWeight: 900, color: "rgba(255,255,255,0.92)" }}>
            Pattern Recognition
          </div>
          <div style={{ marginTop: 12, fontSize: 18, color: "rgba(255,255,255,0.50)" }}>
            You played into his strength
          </div>

          {/* Compare Patterns Button */}
          <button
            style={{
              marginTop: 24,
              padding: "14px 32px",
              borderRadius: 999,
              background: "transparent",
              border: "1px solid rgba(255,255,255,0.20)",
              color: "rgba(255,255,255,0.85)",
              fontSize: 14,
              fontWeight: 600,
              letterSpacing: "0.08em",
              cursor: "pointer",
              transition: "all 0.3s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.08)";
              e.currentTarget.style.borderColor = "rgba(255,255,255,0.35)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.borderColor = "rgba(255,255,255,0.20)";
            }}
          >
            Compare Patterns
          </button>
        </div>

        {/* Court Comparison Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 32,
          }}
        >
          {/* Your Match - Left Court */}
          <CourtPattern
            title="Your Match"
            badge="DEFENSIVE"
            badgeColor="rgba(255,100,50,0.85)"
            isVisible={isVisible}
            delay={0}
            stats={[
              { label: "Footwork Quality", value: "58%", color: "rgba(255,100,50,0.95)" },
              { label: "Avg Rally Length", value: "18", color: "rgba(255,255,255,0.85)" },
              { label: "Attack Rate", value: "28%", color: "rgba(255,100,50,0.95)" },
            ]}
            ballPositions={[
              { x: 25, y: 30 }, // defensive left side
              { x: 32, y: 45 },
              { x: 28, y: 55 },
              { x: 35, y: 38 },
              { x: 30, y: 48 },
            ]}
          />

          {/* Opponent Pattern - Right Court */}
          <CourtPattern
            title="Opponent Pattern"
            badge="COUNTER-PUNCHER"
            badgeColor="rgba(50,200,150,0.85)"
            isVisible={isVisible}
            delay={200}
            stats={[
              { label: "Win Rate (Long Rallies)", value: "89%", color: "rgba(50,200,150,0.95)" },
              { label: "Avg Rally Length", value: "16", color: "rgba(255,255,255,0.85)" },
              { label: "Counter Success", value: "71%", color: "rgba(50,200,150,0.95)" },
            ]}
            ballPositions={[
              { x: 62, y: 32 }, // counter-puncher center-right
              { x: 68, y: 38 },
              { x: 65, y: 47 },
              { x: 70, y: 42 },
              { x: 63, y: 40 },
            ]}
          />
        </div>

        {/* Bottom hint - positioned at very bottom of viewport */}
        <div
          style={{
            position: "fixed",
            bottom: 20,
            left: 0,
            right: 0,
            textAlign: "center",
            fontSize: 12,
            letterSpacing: "0.35em",
            opacity: 0.42,
            userSelect: "none",
            color: "rgba(255,255,255,0.45)",
            zIndex: 100,
          }}
        >
          SCROLL FOR INSIGHTS ↓
        </div>
      </div>

      {/* CSS Animations */}
      <style>
        {`
          .pr-header-enter {
            animation: prHeaderEnter 600ms cubic-bezier(.2,.9,.2,1) forwards;
          }
          @keyframes prHeaderEnter {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }

          .pr-court-enter {
            animation: prCourtEnter 700ms cubic-bezier(.2,.9,.2,1) forwards;
          }
          @keyframes prCourtEnter {
            from { opacity: 0; transform: translateY(30px) scale(0.95); }
            to { opacity: 1; transform: translateY(0) scale(1); }
          }

          .pr-stat-enter {
            animation: prStatEnter 550ms cubic-bezier(.2,.9,.2,1) forwards;
          }
          @keyframes prStatEnter {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
          }

          @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
          }

          /* Ball rally animation - left court (Your Match) */
          @keyframes ballRally0 {
            0% { left: 30%; top: 60%; }
            25% { left: 42%; top: 35%; }  /* Arc up */
            50% { left: 70%; top: 60%; }  /* Land on opponent side */
            75% { left: 58%; top: 35%; }  /* Arc back up */
            100% { left: 30%; top: 60%; } /* Return to start */
          }

          /* Ball rally animation - right court (Opponent) */
          @keyframes ballRally200 {
            0% { left: 70%; top: 60%; }
            25% { left: 58%; top: 35%; }  /* Arc up */
            50% { left: 30%; top: 60%; }  /* Land on your side */
            75% { left: 42%; top: 35%; }  /* Arc back up */
            100% { left: 70%; top: 60%; } /* Return to start */
          }
        `}
      </style>
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
    </section>
  );
}

<<<<<<< HEAD
function StatCard({ label, value, accent, warn }: { label: string; value: string; accent?: boolean; warn?: boolean }) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)",
      borderRadius: 10, padding: "10px 8px", textAlign: "center",
    }}>
      <div style={{ fontSize: 20, fontWeight: 900, color: warn ? "rgba(220,80,60,0.85)" : accent ? WHITE : "#ffffff", marginBottom: 2 }}>{value}</div>
      <div style={{ fontSize: 9, color: "rgba(255,255,255,0.40)", letterSpacing: "0.05em", textTransform: "uppercase" }}>{label}</div>
    </div>
  );
}

function MetricBar({ label, value, max, suffix, warn }: { label: string; value: number; max: number; suffix: string; warn?: boolean }) {
  const pct = Math.min((value / max) * 100, 100);
  const color = warn ? "rgba(220,80,60,0.75)" : WHITE;
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <div style={{ fontSize: 11, color: "rgba(255,255,255,0.50)" }}>{label}</div>
        <div style={{ fontSize: 12, fontWeight: 700, color }}>{value}{suffix}</div>
      </div>
      <div style={{ height: 4, borderRadius: 2, background: "rgba(255,255,255,0.10)", overflow: "hidden" }}>
        <div style={{ width: `${pct}%`, height: "100%", borderRadius: 2, background: color, transition: "width 0.6s ease" }} />
      </div>
    </div>
  );
}

function SummaryCard({ label, value, sub, accent, warn }: { label: string; value: string; sub: string; accent?: boolean; warn?: boolean }) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.03)", border: "1.5px solid rgba(255,255,255,0.10)",
      borderRadius: 14, padding: "16px 12px", textAlign: "center",
      boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
    }}>
      <div style={{ fontSize: 9, color: "rgba(255,255,255,0.40)", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 5 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 900, color: warn ? "rgba(220,80,60,0.85)" : accent ? WHITE : "#ffffff" }}>{value}</div>
      <div style={{ fontSize: 10, color: "rgba(255,255,255,0.35)", marginTop: 3 }}>{sub}</div>
    </div>
  );
}
=======
// Court Pattern Component
function CourtPattern({
  title,
  badge,
  badgeColor,
  stats,
  ballPositions,
  isVisible,
  delay,
}: {
  title: string;
  badge: string;
  badgeColor: string;
  stats: Array<{ label: string; value: string; color: string }>;
  ballPositions: Array<{ x: number; y: number }>;
  isVisible: boolean;
  delay: number;
}) {
  return (
    <div
      className={isVisible ? "pr-court-enter" : ""}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? "translateY(0) scale(1)" : "translateY(30px) scale(0.95)",
        animationDelay: `${delay}ms`,
      }}
    >
      {/* Title + Badge */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 16, color: "rgba(255,255,255,0.50)", marginBottom: 8 }}>
          {title}
        </div>
        <div
          style={{
            display: "inline-block",
            fontSize: 11,
            letterSpacing: "0.15em",
            color: badgeColor,
            fontWeight: 700,
          }}
        >
          {badge}
        </div>
      </div>

      {/* Court Visualization */}
      <div
        style={{
          background: "rgba(255,255,255,0.03)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 20,
          padding: 28,
          boxShadow: "0 30px 80px rgba(0,0,0,0.60)",
          height: 380,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Court Background */}
        <div
          style={{
            position: "absolute",
            inset: 28,
            background: "linear-gradient(180deg, rgba(20,30,50,0.4) 0%, rgba(10,15,25,0.6) 100%)",
            borderRadius: 12,
            border: "2px solid rgba(100,120,160,0.20)",
          }}
        >
          {/* Net line (horizontal center) */}
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: "50%",
              height: 2,
              background: "rgba(200,210,230,0.25)",
              transform: "translateY(-50%)",
            }}
          />

          {/* Court lines (perspective effect) */}
          <svg
            width="100%"
            height="100%"
            style={{ position: "absolute", inset: 0 }}
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
          >
            {/* Outer court boundary */}
            <path
              d="M 10,15 L 90,15 L 85,85 L 15,85 Z"
              fill="none"
              stroke="rgba(200,210,230,0.15)"
              strokeWidth="0.3"
            />

            {/* Service boxes */}
            <path
              d="M 30,15 L 70,15 L 68,50 L 32,50 Z"
              fill="none"
              stroke="rgba(200,210,230,0.12)"
              strokeWidth="0.3"
            />
            <path
              d="M 32,50 L 68,50 L 70,85 L 30,85 Z"
              fill="none"
              stroke="rgba(200,210,230,0.12)"
              strokeWidth="0.3"
            />
          </svg>

          {/* Single animated ball moving back and forth */}
          {isVisible && (
            <div
              style={{
                position: "absolute",
                width: 14,
                height: 14,
                borderRadius: 999,
                background: "rgba(255,140,60,0.95)",
                boxShadow: "0 0 24px rgba(255,140,60,0.70), 0 0 48px rgba(255,140,60,0.35)",
                transform: "translate(-50%, -50%)",
                zIndex: 10,
                opacity: 0,
                animation: `fadeIn 400ms ease-out forwards ${500 + delay}ms, ballRally${delay} 3s ease-in-out ${900 + delay}ms infinite`,
              }}
            />
          )}

          {/* Player silhouette (bottom center) */}
          <div
            style={{
              position: "absolute",
              bottom: 20,
              left: "50%",
              transform: "translateX(-50%)",
              width: 40,
              height: 50,
              background: "rgba(150,160,180,0.30)",
              borderRadius: "50% 50% 40% 40%",
            }}
          />
        </div>
      </div>

      {/* Stats Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 12,
          marginTop: 20,
        }}
      >
        {stats.map((stat, i) => (
          <div
            key={i}
            className={isVisible ? "pr-stat-enter" : ""}
            style={{
              background: "rgba(255,255,255,0.02)",
              border: "1px solid rgba(255,255,255,0.06)",
              borderRadius: 12,
              padding: "14px 12px",
              textAlign: "center",
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? "translateY(0)" : "translateY(12px)",
              animationDelay: `${600 + delay + i * 100}ms`,
            }}
          >
            <div
              style={{
                fontSize: 22,
                fontWeight: 900,
                color: stat.color,
                marginBottom: 4,
              }}
            >
              {stat.value}
            </div>
            <div
              style={{
                fontSize: 10,
                color: "rgba(255,255,255,0.40)",
                letterSpacing: "0.05em",
              }}
            >
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      {/* Ball pulse animation removed from here since it's now in parent */}
    </div>
  );
}
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
