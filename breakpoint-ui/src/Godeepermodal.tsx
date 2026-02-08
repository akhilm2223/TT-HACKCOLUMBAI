import { useState } from 'react'
import { PricingModal } from './PricingModal'

const WHITE = "rgba(255,255,255,0.95)";

export function GoDeeperModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [showPricing, setShowPricing] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  if (!isOpen) return null;

  const handleUnlockClick = () => {
    // Open pricing modal instead of direct checkout
    setShowPricing(true)
  }

  const handlePlanSelected = async (priceId: string, planName: string) => {
    console.log('🔵 Plan selected:', planName, priceId);
    setShowPricing(false)
    setIsProcessing(true)

    try {
      let customerId = localStorage.getItem('breakpoint_customer_id');
      if (!customerId) {
        customerId = 'user_' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('breakpoint_customer_id', customerId);
      }

      const response = await fetch('http://localhost:3001/api/flowglad/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-customer-id': customerId,
        },
        body: JSON.stringify({
          priceId: priceId, // Use priceId directly
          successUrl: window.location.origin + '?payment=success',
          cancelUrl: window.location.origin + '?payment=cancelled',
        }),
      });

      if (!response.ok) {
        throw new Error(`Checkout failed: ${response.status}`);
      }

      const data = await response.json();

      if (data.url) {
        console.log('✅ Opening checkout:', data.url);
        window.open(data.url, '_blank');
        onClose();
      }
    } catch (error) {
      console.error('❌ Checkout error:', error);
      alert('Checkout failed: ' + error.message);
      setIsProcessing(false);
    }
  }

  return (
    <>
      <div
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.85)",
          backdropFilter: "blur(12px)",
          zIndex: 9999,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
          animation: "fadeIn 0.3s ease-out",
        }}
        onClick={onClose}
      >
        <div
          onClick={(e) => e.stopPropagation()}
          style={{
            width: "min(860px, 95vw)",
            background: "#111111",
            borderRadius: 22,
            padding: 55,
            position: "relative",
            boxShadow: "0 30px 80px rgba(0,0,0,0.40)",
            border: "1.5px solid rgba(255,255,255,0.10)",
            animation: "slideUp 0.4s cubic-bezier(.2,.9,.2,1)",
          }}
        >
          <button
            onClick={onClose}
            style={{
              position: "absolute", top: 22, right: 22,
              width: 38, height: 38, borderRadius: 999,
              background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.12)",
              color: "rgba(255,255,255,0.50)", fontSize: 18, cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.10)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(255,255,255,0.05)"; }}
          >
            ✕
          </button>

          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 42, fontWeight: 900, color: "#ffffff", marginBottom: 14 }}>
              Level Up
            </div>
            <div style={{ fontSize: 16, color: "rgba(255,255,255,0.50)", marginBottom: 44 }}>
              Get the full breakdown and dominate your next match
            </div>

            <div style={{
              background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)",
              borderRadius: 18, padding: 70, marginBottom: 36, position: "relative", overflow: "hidden",
            }}>
              <div style={{
                position: "absolute", inset: 0,
                background: "radial-gradient(circle at center, rgba(0,0,0,0.3), rgba(0,0,0,0.7) 50%, rgba(0,0,0,0.9) 100%)",
                backdropFilter: "blur(8px)",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <div style={{
                  width: 90, height: 90, borderRadius: 999,
                  background: "rgba(255,255,255,0.05)", border: "2px solid rgba(255,255,255,0.15)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 40, color: "rgba(255,255,255,0.40)",
                }}>
                  🔒
                </div>
              </div>
              <div style={{ opacity: 0.25, filter: "blur(3px)" }}>
                <div style={{ fontSize: 13, color: "rgba(255,255,255,0.50)", marginBottom: 10 }}>Rally-by-Rally Breakdown</div>
                <div style={{ height: 100, background: "rgba(255,255,255,0.05)", borderRadius: 10, marginBottom: 16 }} />
                <div style={{ fontSize: 13, color: "rgba(255,255,255,0.50)", marginBottom: 10 }}>Mental State Analysis</div>
                <div style={{ height: 70, background: "rgba(255,255,255,0.05)", borderRadius: 10 }} />
              </div>
            </div>

            <button 
              onClick={handleUnlockClick}
              disabled={isProcessing}
              style={{
                width: "100%", maxWidth: 380, padding: "16px 44px", borderRadius: 999,
                background: isProcessing ? "rgba(100,100,100,0.40)" : WHITE, 
                border: "none", 
                color: "#000",
                fontSize: 15, fontWeight: 700, letterSpacing: "0.05em", 
                cursor: isProcessing ? "wait" : "pointer",
                transition: "all 0.3s ease", 
                boxShadow: "0 6px 20px rgba(255,255,255,0.15)",
                marginBottom: 18,
                opacity: isProcessing ? 0.6 : 1,
              }}
              onMouseEnter={(e) => { 
                if (!isProcessing) e.currentTarget.style.transform = "translateY(-2px)"; 
              }}
              onMouseLeave={(e) => { 
                if (!isProcessing) e.currentTarget.style.transform = "translateY(0)"; 
              }}
            >
              {isProcessing ? "Opening Checkout..." : "Unlock Your Edge"}
            </button>

            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", letterSpacing: "0.08em" }}>
              Powered by Flowglad
            </div>
          </div>

          <style>{`
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            @keyframes slideUp { from { opacity: 0; transform: translateY(30px) scale(0.96); } to { opacity: 1; transform: translateY(0) scale(1); } }
          `}</style>
        </div>
      </div>

      {/* Pricing Modal */}
      <PricingModal
        isOpen={showPricing}
        onClose={() => setShowPricing(false)}
        onSelectPlan={handlePlanSelected}
      />
    </>
  );
}