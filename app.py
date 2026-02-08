import streamlit as st

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Break Point AI Coach",
    page_icon="🏓",
    layout="centered",  # Centered = more focused
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------
# Clean, Minimal CSS
# -------------------------------------------------------------
st.markdown("""
<style>
    /* --- Global --- */
    .stApp {
        background: linear-gradient(160deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* --- Cards --- */
    .card {
        background: white;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
    }
    
    .card-header {
        font-size: 0.85rem;
        font-weight: 600;
        color: #868e96;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }
    
    /* --- Snapshot Stats --- */
    .snapshot-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 16px;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #212529;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #868e96;
        margin-top: 4px;
    }
    
    /* --- Findings --- */
    .finding {
        display: flex;
        align-items: flex-start;
        padding: 16px 0;
        border-bottom: 1px solid #f1f3f4;
    }
    
    .finding:last-child {
        border-bottom: none;
        padding-bottom: 0;
    }
    
    .finding-icon {
        font-size: 1.5rem;
        margin-right: 16px;
        flex-shrink: 0;
    }
    
    .finding-text {
        font-size: 1.1rem;
        color: #212529;
        line-height: 1.5;
    }
    
    /* --- Actions --- */
    .action {
        background: #e7f5ff;
        border-left: 4px solid #339af0;
        padding: 14px 18px;
        margin-bottom: 12px;
        border-radius: 0 8px 8px 0;
        color: #1c7ed6;
        font-size: 1rem;
    }
    
    .action:last-child {
        margin-bottom: 0;
    }
    
    /* --- Mental --- */
    .mental-card {
        background: linear-gradient(135deg, #fff3bf 0%, #ffe066 100%);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 20px;
        border: 1px solid #ffd43b;
    }
    
    .mental-insight {
        font-size: 1.15rem;
        color: #664d03;
        font-style: italic;
        margin-bottom: 16px;
    }
    
    .mental-fix {
        font-size: 1rem;
        color: #664d03;
        background: rgba(255,255,255,0.5);
        padding: 12px 16px;
        border-radius: 8px;
    }
    
    /* --- Confidence --- */
    .confidence-bar {
        background: #e9ecef;
        border-radius: 100px;
        height: 12px;
        margin-top: 12px;
        overflow: hidden;
    }
    
    .confidence-fill {
        background: linear-gradient(90deg, #51cf66 0%, #40c057 100%);
        height: 100%;
        border-radius: 100px;
    }
    
    .confidence-text {
        display: flex;
        justify-content: space-between;
        margin-top: 8px;
        font-size: 0.85rem;
        color: #868e96;
    }
    
    /* --- Title --- */
    .main-title {
        text-align: center;
        margin-bottom: 32px;
    }
    
    .main-title h1 {
        font-size: 2rem;
        font-weight: 800;
        color: #212529;
        margin: 0;
    }
    
    .main-title p {
        color: #868e96;
        font-size: 1rem;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Data (extracted from LLM response)
# -------------------------------------------------------------
data = {
    "snapshot": {
        "shots": 6,
        "rallies": 3,
        "style": "Passive / Push-heavy",
        "pressure": "Footwork drops late"
    },
    "findings": [
        {"icon": "🎯", "text": "You pushed 100% of returns, giving the opponent control of every rally."},
        {"icon": "🦶", "text": "Your footwork slowed 35% after the first rally — fatigue or hesitation."},
        {"icon": "👁️", "text": "Opponent stayed wide on backhand and waited for your errors."}
    ],
    "actions": [
        "Attack the far-left zone early — opponent recovers slow there.",
        "Use one fast forehand per rally to break rhythm.",
        "Reset footwork after long rallies (you lose speed after 5–6 seconds)."
    ],
    "mental": {
        "insight": "You play safe after losing a rally instead of resetting aggressively.",
        "fix": "Before the next serve, take one deep breath and step forward intentionally."
    },
    "confidence": 82
}

# -------------------------------------------------------------
# Main UI
# -------------------------------------------------------------
def main():
    # Title
    st.markdown("""
    <div class="main-title">
        <h1>🏓 Break Point AI Coach</h1>
        <p>Powered by Snowflake Cortex & Kimi K2</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════
    # 1️⃣ MATCH SNAPSHOT
    # ═══════════════════════════════════════════════════════════
    st.markdown(f"""
    <div class="card">
        <div class="card-header">📋 What happened in this clip</div>
        <div class="snapshot-grid">
            <div class="stat-item">
                <div class="stat-value">{data['snapshot']['shots']}</div>
                <div class="stat-label">Shots Analyzed</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{data['snapshot']['rallies']}</div>
                <div class="stat-label">Rallies</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="font-size: 1.1rem;">{data['snapshot']['style']}</div>
                <div class="stat-label">Style Detected</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="font-size: 1.1rem;">{data['snapshot']['pressure']}</div>
                <div class="stat-label">Pressure Behavior</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════
    # 2️⃣ 3 KEY FINDINGS
    # ═══════════════════════════════════════════════════════════
    f1, f2, f3 = data['findings']
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">🔍 3 Key Findings</div>
        <div class="finding">
            <span class="finding-icon">{f1['icon']}</span>
            <span class="finding-text">{f1['text']}</span>
        </div>
        <div class="finding">
            <span class="finding-icon">{f2['icon']}</span>
            <span class="finding-text">{f2['text']}</span>
        </div>
        <div class="finding">
            <span class="finding-icon">{f3['icon']}</span>
            <span class="finding-text">{f3['text']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════
    # 3️⃣ WHAT TO DO NEXT TIME
    # ═══════════════════════════════════════════════════════════
    a1, a2, a3 = data['actions']
    
    st.markdown(f"""
    <div class="card">
        <div class="card-header">🎯 If you play this opponent again</div>
        <div class="action"><strong>1.</strong> {a1}</div>
        <div class="action"><strong>2.</strong> {a2}</div>
        <div class="action"><strong>3.</strong> {a3}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════
    # 4️⃣ MENTAL GAME
    # ═══════════════════════════════════════════════════════════
    st.markdown(f"""
    <div class="mental-card">
        <div class="card-header" style="color: #664d03;">🧠 Mental Pattern Detected</div>
        <div class="mental-insight">"{data['mental']['insight']}"</div>
        <div class="mental-fix">
            <strong>Try this:</strong> {data['mental']['fix']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════
    # 5️⃣ CONFIDENCE SCORE
    # ═══════════════════════════════════════════════════════════
    st.markdown(f"""
    <div class="card">
        <div class="card-header">📊 Decision Confidence</div>
        <div class="confidence-bar">
            <div class="confidence-fill" style="width: {data['confidence']}%;"></div>
        </div>
        <div class="confidence-text">
            <span>Based on: movement + shot placement + opponent response</span>
            <span><strong>{data['confidence']}%</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; color: #adb5bd; font-size: 0.85rem; margin-top: 32px;">
        Break Point AI • Snowflake Hackathon 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
