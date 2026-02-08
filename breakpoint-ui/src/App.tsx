import { useRef } from "react";
import { Hero3D } from "./Hero3D";
import { VideoGallerySection } from "./VideoGallerySection";
import { PatternRecognitionSection } from "./Patternrecognitionsection";
import { ThinkingSection } from "./Thinkingsection";
import { CorrectionSection } from "./Correctionsection";
import { UploadSection } from "./Uploadsection";


export default function App() {
  const scrollRootRef = useRef<HTMLDivElement | null>(null);

  const goToVideoGallery = () => {
    scrollRootRef.current?.querySelector('[data-section="videos"]')?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

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
        <Hero3D onNext={goToVideoGallery} />
      </div>

      {/* Page 2: See Past Video Analysis */}
      <div style={{ scrollSnapAlign: "start" }} data-section="videos">
        <VideoGallerySection />
      </div>

      {/* Page 3: Pattern Recognition - Stats & Improvement */}
      <div style={{ scrollSnapAlign: "start" }} data-section="pattern">
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
