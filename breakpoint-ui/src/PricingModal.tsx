import { useState, useEffect } from 'react'

interface PricingPlan {
  id: string
  name: string
  slug: string
  price: number
  interval: string
  description: string
  features: string[]
  popular?: boolean
}

export function PricingModal({ 
  isOpen, 
  onClose, 
  onSelectPlan 
}: { 
  isOpen: boolean
  onClose: () => void
  onSelectPlan: (priceId: string, planName: string) => void
}) {
  const [plans, setPlans] = useState<PricingPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      fetchPlans()
    }
  }, [isOpen])

  const fetchPlans = async () => {
    try {
      setLoading(true)
      
      // Fetch plans from your backend
      const response = await fetch('http://localhost:3001/api/flowglad/plans')
      const data = await response.json()
      
      setPlans(data.plans || [])
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch plans:', error)
      setLoading(false)
    }
  }

  const handleSelectPlan = (priceId: string, planName: string) => {
    setSelectedPlan(priceId)
    // Small delay for visual feedback
    setTimeout(() => {
      onSelectPlan(priceId, planName)
    }, 300)
  }

  if (!isOpen) return null

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.90)',
        backdropFilter: 'blur(12px)',
        zIndex: 99999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
        animation: 'fadeIn 0.3s ease-out',
        overflowY: 'auto',
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 'min(1200px, 95vw)',
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          borderRadius: 24,
          padding: '60px 40px',
          position: 'relative',
          animation: 'slideUp 0.4s cubic-bezier(.2,.9,.2,1)',
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            width: 40,
            height: 40,
            borderRadius: 999,
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.10)',
            color: 'rgba(255,255,255,0.60)',
            fontSize: 20,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          ✕
        </button>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 50 }}>
          <h2 style={{ 
            fontSize: 48, 
            fontWeight: 900, 
            background: 'linear-gradient(135deg, #fff 0%, #a78bfa 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: 16 
          }}>
            Choose Your Analysis Level
          </h2>
          <p style={{ fontSize: 18, color: 'rgba(255,255,255,0.60)' }}>
            Pricing based on AI reasoning depth. The more you need the AI to think and remember, the more powerful your insights.
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>⏳</div>
            <div style={{ fontSize: 18, color: 'rgba(255,255,255,0.60)' }}>
              Loading pricing plans...
            </div>
          </div>
        )}

        {/* Plans Grid */}
        {!loading && plans.length > 0 && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
            gap: 24,
            marginBottom: 40 
          }}>
            {plans.map((plan) => (
              <PricingCard
                key={plan.id}
                plan={plan}
                isSelected={selectedPlan === plan.id}
                onSelect={() => handleSelectPlan(plan.id, plan.name)}
              />
            ))}
          </div>
        )}

        {/* No Plans */}
        {!loading && plans.length === 0 && (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📋</div>
            <div style={{ fontSize: 18, color: 'rgba(255,255,255,0.60)' }}>
              No pricing plans available. Please contact support.
            </div>
          </div>
        )}

        <style>{`
          @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
          @keyframes slideUp { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }
        `}</style>
      </div>
    </div>
  )
}

function PricingCard({ 
  plan, 
  isSelected, 
  onSelect 
}: { 
  plan: PricingPlan
  isSelected: boolean
  onSelect: () => void
}) {
  return (
    <div
      style={{
        background: plan.popular 
          ? 'linear-gradient(135deg, rgba(167,139,250,0.15) 0%, rgba(139,92,246,0.10) 100%)'
          : 'rgba(255,255,255,0.03)',
        border: plan.popular 
          ? '2px solid rgba(167,139,250,0.40)' 
          : '2px solid rgba(255,255,255,0.10)',
        borderRadius: 20,
        padding: 32,
        position: 'relative',
        transition: 'all 0.3s ease',
        cursor: 'pointer',
        transform: isSelected ? 'scale(1.02)' : 'scale(1)',
      }}
      onClick={onSelect}
      onMouseEnter={(e) => {
        if (!isSelected) {
          e.currentTarget.style.borderColor = 'rgba(167,139,250,0.30)'
          e.currentTarget.style.transform = 'scale(1.02)'
        }
      }}
      onMouseLeave={(e) => {
        if (!isSelected) {
          e.currentTarget.style.borderColor = plan.popular ? 'rgba(167,139,250,0.40)' : 'rgba(255,255,255,0.10)'
          e.currentTarget.style.transform = 'scale(1)'
        }
      }}
    >
      {/* Popular Badge */}
      {plan.popular && (
        <div style={{
          position: 'absolute',
          top: -12,
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)',
          padding: '6px 16px',
          borderRadius: 999,
          fontSize: 11,
          fontWeight: 700,
          color: '#fff',
          letterSpacing: '0.05em',
        }}>
          MOST POPULAR
        </div>
      )}

      {/* Plan Name */}
      <h3 style={{ fontSize: 28, fontWeight: 900, color: '#fff', marginBottom: 8 }}>
        {plan.name}
      </h3>

      {/* Description */}
      <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.50)', marginBottom: 20 }}>
        {plan.description}
      </p>

      {/* Price */}
      <div style={{ marginBottom: 24 }}>
        <span style={{ fontSize: 42, fontWeight: 900, color: '#fff' }}>
          ${plan.price}
        </span>
        <span style={{ fontSize: 18, color: 'rgba(255,255,255,0.50)' }}>
          /{plan.interval}
        </span>
      </div>

      {/* Subscribe Button */}
      <button
        style={{
          width: '100%',
          padding: '14px 24px',
          borderRadius: 999,
          background: isSelected 
            ? 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)'
            : plan.popular
              ? 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)'
              : 'rgba(255,255,255,0.10)',
          border: 'none',
          color: '#fff',
          fontSize: 16,
          fontWeight: 700,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          marginBottom: 24,
        }}
      >
        {isSelected ? '✓ Selected' : 'Subscribe Now'}
      </button>

      {/* Features */}
      <div>
        <div style={{ fontSize: 12, fontWeight: 700, color: 'rgba(255,255,255,0.40)', marginBottom: 12, letterSpacing: '0.05em' }}>
          FEATURES
        </div>
        {plan.features.map((feature, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ color: '#10b981', marginRight: 8, fontSize: 18 }}>✓</span>
            <span style={{ fontSize: 14, color: 'rgba(255,255,255,0.70)' }}>{feature}</span>
          </div>
        ))}
      </div>
    </div>
  )
}