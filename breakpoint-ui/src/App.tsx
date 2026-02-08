import { useEffect, useRef, useState } from "react";
import { Hero3D } from "./Hero3D";
import { BreakdownSection } from "./BreakdownSection";
import { PatternRecognitionSection } from "./PatternRecognitionSection";
import { ThinkingSection } from "./ThinkingSection";
import { CorrectionSection } from "./CorrectionSection";
import { UploadSection } from "./UploadSection";

export default function App() {
  const scrollRootRef = useRef<HTMLDivElement | null>(null);
  const breakdownRef = useRef<HTMLElement | null>(null);

  const [activeRally, setActiveRally] = useState<number | null>(null);

  const goToBreakdown = () => {
    setActiveRally(null); // <- important: not red until we land
    breakdownRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  // ✅ Trigger highlight when breakdown is actually in view
  useEffect(() => {
    const target = breakdownRef.current;
    if (!target) return;

    const root = scrollRootRef.current; // our scroll container

    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.7) {
          setActiveRally(7);
        } else {
          setActiveRally(null);
        }
      },
      {
        root,              // important when using a custom scroll container
        threshold: [0.7],  // means "landed"
      }
    );

    obs.observe(target);
    return () => obs.disconnect();
  }, []);

  return (
    <div
      ref={scrollRootRef}
      style={{
        height: "100vh",
        width: "100%",
        overflowY: "auto",
        scrollSnapType: "y mandatory",
      }}
    >
      <div style={{ scrollSnapAlign: "start" }}>
        <Hero3D onNext={goToBreakdown} />
      </div>

      <div style={{ scrollSnapAlign: "start" }}>
        <section ref={(el) => (breakdownRef.current = el)} style={{ height: "100vh" }}>
          <BreakdownSection activeRally={activeRally} />
        </section>
      </div>

      {/* Page 3: Pattern Recognition comparison */}
      <div style={{ scrollSnapAlign: "start" }}>
        <PatternRecognitionSection />
      </div>

      {/* Page 4: The Thinking - AI reasoning engine */}
      <div style={{ scrollSnapAlign: "start" }}>
        <ThinkingSection />
      </div>

      {/* Page 5: The Correction - Voice feedback */}
      <div style={{ scrollSnapAlign: "start" }}>
        <CorrectionSection />
      </div>

      {/* Page 6: Upload - Get your own analysis */}
      <div style={{ scrollSnapAlign: "start" }}>
        <UploadSection />
      </div>
    </div>
  );
}