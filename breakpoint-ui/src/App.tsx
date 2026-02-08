import { useRef, useEffect, useState } from "react";
import { Hero3D } from "./Hero3D";
import { VideoGallerySection } from "./VideoGallerySection";
import { PatternRecognitionSection } from "./Patternrecognitionsection";
import { ThinkingSection } from "./Thinkingsection";
import { CorrectionSection } from "./Correctionsection";
import { UploadSection } from "./Uploadsection";

export default function App() {
  const scrollRootRef = useRef<HTMLDivElement | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);

  // Check for payment success
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('payment') === 'success') {
      setShowSuccess(true);
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
      // Hide after 5 seconds
      setTimeout(() => setShowSuccess(false), 5000);
    }
  }, []);

  const goToVideoGallery = () => {
    scrollRootRef.current?.querySelector('[data-section="videos"]')?.scrollIntoView({ 
      behavior: "smooth", 
      block: "start" 
    });
  };

  return (
    <>
      {/* Success Notification */}
      {showSuccess && (
        <div
          style={{
            position: 'fixed',
            top: 24,
            right: 24,
            zIndex: 99999,
            background: 'linear-gradient(135deg, rgba(50,220,120,0.95), rgba(40,180,100,0.95))',
            padding: '20px 32px',
            borderRadius: 16,
            boxShadow: '0 12px 40px rgba(50,220,120,0.40)',
            color: 'white',
            fontSize: 16,
            fontWeight: 700,
            animation: 'slideInRight 0.4s ease-out',
          }}
        >
          ✅ Payment Successful! You now have Pro access.
        </div>
      )}

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

        <div style={{ scrollSnapAlign: "start" }} data-section="videos">
          <VideoGallerySection />
        </div>

        <div style={{ scrollSnapAlign: "start" }} data-section="pattern">
          <PatternRecognitionSection />
        </div>

        <div style={{ scrollSnapAlign: "start" }}>
          <ThinkingSection />
        </div>

        <div style={{ scrollSnapAlign: "start" }}>
          <CorrectionSection />
        </div>

        <div style={{ scrollSnapAlign: "start" }}>
          <UploadSection />
        </div>
      </div>

      {/* Success Animation */}
      <style>
        {`
          @keyframes slideInRight {
            from {
              opacity: 0;
              transform: translateX(100px);
            }
            to {
              opacity: 1;
              transform: translateX(0);
            }
          }
        `}
      </style>
    </>
  );
}