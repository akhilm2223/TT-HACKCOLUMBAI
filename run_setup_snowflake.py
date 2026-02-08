"""
Run setup_snowflake.sql statements via Python connector.
Creates all tables, views, and functions needed for the pipeline.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.snowflake_db import SnowflakeDB

STATEMENTS = [
    # 1. Warehouse
    """CREATE WAREHOUSE IF NOT EXISTS TENNIS_WH
       WITH WAREHOUSE_SIZE = 'XSMALL'
       AUTO_SUSPEND = 60
       AUTO_RESUME = TRUE""",

    # 2. Database + Schema
    "CREATE DATABASE IF NOT EXISTS TENNIS_DB",
    "CREATE SCHEMA IF NOT EXISTS TENNIS_DB.RAW_DATA",
    "USE WAREHOUSE TENNIS_WH",
    "USE DATABASE TENNIS_DB",
    "USE SCHEMA RAW_DATA",

    # 3. Tables
    """CREATE TABLE IF NOT EXISTS MATCHES (
        MATCH_ID VARCHAR(50) PRIMARY KEY,
        PLAYER1_NAME VARCHAR(50),
        PLAYER2_NAME VARCHAR(50),
        VIDEO_FILE VARCHAR(255),
        MATCH_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )""",

    """CREATE TABLE IF NOT EXISTS TRACKING_EVENTS (
        EVENT_ID VARCHAR(50) PRIMARY KEY,
        MATCH_ID VARCHAR(50),
        RALLY_ID VARCHAR(50),
        TIMESTAMP TIMESTAMP_NTZ,
        RAW_DATA VARIANT
    )""",

    """CREATE TABLE IF NOT EXISTS MATCH_STATS (
        STATS_ID VARCHAR(50) PRIMARY KEY DEFAULT UUID_STRING(),
        MATCH_ID VARCHAR(50),
        SUMMARY_JSON VARIANT,
        RALLIES_JSON VARIANT,
        CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )""",

    """CREATE TABLE IF NOT EXISTS ANALYSIS_OUTPUT (
        MATCH_ID VARCHAR(50) PRIMARY KEY,
        FULL_ANALYSIS VARIANT,
        SEMANTIC_SUMMARY VARCHAR(4000),
        SEMANTIC_VECTOR VECTOR(FLOAT, 768),
        CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )""",

    """CREATE TABLE IF NOT EXISTS COACHING_INSIGHTS (
        INSIGHT_ID VARCHAR(50) PRIMARY KEY DEFAULT UUID_STRING(),
        MATCH_ID VARCHAR(50),
        PROMPT_TEXT STRING,
        LLM_RESPONSE_TEXT STRING,
        PROCESSED_RESPONSE_JSON VARIANT,
        CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    )""",

    # 4. Views
    """CREATE OR REPLACE VIEW V_ALL_SHOTS AS
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
    JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID""",

    """CREATE OR REPLACE VIEW V_BEHAVIORAL AS
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
    JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID""",

    """CREATE OR REPLACE VIEW V_ALL_RALLIES AS
    SELECT
        a.MATCH_ID,
        r.VALUE:rally_id::INT AS RALLY_ID,
        r.VALUE:t_start::FLOAT AS T_START,
        r.VALUE:t_end::FLOAT AS T_END,
        r.VALUE:length::INT AS RALLY_LENGTH,
        r.VALUE:winner::VARCHAR AS WINNER
    FROM ANALYSIS_OUTPUT a,
        LATERAL FLATTEN(input => a.FULL_ANALYSIS:rallies) r""",
]


def main():
    db = SnowflakeDB()
    if not db.connect():
        print("FAILED: Could not connect to Snowflake.")
        return

    print(f"Connected to Snowflake: {db.account}")
    print(f"{'='*60}")

    for i, sql in enumerate(STATEMENTS):
        label = sql.strip().split('\n')[0][:70]
        try:
            cursor = db.conn.cursor()
            cursor.execute(sql)
            cursor.close()
            print(f"  [{i+1}/{len(STATEMENTS)}] OK: {label}")
        except Exception as e:
            print(f"  [{i+1}/{len(STATEMENTS)}] ERROR: {label}")
            print(f"         {e}")

    # Verify tables exist
    print(f"\n{'='*60}")
    print("Verifying tables...")
    cursor = db.conn.cursor()
    cursor.execute("SHOW TABLES IN SCHEMA TENNIS_DB.RAW_DATA")
    rows = cursor.fetchall()
    for r in rows:
        print(f"  Table: {r[1]}")
    cursor.close()

    db.close()
    print("\nSetup complete! Now run: py -3 push_to_snowflake.py")


if __name__ == "__main__":
    main()
