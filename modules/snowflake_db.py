import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SnowflakeDB:
    def __init__(self):
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA")
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
            print("Successfully connected to Snowflake")
            return True
        except Exception as e:
            print(f"Failed to connect to Snowflake: {e}")
            return False

    def close(self):
        """Close the connection."""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """Execute a query and return results."""
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
            print(f"Query execution error: {e}")
            # Only close on error, otherwise caller handles it (or implicitly closed by conn.close)
            cursor.close()
            return None

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
        
        self.execute_query(matches_ddl)
        self.execute_query(tracking_ddl)
        print("Tables checked/created.")

    def insert_match(self, match_id, p1_name, p2_name, video_file):
        """Insert a new match record."""
        query = """
        MERGE INTO MATCHES AS target
        USING (SELECT %s AS id, %s AS p1, %s AS p2, %s AS vid) AS source
        ON target.MATCH_ID = source.id
        WHEN NOT MATCHED THEN
        INSERT (MATCH_ID, PLAYER1_NAME, PLAYER2_NAME, VIDEO_FILE)
        VALUES (source.id, source.p1, source.p2, source.vid)
        """
        self.execute_query(query, (match_id, p1_name, p2_name, video_file))

    def insert_tracking_data(self, tracking_data):
        """
        Insert a batch of tracking data.
        tracking_data: list of dicts, each containing:
          - event_id, match_id, rally_id, timestamp, raw_data (dict)
        """
        import json
        values = []
        for item in tracking_data:
            values.append((
                item['event_id'],
                item['match_id'],
                item['rally_id'],
                item['timestamp'],
                json.dumps(item['raw_data'])
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
            print(f"Inserted {len(values)} tracking events.")
        except Exception as e:
            print(f"Batch insert error: {e}")
        finally:
            cursor.close()

    def insert_match_stats(self, match_id, summary, rallies):
        """
        Save computed stats to MATCH_STATS table.
        """
        import json
        query = """
        INSERT INTO MATCH_STATS (MATCH_ID, SUMMARY_JSON, RALLIES_JSON)
        SELECT %s, PARSE_JSON(%s), PARSE_JSON(%s)
        """
        self.execute_query(query, (match_id, json.dumps(summary), json.dumps(rallies)))
        print(f"Saved stats for match {match_id}")

    def insert_coaching_insight(self, match_id, prompt, response, processed_json=None):
        """
        Save LLM interaction to COACHING_INSIGHTS table.
        """
        import json
        processed_str = json.dumps(processed_json) if processed_json else None
        
        query = """
        INSERT INTO COACHING_INSIGHTS (MATCH_ID, PROMPT_TEXT, LLM_RESPONSE_TEXT, PROCESSED_RESPONSE_JSON)
        SELECT %s, %s, %s, PARSE_JSON(%s)
        """
        self.execute_query(query, (match_id, prompt, response, processed_str))
        print(f"Saved coaching insight for match {match_id}")


import uuid
import datetime

class TrackingDB:
    """
    High-level wrapper for tracking data storage.
    Handles buffering and batch inserts.
    """
    def __init__(self):
        self.db = SnowflakeDB()
        self.buffer = []
        self.buffer_size = 100
        
    def connect(self):
        return self.db.connect()
        
    def create_new_match(self, video_file, p1_name="Player 1", p2_name="Player 2"):
        """Create a new match record and return its ID."""
        match_id = str(uuid.uuid4())
        self.db.insert_match(match_id, p1_name, p2_name, video_file)
        return match_id
        
    def add_event(self, match_id, frame_num, ball_pos, p1_pose=None, p2_pose=None, event_type="tracking"):
        """Buffer a tracking event."""
        # Normalize data structure
        # Ball: (x, y)
        # Players: list of (x,y) keypoints
        
        data = {
            "frame": frame_num,
            "ball": {"x": float(ball_pos[0]), "y": float(ball_pos[1])} if ball_pos else None,
            "p1": self._serialize_pose(p1_pose),
            "p2": self._serialize_pose(p2_pose),
            "event": event_type
        }
        
        event_record = {
            "event_id": str(uuid.uuid4()),
            "match_id": match_id,
            "rally_id": None, # Could be set if we tracked rallies
            "timestamp": datetime.datetime.now().isoformat(),
            "raw_data": data
        }
        
        self.buffer.append(event_record)
        
        if len(self.buffer) >= self.buffer_size:
            self.flush()
            
    def _serialize_pose(self, pose):
        """Convert pose keypoints to list of dicts."""
        if pose is None:
            return None
        # Assuming pose is a list/array of [x, y] or [x, y, conf]
        try:
            return [{"x": float(k[0]), "y": float(k[1])} for k in pose]
        except:
            return None
            
    def flush(self):
        """Force write buffer to DB."""
        if self.buffer:
            self.db.insert_tracking_data(self.buffer)
            self.buffer = []

    def close(self):
        self.flush()
        self.db.close()
