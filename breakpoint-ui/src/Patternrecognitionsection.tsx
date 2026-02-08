import { useEffect, useRef, useState } from "react";

export function PatternRecognitionSection() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
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

  return (
    <section
      ref={sectionRef}
      id="pattern-recognition"
      style={{
        height: "100vh",
        width: "100%",
        background: "#050506",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 24px 80px 24px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Background glow */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(900px 400px at 30% 40%, rgba(255,100,50,0.06), transparent 60%)," +
            "radial-gradient(800px 500px at 70% 60%, rgba(50,150,255,0.06), transparent 60%)",
          pointerEvents: "none",
        }}
      />

      <div style={{ width: "min(1400px, 96vw)", position: "relative" }}>
        {/* Header */}
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
    </section>
  );
}

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