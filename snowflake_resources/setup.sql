-- ==============================================================================
-- SETUP SCRIPT FOR BREAK POINT AI (Snowflake Resources)
-- Run this in your Snowsight Worksheet to initialize tables and advanced features.
-- ==============================================================================

-- 1. TRACKING & RAW DATA (Historical Storage)
-- Already created by python script, but good to have definition here
CREATE TABLE IF NOT EXISTS MATCHES (
    MATCH_ID VARCHAR(50) PRIMARY KEY,
    PLAYER1_NAME VARCHAR(50),
    PLAYER2_NAME VARCHAR(50),
    VIDEO_FILE VARCHAR(255),
    MATCH_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS MATCH_STATS (
    MATCH_ID VARCHAR(50) PRIMARY KEY,
    SUMMARY_JSON VARIANT,
    RALLIES_JSON VARIANT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
);

CREATE TABLE IF NOT EXISTS COACHING_INSIGHTS (
    MATCH_ID VARCHAR(50),
    PROMPT_TEXT TEXT,
    LLM_RESPONSE_TEXT TEXT,
    PROCESSED_RESPONSE_JSON VARIANT,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
);

CREATE TABLE IF NOT EXISTS ANALYSIS_OUTPUT (
    MATCH_ID VARCHAR(50) PRIMARY KEY,
    FULL_ANALYSIS VARIANT,
    SEMANTIC_SUMMARY TEXT,
    SEMANTIC_VECTOR VECTOR(FLOAT, 768),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
);

-- ==============================================================================
-- FEATURE ENGINEERING IN SNOWFLAKE (Advanced)
-- Moving logic from Python to SQL for scalability
-- ==============================================================================

-- Feature 1: Flattened Match Summary
-- Extracts key metrics from the JSON blob into queryable columns
CREATE OR REPLACE VIEW MATCH_METRICS_VIEW AS
SELECT 
    MS.MATCH_ID,
    M.PLAYER1_NAME,
    M.PLAYER2_NAME,
    M.MATCH_DATE,
    MS.SUMMARY_JSON:total_rallies::INTEGER as TOTAL_RALLIES,
    MS.SUMMARY_JSON:total_shots::INTEGER as TOTAL_SHOTS,
    MS.SUMMARY_JSON:avg_rhythm_score::FLOAT as AVG_RHYTHM,
    MS.SUMMARY_JSON:avg_timing_score::FLOAT as AVG_TIMING,
    MS.SUMMARY_JSON:avg_tactical_score::FLOAT as AVG_TACTICS
FROM MATCH_STATS MS
JOIN MATCHES M ON MS.MATCH_ID = M.MATCH_ID;

-- Feature 2: Player Performance Aggregation
-- Aggregates stats across all matches to find historical trends
CREATE OR REPLACE VIEW PLAYER_STATS_AGGREGATE AS
SELECT 
    PLAYER1_NAME as PLAYER,
    COUNT(DISTINCT MATCH_ID) as MATCHES_PLAYED,
    AVG(TOTAL_RALLIES) as AVG_RALLIES_PER_MATCH,
    AVG(AVG_TIMING) as AVG_TIMING_SCORE,
    AVG(AVG_TACTICS) as AVG_TACTICAL_SCORE
FROM MATCH_METRICS_VIEW
GROUP BY PLAYER1_NAME;

-- Feature 3: Rally Analysis View
-- Expands the RALLIES_JSON array into individual rows for rally-level analysis
CREATE OR REPLACE VIEW RALLY_DETAILS_VIEW AS
SELECT 
    MATCH_ID,
    value:id::INTEGER as RALLY_ID,
    value:duration_sec::FLOAT as DURATION,
    value:shot_count::INTEGER as SHOT_COUNT,
    value:rhythm_consistency::FLOAT as RHYTHM,
    value:winner::STRING as WINNER
FROM MATCH_STATS,
LATERAL FLATTEN(input => RALLIES_JSON);

-- Feature 4: Cortex Search for Similar Matches
-- SQL Function to find matches with similar semantic content
-- Usage: SELECT * FROM TABLE(FIND_SIMILAR_MATCHES('player loop aggression', 5));
CREATE OR REPLACE FUNCTION FIND_SIMILAR_MATCHES(QUERY_TEXT STRING, TOP_K INTEGER)
RETURNS TABLE (MATCH_ID STRING, SCORE FLOAT, SUMMARY STRING)
LANGUAGE SQL
AS
$$
    SELECT
        MATCH_ID,
        VECTOR_COSINE_SIMILARITY(
            SEMANTIC_VECTOR,
            SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', QUERY_TEXT)
        ) AS SCORE,
        SEMANTIC_SUMMARY
    FROM ANALYSIS_OUTPUT
    ORDER BY SCORE DESC
    LIMIT TOP_K
$$;
