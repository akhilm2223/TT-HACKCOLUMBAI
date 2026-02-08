# Snowflake Integration Guide

This directory contains resources to deploy your table tennis analytics on Snowflake.

## 1. Setup (SQL Tables & Features)

Run the content of `setup.sql` in a Snowflake Worksheet to:

1.  Create the necessary tables (`MATCHES`, `MATCH_STATS`, `COACHING_INSIGHTS`, `ANALYSIS_OUTPUT`).
2.  Create **Views** for feature engineering (`MATCH_METRICS_VIEW`, `PLAYER_STATS_AGGREGATE`).
3.  Register the **Cortex Vector Search** function (`FIND_SIMILAR_MATCHES`).

## 2. Streamlit in Snowflake (App)

1.  Log in to Snowsight.
2.  Go to **Streamlit** -> **+ Streamlit App**.
3.  Paste the code from `streamlit_app.py`.
4.  Run the app to see your match analysis dashboard.

## 3. Advanced Snowflake Features (How else to use it?)

### A. Feature Engineering with SQL/Snowpark

Instead of calculating average rally length in Python, let Snowflake do it for thousands of matches instantly:

- **Views**: `MATCH_METRICS_VIEW` (in `setup.sql`) automatically flattens JSON data into columns.
- **UDFs**: Create a Python UDF to categorize playing styles based on shot distribution directly in SQL.

### B. Cortex Vector Search (RAG)

We implemented `FIND_SIMILAR_MATCHES` using `VECTOR_COSINE_SIMILARITY`. This allows you to find "players with similar backhand loops" purely by semantic meaning, not just keyword matching.

### C. Dynamic Tables (Near Real-Time)

Use Dynamic Tables to maintain a live leaderboard:

```sql
CREATE OR REPLACE DYNAMIC TABLE LEADERBOARD
TARGET_LAG = '1 minute'
AS SELECT PLAYER1_NAME, COUNT(*) as WINS FROM MATCH_METRICS_VIEW WHERE WINNER = PLAYER1_NAME GROUP BY 1;
```

### D. Snowpark ML

Train a model to predict the winner of a rally based on the first 3 shots using Snowpark ML, running purely on Snowflake compute without moving data out.
