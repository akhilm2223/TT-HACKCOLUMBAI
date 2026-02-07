-- Run this in a Snowflake Worksheet to set up the necessary objects
-- Break Point: Snowflake-Native Architecture (Memory + Reasoning + Decision)

-- 1. Create a Warehouse (Compute resource)
CREATE OR REPLACE WAREHOUSE TENNIS_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

-- 2. Create the Database
CREATE OR REPLACE DATABASE TENNIS_DB;

-- 3. Create the Schema
CREATE OR REPLACE SCHEMA TENNIS_DB.RAW_DATA;

-- 4. Switch to use these objects
USE WAREHOUSE TENNIS_WH;
USE DATABASE TENNIS_DB;
USE SCHEMA RAW_DATA;

-- ============================================================
-- TABLES
-- ============================================================

-- Matches (one row per video analyzed)
CREATE OR REPLACE TABLE MATCHES (
    MATCH_ID VARCHAR(50) PRIMARY KEY,
    PLAYER1_NAME VARCHAR(50),
    PLAYER2_NAME VARCHAR(50),
    VIDEO_FILE VARCHAR(255),
    MATCH_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Frame-level tracking events (raw perception, buffered inserts)
CREATE OR REPLACE TABLE TRACKING_EVENTS (
    EVENT_ID VARCHAR(50) PRIMARY KEY,
    MATCH_ID VARCHAR(50),
    RALLY_ID VARCHAR(50),
    TIMESTAMP TIMESTAMP_NTZ,
    RAW_DATA VARIANT,
    CONSTRAINT fk_tracking_match FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
);

-- Computed match stats (from StatsEngine)
CREATE OR REPLACE TABLE MATCH_STATS (
    STATS_ID VARCHAR(50) PRIMARY KEY DEFAULT UUID_STRING(),
    MATCH_ID VARCHAR(50),
    SUMMARY_JSON VARIANT,
    RALLIES_JSON VARIANT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT fk_stats_match FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
);

-- Full pipeline output: court + perception + shots + rallies + behavioral + semantic
-- This is the SINGLE SOURCE OF TRUTH for K2/Cortex reasoning
CREATE OR REPLACE TABLE ANALYSIS_OUTPUT (
    MATCH_ID VARCHAR(50) PRIMARY KEY,
    FULL_ANALYSIS VARIANT,
    SEMANTIC_SUMMARY VARCHAR(4000),
    SEMANTIC_VECTOR VECTOR(FLOAT, 768),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT fk_analysis_match FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
);

-- Coaching insights from Cortex LLM reasoning
CREATE OR REPLACE TABLE COACHING_INSIGHTS (
    INSIGHT_ID VARCHAR(50) PRIMARY KEY DEFAULT UUID_STRING(),
    MATCH_ID VARCHAR(50),
    PROMPT_TEXT STRING,
    LLM_RESPONSE_TEXT STRING,
    PROCESSED_RESPONSE_JSON VARIANT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT fk_insight_match FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
);

-- ============================================================
-- CORTEX: Vector search function for cross-match pattern retrieval
-- ============================================================

-- Find matches with similar playing patterns (semantic vector similarity)
-- Usage: SELECT * FROM TABLE(FIND_SIMILAR_MATCHES('footwork dropped under pressure', 5));
CREATE OR REPLACE FUNCTION FIND_SIMILAR_MATCHES(QUERY_TEXT VARCHAR, TOP_K INT)
RETURNS TABLE (MATCH_ID VARCHAR, VIDEO_FILE VARCHAR, SIMILARITY FLOAT, SEMANTIC_SUMMARY VARCHAR)
AS
$$
    SELECT
        a.MATCH_ID,
        m.VIDEO_FILE,
        VECTOR_COSINE_SIMILARITY(
            a.SEMANTIC_VECTOR,
            SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', QUERY_TEXT)
        ) AS SIMILARITY,
        a.SEMANTIC_SUMMARY
    FROM ANALYSIS_OUTPUT a
    JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID
    WHERE a.SEMANTIC_VECTOR IS NOT NULL
    ORDER BY SIMILARITY DESC
    LIMIT TOP_K
$$;

-- ============================================================
-- CORTEX: Structured queries on VARIANT (SQL on JSON)
-- ============================================================

-- Example: all forehand shots across all matches
-- SELECT * FROM V_ALL_SHOTS WHERE HAND = 'forehand' AND LANDING_ZONE LIKE 'near%';
CREATE OR REPLACE VIEW V_ALL_SHOTS AS
SELECT
    a.MATCH_ID,
    m.VIDEO_FILE,
    s.VALUE:shot_id::INT AS SHOT_ID,
    s.VALUE:t_start::FLOAT AS T_START,
    s.VALUE:t_contact::FLOAT AS T_CONTACT,
    s.VALUE:t_end::FLOAT AS T_END,
    s.VALUE:player::VARCHAR AS PLAYER,
    s.VALUE:hand::VARCHAR AS HAND,
    s.VALUE:shot_type::VARCHAR AS SHOT_TYPE,
    s.VALUE:landing.depth::VARCHAR AS DEPTH,
    s.VALUE:landing.zone::VARCHAR AS LANDING_ZONE,
    s.VALUE:landing.x::INT AS LANDING_X,
    s.VALUE:landing.y::INT AS LANDING_Y
FROM ANALYSIS_OUTPUT a,
    LATERAL FLATTEN(input => a.FULL_ANALYSIS:shots) s
JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID;

-- Example: behavioral metrics across matches
-- SELECT * FROM V_BEHAVIORAL WHERE FOOTWORK_DROP_PCT > 30;
CREATE OR REPLACE VIEW V_BEHAVIORAL AS
SELECT
    a.MATCH_ID,
    m.VIDEO_FILE,
    a.FULL_ANALYSIS:behavioral_metrics.player.footwork_drop_pct::INT AS FOOTWORK_DROP_PCT,
    a.FULL_ANALYSIS:behavioral_metrics.player.avg_footwork_speed::FLOAT AS AVG_FOOTWORK,
    a.FULL_ANALYSIS:behavioral_metrics.player.avg_arm_speed::FLOAT AS AVG_ARM_SPEED,
    a.FULL_ANALYSIS:behavioral_metrics.player.aggression_index.value::FLOAT AS AGGRESSION,
    a.FULL_ANALYSIS:behavioral_metrics.match.total_shots::INT AS TOTAL_SHOTS,
    a.FULL_ANALYSIS:behavioral_metrics.match.total_rallies::INT AS TOTAL_RALLIES,
    a.FULL_ANALYSIS:behavioral_metrics.match.forehand_pct::FLOAT AS FOREHAND_PCT,
    a.FULL_ANALYSIS:behavioral_metrics.match.backhand_pct::FLOAT AS BACKHAND_PCT,
    a.FULL_ANALYSIS:behavioral_metrics.match.avg_rally_duration::FLOAT AS AVG_RALLY_DURATION,
    a.SEMANTIC_SUMMARY
FROM ANALYSIS_OUTPUT a
JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID;

-- Example: all rallies
CREATE OR REPLACE VIEW V_ALL_RALLIES AS
SELECT
    a.MATCH_ID,
    r.VALUE:rally_id::INT AS RALLY_ID,
    r.VALUE:t_start::FLOAT AS T_START,
    r.VALUE:t_end::FLOAT AS T_END,
    r.VALUE:length::INT AS RALLY_LENGTH,
    r.VALUE:winner::VARCHAR AS WINNER
FROM ANALYSIS_OUTPUT a,
    LATERAL FLATTEN(input => a.FULL_ANALYSIS:rallies) r;
