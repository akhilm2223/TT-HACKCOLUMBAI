import streamlit as st
import json
import os
import sys
import time

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import backend modules
try:
    from HH.stats_engine import StatsEngine
    from modules.dedalus_coach import DedalusCoach
except ImportError as e:
    st.error(f"Module Import Error: {e}. Please ensure you are running from the project root.")
    st.stop()

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Break Point AI Coach",
    page_icon="🏓",
    layout="wide",  # Wide layout for dashboard feel
    initial_sidebar_state="expanded",
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

    /* --- Chat --- */
    .chat-user {
        background-color: #e7f5ff;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .chat-bot {
        background-color: #f1f3f4;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# App State Intitialization
# -------------------------------------------------------------

if 'coach' not in st.session_state:
    st.session_state.coach = DedalusCoach()

if 'stats_engine' not in st.session_state:
    st.session_state.stats_engine = StatsEngine()

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'match_stats' not in st.session_state:
    st.session_state.match_stats = None


# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------

def process_last_match():
    """Load HH/output.json, process with StatsEngine, and Analyze with Dedalus."""
    json_path = os.path.join(current_dir, "HH", "output.json")
    
    if not os.path.exists(json_path):
        st.error("No match data found! Run 'main.py' first to generate HH/output.json")
        return None

    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        # Step 1: Load Raw JSON
        status_text.text("📂 Loading raw tracking data...")
        with open(json_path, 'r') as f:
            raw_data = json.load(f)
        progress_bar.progress(25)
        
        # Step 2: Enrich with StatsEngine
        status_text.text("⚙️ Calculating biomechanics & physics...")
        stats = st.session_state.stats_engine.process_match(raw_data)
        st.session_state.match_stats = stats # Save for chat context
        progress_bar.progress(50)
        
        # Step 3: Analyze with Dedalus Agent
        status_text.text("🤖 Dedalus Agent analyzing patterns...")
        json_response_str = st.session_state.coach.analyze_match(stats)
        progress_bar.progress(90)
        
        # Step 4: Parse & Store
        status_text.text("✨ Finalizing report...")
        result = json.loads(json_response_str)
        st.session_state.analysis_result = result
        progress_bar.progress(100)
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
    except json.JSONDecodeError:
        st.error("Error: Dedalus output was not valid JSON. Please try again.")
        # Fallback to manual parsing if needed, but for now show error
    except Exception as e:
        st.error(f"Analysis Failed: {str(e)}")


# -------------------------------------------------------------
# Main UI
# -------------------------------------------------------------
def main():
    # Sidebar Navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to:", ["Match Analysis", "Chat with Coach", "Sponsor Track"])
        
        st.divider()
        st.caption("System Status")
        if st.session_state.match_stats:
            st.success("Match Data Loaded ✅")
        else:
            st.warning("No Data Loaded ❌")

    # TITLE
    st.markdown("""
    <div class="main-title">
        <h1>🏓 Break Point AI Coach</h1>
        <p>Powered by Dedalus Labs Multi-Agent System & Snowflake Cortex</p>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════
    # PAGE: SPONSOR TRACK
    # ═══════════════════════════════════════════════════════════
    if page == "Sponsor Track":
        st.markdown("### 🏆 Sponsor Track Verification")
        st.info("Teams on the Sponsor Track get priority access to advanced coaching features.")
        
        # Initialize FlowGlad Client
        try:
            from modules.flowglad_client import FlowGladClient
            client = FlowGladClient()
            
            # Helper to check status
            def check_status():
                if 'user_org_id' in st.session_state and st.session_state.user_org_id:
                    with st.spinner("Verifying Org Status..."):
                        customer = client.get_customer(st.session_state.user_org_id)
                        if customer:
                            st.session_state.flowglad_customer = customer
                            # Check subscription
                            sub = client.get_subscription_status(customer['id'])
                            if sub:
                                st.session_state.is_sponsor = True
                                st.session_state.subscription = sub
                            else:
                                st.session_state.is_sponsor = False
                        else:
                             st.session_state.flowglad_customer = None

            # Input for Org ID
            org_id = st.text_input("Enter your Organization ID", 
                                 value=st.session_state.get('user_org_id', ''),
                                 help="This is the ID you used when registering your team.")
            
            if st.button("Verify Status"):
                st.session_state.user_org_id = org_id
                check_status()
                st.rerun()

            # Display Status
            if 'flowglad_customer' in st.session_state:
                cust = st.session_state.flowglad_customer
                if cust:
                    st.success(f"Organization Found: **{cust.get('name', 'Unknown')}**")
                    
                    if st.session_state.get('is_sponsor'):
                        st.markdown("""
                        <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                            <h4>✅ VERIFIED SPONSOR</h4>
                            <p>You have full access to Pro features.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Portal Link
                        if st.button("Manage Billing & Subscription"):
                            portal_url = client.get_portal_url(cust['id'])
                            if portal_url:
                                st.markdown(f"[**Click here to open Billing Portal**]({portal_url})")
                            else:
                                st.error("Could not retrieve portal URL.")
                                
                    else:
                        st.warning("⚠️ Organization found, but no active 'Sponsor' subscription detected.")
                        st.markdown("To qualify, please subscribe to the Sponsor Plan.")
                        
                        if st.button("Subscribe to Sponsor Track ($0/test)"):
                            price_id = os.getenv("FLOWGLAD_PRICE_ID")
                            if not price_id:
                                st.error("Configuration Error: FLOWGLAD_PRICE_ID not set in .env")
                            else:
                                session = client.create_checkout_session(
                                    customer_id=cust['id'],
                                    price_id=price_id,
                                    success_url="http://localhost:8501/?status=success",
                                    cancel_url="http://localhost:8501/?status=cancel"
                                )
                                if session and 'url' in session:
                                    st.markdown(f"[**👉 Click here to complete payment**]({session['url']})", unsafe_allow_html=True)
                                else:
                                    st.error("Failed to create checkout session.")
                else:
                    st.error("Organization not found.")
                    st.markdown("### New Team?")
                    with st.form("register_form"):
                        new_name = st.text_input("Organization Name")
                        new_email = st.text_input("Contact Email")
                        submit = st.form_submit_button("Register Organization")
                        
                        if submit:
                            if new_name and new_email and org_id:
                                res = client.create_customer(org_id, new_name, new_email)
                                if res and 'id' in res:
                                    st.success("Registration Successful! Please Verify Status above.")
                                else:
                                    st.error("Registration failed.")
                            else:
                                st.warning("Please fill all fields.")
        
        except Exception as e:
            st.error(f"Integration Error: {str(e)}")


    # ═══════════════════════════════════════════════════════════
    # PAGE: MATCH ANALYSIS
    # ═══════════════════════════════════════════════════════════
    if page == "Match Analysis":
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Analyze Latest Match", use_container_width=True, type="primary"):
                process_last_match()

        if st.session_state.analysis_result:
            data = st.session_state.analysis_result
            
            # --- 1. SNAPSHOT ---
            snap = data.get('snapshot', {})
            st.markdown(f"""
            <div class="card">
                <div class="card-header">📋 Match Snapshot</div>
                <div class="snapshot-grid">
                    <div class="stat-item">
                        <div class="stat-value">{snap.get('shots_analyzed', 0)}</div>
                        <div class="stat-label">Shots</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{snap.get('rallies', 0)}</div>
                        <div class="stat-label">Rallies</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" style="font-size: 1.1rem;">{snap.get('style', 'Unknown')}</div>
                        <div class="stat-label">Style</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" style="font-size: 1.1rem;">{snap.get('pressure_behavior', 'Stable')}</div>
                        <div class="stat-label">Behavior</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- 2. FINDINGS ---
            findings = data.get('key_findings', [])
            icons = ["🎯", "⚡", "⚠️"]
            findings_html = ""
            for i, f in enumerate(findings):
                icon = icons[i % len(icons)]
                findings_html += f"""
                <div class="finding">
                    <span class="finding-icon">{icon}</span>
                    <span class="finding-text">{f}</span>
                </div>
                """
            
            st.markdown(f"""
            <div class="card">
                <div class="card-header">🔍 Key Findings</div>
                {findings_html}
            </div>
            """, unsafe_allow_html=True)
            
            # --- 3. RECOMMENDATIONS ---
            recs = data.get('recommendations', [])
            recs_html = ""
            for i, r in enumerate(recs):
                recs_html += f'<div class="action"><strong>{i+1}.</strong> {r}</div>'
                
            st.markdown(f"""
            <div class="card">
                <div class="card-header">🎯 Recommendation</div>
                {recs_html}
            </div>
            """, unsafe_allow_html=True)
            
            # --- 4. MENTAL ---
            mental = data.get('mental_pattern', {})
            st.markdown(f"""
            <div class="mental-card">
                <div class="card-header" style="color: #664d03;">🧠 Mental Pattern Detected</div>
                <div class="mental-insight">"{mental.get('insight', 'No pattern detected')}"</div>
                <div class="mental-fix">
                    <strong>Try this:</strong> {mental.get('fix', 'Keep playing focused')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- 5. CONFIDENCE ---
            conf = data.get('confidence_score', 0)
            st.markdown(f"""
            <div class="card">
                <div class="card-header">📊 Coach Confidence</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {conf}%;"></div>
                </div>
                <div class="confidence-text">
                    <span>Dedalus Reliability Score</span>
                    <span><strong>{conf}%</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif not st.session_state.match_stats:
            st.info("👆 Click 'Analyze Latest Match' to start.")

    # ═══════════════════════════════════════════════════════════
    # PAGE: CHAT WITH COACH
    # ═══════════════════════════════════════════════════════════
    elif page == "Chat with Coach":
        st.markdown("### 💬 Chat with Dedalus Agent")
        st.caption("Ask specific questions about your technique, history, or strategy.")
        
        # Display history
        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f'<div class="chat-user">{content}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot">🤖 <strong>Coach:</strong> {content}</div>', unsafe_allow_html=True)
        
        # Input
        if prompt := st.chat_input("Ask me anything about your game..."):
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.rerun() # Immediate update to show user message
            
        # Process response if last message was user (handled after rerun to avoid lag in UI)
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
            with st.spinner("Thinking..."):
                response = st.session_state.coach.chat(
                    st.session_state.chat_history[-1]["content"], 
                    match_stats=st.session_state.match_stats
                )
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    # Footer
    st.markdown("""
    <div style="text-align: center; color: #adb5bd; font-size: 0.85rem; margin-top: 32px;">
        Break Point AI • Snowflake Hackathon 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
