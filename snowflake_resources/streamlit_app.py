# Break Point AI - Snowflake Streamlit Dashboard
# Paste this code into a new Streamlit App in Snowsight

import streamlit as st
import pandas as pd
import json
import altair as alt

# Only needed if running locally (which this script isn't intended for, but imports help linting)
try:
    from snowflake.snowpark.context import get_active_session
    from snowflake.snowpark.functions import col
except ImportError:
    st.error("Please run this app inside Snowflake!")

st.set_page_config(layout="wide")

st.title("🏓 Break Point AI - Match Analysis Dashboard")
st.markdown("Advanced Table Tennis Analytics powered by Snowflake Cortex & Snowpark")

# 1. Connect to Snowflake Session
session = get_active_session()

# 2. Match Selector
matches_df = session.sql("SELECT MATCH_ID, VIDEO_FILE, MATCH_DATE FROM MATCHES ORDER BY MATCH_DATE DESC").to_pandas()
if matches_df.empty:
    st.warning("No match data found. Please run the analysis pipeline first.")
    st.stop()

selected_match = st.selectbox(
    "Select a Match to Analyze",
    matches_df['MATCH_ID'].tolist(),
    format_func=lambda x: f"{x} ({matches_df[matches_df['MATCH_ID'] == x]['VIDEO_FILE'].iloc[0]})"
)

# 3. Fetch Data for Selected Match
match_stats = session.sql(f"SELECT * FROM MATCH_STATS WHERE MATCH_ID = '{selected_match}'").to_pandas()
insights = session.sql(f"SELECT * FROM COACHING_INSIGHTS WHERE MATCH_ID = '{selected_match}'").to_pandas()
analysis = session.sql(f"SELECT * FROM ANALYSIS_OUTPUT WHERE MATCH_ID = '{selected_match}'").to_pandas()

if not match_stats.empty:
    stats_json = json.loads(match_stats['SUMMARY_JSON'].iloc[0])
    
    # 4. Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rallies", stats_json.get('total_rallies', 0))
    with col2:
        st.metric("Avg Rhythm (Lower is Better)", stats_json.get('avg_rhythm_score', 0))
    with col3:
        st.metric("Timing Score", stats_json.get('avg_timing_score', 0))
    with col4:
        st.metric("Tactical Score", stats_json.get('avg_tactical_score', 0))

    # 5. Charts
    st.subheader("Performance Breakdown")
    chart_data = pd.DataFrame({
        'Metric': ['Rhythm', 'Timing', 'Tactics'],
        'Score': [
            stats_json.get('avg_rhythm_score', 0),
            stats_json.get('avg_timing_score', 0),
            stats_json.get('avg_tactical_score', 0)
        ]
    })
    
    chart = alt.Chart(chart_data).mark_bar().encode(
        x='Metric',
        y='Score',
        color='Metric'
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

    # 6. AI Coaching Insight
    st.subheader("🤖 AI Coach Insight")
    if not insights.empty:
        st.info(insights['LLM_RESPONSE_TEXT'].iloc[0])
    else:
        st.warning("No AI insights generated for this match.")

    # 7. Semantic Search (Historical Context)
    st.subheader("🔍 Find Similar Matches (Cortex Vector Search)")
    search_query = st.text_input("Describe a style or situation (e.g., 'aggressive loop play'):")
    if search_query:
        # Use our FIND_SIMILAR_MATCHES UDTF
        try:
            results = session.sql(f"SELECT * FROM TABLE(FIND_SIMILAR_MATCHES('{search_query}', 3))").to_pandas()
            if not results.empty:
                for idx, row in results.iterrows():
                    with st.expander(f"Match {row['MATCH_ID']} (Score: {row['SCORE']:.2f})"):
                        st.write(row['SUMMARY'])
            else:
                st.write("No similar matches found.")
        except Exception as e:
            st.error(f"Generate embeddings first! Error: {e}")

else:
    st.error("Stats data not found for this match.")
