"""
Snowflake-Native Storage + Cortex AI for Break Point
Replaces MongoDB + Vector DB with a single Snowflake platform:
  - VARIANT columns for structured JSON (perception, shots, rallies)
  - VECTOR columns for semantic embeddings (Cortex EMBED_TEXT_768)
  - Cortex COMPLETE for LLM reasoning (coaching insights)
  - VECTOR_COSINE_SIMILARITY for cross-match pattern retrieval
"""
import os
import json
import uuid
import datetime
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


class SnowflakeDB:
    """Low-level Snowflake connection and query execution."""

    def __init__(self):
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "TENNIS_WH")
        self.database = os.getenv("SNOWFLAKE_DATABASE", "TENNIS_DB")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA", "RAW_DATA")
        self.conn = None

    def connect(self):
        """Establish connection to Snowflake."""
        try:
            self.conn = snowflake.connector.connect(
                user=self.user,
                password=self.password,
                account=self.account,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema
            )
            print("[Snowflake] Connected")
            return True
        except Exception as e:
            print(f"[Snowflake] Connection failed: {e}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """Execute a query and return cursor."""
        if not self.conn:
            if not self.connect():
                return None
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            print(f"[Snowflake] Query error: {e}")
            cursor.close()
            return None

<<<<<<< HEAD
    # ----------------------------------------------------------
    # MATCHES
    # ----------------------------------------------------------
=======
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        # MATCHES table
        matches_ddl = """
        CREATE TABLE IF NOT EXISTS MATCHES (
            MATCH_ID VARCHAR(50) PRIMARY KEY,
            PLAYER1_NAME VARCHAR(50),
            PLAYER2_NAME VARCHAR(50),
            VIDEO_FILE VARCHAR(255),
            MATCH_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
        
        # TRACKING_EVENTS table
        tracking_ddl = """
        CREATE TABLE IF NOT EXISTS TRACKING_EVENTS (
            EVENT_ID VARCHAR(50) PRIMARY KEY,
            MATCH_ID VARCHAR(50),
            RALLY_ID VARCHAR(50),
            TIMESTAMP TIMESTAMP_NTZ,
            RAW_DATA VARIANT,
            FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
        )
        """

        # MATCH_STATS table
        stats_ddl = """
        CREATE TABLE IF NOT EXISTS MATCH_STATS (
            MATCH_ID VARCHAR(50) PRIMARY KEY,
            SUMMARY_JSON VARIANT,
            RALLIES_JSON VARIANT,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
        )
        """

        # COACHING_INSIGHTS table
        insights_ddl = """
        CREATE TABLE IF NOT EXISTS COACHING_INSIGHTS (
            MATCH_ID VARCHAR(50),
            PROMPT_TEXT TEXT,
            LLM_RESPONSE_TEXT TEXT,
            PROCESSED_RESPONSE_JSON VARIANT,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
        )
        """

        # ANALYSIS_OUTPUT table (Full Pipeline + Cortex Embeddings)
        analysis_ddl = """
        CREATE TABLE IF NOT EXISTS ANALYSIS_OUTPUT (
            MATCH_ID VARCHAR(50) PRIMARY KEY,
            FULL_ANALYSIS VARIANT,
            SEMANTIC_SUMMARY TEXT,
            SEMANTIC_VECTOR VECTOR(FLOAT, 768),
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            FOREIGN KEY (MATCH_ID) REFERENCES MATCHES(MATCH_ID)
        )
        """
        
        self.execute_query(matches_ddl)
        self.execute_query(tracking_ddl)
        self.execute_query(stats_ddl)
        self.execute_query(insights_ddl)
        self.execute_query(analysis_ddl)
        print("Tables checked/created.")

>>>>>>> 9e0a16c (changes)
    def insert_match(self, match_id, p1_name, p2_name, video_file):
        query = """
        MERGE INTO MATCHES AS target
        USING (SELECT %s AS id, %s AS p1, %s AS p2, %s AS vid) AS source
        ON target.MATCH_ID = source.id
        WHEN NOT MATCHED THEN
        INSERT (MATCH_ID, PLAYER1_NAME, PLAYER2_NAME, VIDEO_FILE)
        VALUES (source.id, source.p1, source.p2, source.vid)
        """
        self.execute_query(query, (match_id, p1_name, p2_name, video_file))

    # ----------------------------------------------------------
    # TRACKING EVENTS (buffered frame-level inserts)
    # ----------------------------------------------------------
    def insert_tracking_data(self, tracking_data):
        values = []
        for item in tracking_data:
            values.append((
                item['event_id'], item['match_id'], item['rally_id'],
                item['timestamp'], json.dumps(item['raw_data'])
            ))
        query = """
        INSERT INTO TRACKING_EVENTS (EVENT_ID, MATCH_ID, RALLY_ID, TIMESTAMP, RAW_DATA)
        SELECT column1, column2, column3, column4, PARSE_JSON(column5)
        FROM VALUES (%s, %s, %s, %s, %s)
        """
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.executemany(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"[Snowflake] Batch insert error: {e}")
        finally:
            cursor.close()

    # ----------------------------------------------------------
    # MATCH STATS
    # ----------------------------------------------------------
    def insert_match_stats(self, match_id, summary, rallies):
        query = """
        INSERT INTO MATCH_STATS (MATCH_ID, SUMMARY_JSON, RALLIES_JSON)
        SELECT %s, PARSE_JSON(%s), PARSE_JSON(%s)
        """
        self.execute_query(query, (match_id, json.dumps(summary), json.dumps(rallies)))

    # ----------------------------------------------------------
    # ANALYSIS_OUTPUT: full pipeline JSON + Cortex vector embedding
    # ----------------------------------------------------------
    def insert_full_analysis(self, match_id, analysis_dict):
        """
        Store the complete pipeline output as VARIANT + generate Cortex vector embedding
        from the semantic_summary field.  Single source of truth for K2 / analytics.
        """
        if not self.conn:
            if not self.connect():
                return False
        try:
            json_str = json.dumps(analysis_dict, default=str, ensure_ascii=False)
            semantic = analysis_dict.get("semantic_summary", "")

            # MERGE: insert or update; embed the semantic summary into a 768-dim vector
            query = """
            MERGE INTO ANALYSIS_OUTPUT AS target
            USING (
                SELECT
                    %s AS mid,
                    PARSE_JSON(%s) AS analysis,
                    %s AS summary,
                    SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', %s) AS vec
            ) AS source
            ON target.MATCH_ID = source.mid
            WHEN MATCHED THEN UPDATE SET
                FULL_ANALYSIS = source.analysis,
                SEMANTIC_SUMMARY = source.summary,
                SEMANTIC_VECTOR = source.vec,
                CREATED_AT = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN INSERT
                (MATCH_ID, FULL_ANALYSIS, SEMANTIC_SUMMARY, SEMANTIC_VECTOR)
                VALUES (source.mid, source.analysis, source.summary, source.vec)
            """
            cursor = self.execute_query(query, (match_id, json_str, semantic, semantic))
            if cursor:
                cursor.close()
            self.conn.commit()
            print(f"[Snowflake] Analysis + vector stored for match {match_id}")
            return True
        except Exception as e:
            print(f"[Snowflake] insert_full_analysis error: {e}")
            return False

    # ----------------------------------------------------------
    # CORTEX: Vector search — find similar matches
    # ----------------------------------------------------------
    def find_similar_matches(self, query_text, top_k=5):
        """
        Semantic search across all stored matches using Cortex EMBED + VECTOR_COSINE_SIMILARITY.
        Returns list of dicts: [{match_id, video_file, similarity, semantic_summary}, ...]
        """
        query = """
        SELECT
            a.MATCH_ID,
            m.VIDEO_FILE,
            VECTOR_COSINE_SIMILARITY(
                a.SEMANTIC_VECTOR,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', %s)
            ) AS SIMILARITY,
            a.SEMANTIC_SUMMARY
        FROM ANALYSIS_OUTPUT a
        JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID
        WHERE a.SEMANTIC_VECTOR IS NOT NULL
        ORDER BY SIMILARITY DESC
        LIMIT %s
        """
        cursor = self.execute_query(query, (query_text, top_k))
        if not cursor:
            return []
        rows = cursor.fetchall()
        cursor.close()
        return [
            {"match_id": r[0], "video_file": r[1], "similarity": float(r[2]), "semantic_summary": r[3]}
            for r in rows
        ]

    # ----------------------------------------------------------
    # CORTEX: LLM reasoning via Cortex COMPLETE
    # ----------------------------------------------------------
    def cortex_complete(self, prompt, model='llama3.1-70b'):
        """
        Call Snowflake Cortex COMPLETE for LLM reasoning.
        Returns the generated text string.
        """
        query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s) AS response
        """
        cursor = self.execute_query(query, (model, prompt))
        if not cursor:
            return None
        row = cursor.fetchone()
        cursor.close()
        if row:
            resp = row[0]
            # Cortex returns JSON string or plain text depending on model
            if isinstance(resp, str):
                try:
                    parsed = json.loads(resp)
                    # Some models wrap in {"choices": [{"messages": "..."}]}
                    if isinstance(parsed, dict) and "choices" in parsed:
                        return parsed["choices"][0].get("messages", resp)
                    return resp
                except json.JSONDecodeError:
                    return resp
            return str(resp)
        return None

    # ----------------------------------------------------------
    # CORTEX: Get full analysis from Snowflake for a match
    # ----------------------------------------------------------
    def get_analysis(self, match_id):
        """Fetch the full analysis VARIANT for a match as a Python dict."""
        query = "SELECT FULL_ANALYSIS FROM ANALYSIS_OUTPUT WHERE MATCH_ID = %s"
        cursor = self.execute_query(query, (match_id,))
        if not cursor:
            return None
        row = cursor.fetchone()
        cursor.close()
        if row:
            payload = row[0]
            if isinstance(payload, str):
                return json.loads(payload)
            return payload
        return None

    # ----------------------------------------------------------
    # COACHING INSIGHTS
    # ----------------------------------------------------------
    def insert_coaching_insight(self, match_id, prompt, response, processed_json=None):
        processed_str = json.dumps(processed_json) if processed_json else None
        query = """
        INSERT INTO COACHING_INSIGHTS (MATCH_ID, PROMPT_TEXT, LLM_RESPONSE_TEXT, PROCESSED_RESPONSE_JSON)
        SELECT %s, %s, %s, PARSE_JSON(%s)
        """
        self.execute_query(query, (match_id, prompt, response, processed_str))


<<<<<<< HEAD
# ==============================================================
# TrackingDB: high-level wrapper (used by main.py during processing)
# ==============================================================
=======

    # ----------------------------------------------------------
    # ANALYSIS_OUTPUT: full pipeline JSON + Cortex vector embedding
    # ----------------------------------------------------------
    def insert_full_analysis(self, match_id, analysis_dict):
        """
        Store the complete pipeline output as VARIANT + generate Cortex vector embedding
        from the semantic_summary field.  Single source of truth for K2 / analytics.
        """
        if not self.conn:
            if not self.connect():
                return False
        try:
            import json
            json_str = json.dumps(analysis_dict, default=str, ensure_ascii=False)
            semantic = analysis_dict.get("semantic_summary", "")

            # MERGE: insert or update; embed the semantic summary into a 768-dim vector
            query = """
            MERGE INTO ANALYSIS_OUTPUT AS target
            USING (
                SELECT
                    %s AS mid,
                    PARSE_JSON(%s) AS analysis,
                    %s AS summary,
                    SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', %s) AS vec
            ) AS source
            ON target.MATCH_ID = source.mid
            WHEN MATCHED THEN UPDATE SET
                FULL_ANALYSIS = source.analysis,
                SEMANTIC_SUMMARY = source.summary,
                SEMANTIC_VECTOR = source.vec,
                CREATED_AT = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN INSERT
                (MATCH_ID, FULL_ANALYSIS, SEMANTIC_SUMMARY, SEMANTIC_VECTOR)
                VALUES (source.mid, source.analysis, source.summary, source.vec)
            """
            cursor = self.execute_query(query, (match_id, json_str, semantic, semantic))
            if cursor:
                cursor.close()
            self.conn.commit()
            print(f"[Snowflake] Analysis + vector stored for match {match_id}")
            return True
        except Exception as e:
            print(f"[Snowflake] insert_full_analysis error: {e}")
            return False

    # ----------------------------------------------------------
    # CORTEX: Vector search — find similar matches
    # ----------------------------------------------------------
    def find_similar_matches(self, query_text, top_k=5):
        """
        Semantic search across all stored matches using Cortex EMBED + VECTOR_COSINE_SIMILARITY.
        Returns list of dicts: [{match_id, video_file, similarity, semantic_summary}, ...]
        """
        query = """
        SELECT
            a.MATCH_ID,
            m.VIDEO_FILE,
            VECTOR_COSINE_SIMILARITY(
                a.SEMANTIC_VECTOR,
                SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', %s)
            ) AS SIMILARITY,
            a.SEMANTIC_SUMMARY
        FROM ANALYSIS_OUTPUT a
        JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID
        WHERE a.SEMANTIC_VECTOR IS NOT NULL
        ORDER BY SIMILARITY DESC
        LIMIT %s
        """
        cursor = self.execute_query(query, (query_text, top_k))
        if not cursor:
            return []
        rows = cursor.fetchall()
        cursor.close()
        return [
            {"match_id": r[0], "video_file": r[1], "similarity": float(r[2]), "semantic_summary": r[3]}
            for r in rows
        ]

    # ----------------------------------------------------------
    # CORTEX: LLM reasoning via Cortex COMPLETE
    # ----------------------------------------------------------
    def cortex_complete(self, prompt, model='llama3.1-70b'):
        """
        Call Snowflake Cortex COMPLETE for LLM reasoning.
        Returns the generated text string.
        """
        import json
        query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s) AS response
        """
        cursor = self.execute_query(query, (model, prompt))
        if not cursor:
            return None
        row = cursor.fetchone()
        cursor.close()
        if row:
            resp = row[0]
            # Cortex returns JSON string or plain text depending on model
            if isinstance(resp, str):
                try:
                    parsed = json.loads(resp)
                    # Some models wrap in {"choices": [{"messages": "..."}]}
                    if isinstance(parsed, dict) and "choices" in parsed:
                        return parsed["choices"][0].get("messages", resp)
                    return resp
                except json.JSONDecodeError:
                    return resp
            return str(resp)
        return None

    # ----------------------------------------------------------
    # CORTEX: Get full analysis from Snowflake for a match
    # ----------------------------------------------------------
    def get_analysis(self, match_id):
        """Fetch the full analysis VARIANT for a match as a Python dict."""
        import json
        query = "SELECT FULL_ANALYSIS FROM ANALYSIS_OUTPUT WHERE MATCH_ID = %s"
        cursor = self.execute_query(query, (match_id,))
        if not cursor:
            return None
        row = cursor.fetchone()
        cursor.close()
        if row:
            payload = row[0]
            if isinstance(payload, str):
                return json.loads(payload)
            return payload
        return None


import uuid
import datetime
>>>>>>> 9e0a16c (changes)

class TrackingDB:
    """Buffers frame-level events and provides match lifecycle."""

    def __init__(self):
        self.db = SnowflakeDB()
        self.buffer = []
        self.buffer_size = 100

    def connect(self):
        return self.db.connect()

    def create_new_match(self, video_file, p1_name="Player 1", p2_name="Player 2"):
        match_id = str(uuid.uuid4())
        self.db.insert_match(match_id, p1_name, p2_name, video_file)
        return match_id

    def add_event(self, match_id, frame_num, ball_pos, p1_pose=None, p2_pose=None, event_type="tracking"):
        data = {
            "frame": frame_num,
            "ball": {"x": float(ball_pos[0]), "y": float(ball_pos[1])} if ball_pos else None,
            "p1": self._serialize_pose(p1_pose),
            "p2": self._serialize_pose(p2_pose),
            "event": event_type
        }
        self.buffer.append({
            "event_id": str(uuid.uuid4()),
            "match_id": match_id,
            "rally_id": None,
            "timestamp": datetime.datetime.now().isoformat(),
            "raw_data": data
        })
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def _serialize_pose(self, pose):
        if pose is None:
            return None
        try:
            return [{"x": float(k[0]), "y": float(k[1])} for k in pose]
        except Exception:
            return None

    def flush(self):
        if self.buffer:
            self.db.insert_tracking_data(self.buffer)
            self.buffer = []

    def close(self):
        self.flush()
        self.db.close()
