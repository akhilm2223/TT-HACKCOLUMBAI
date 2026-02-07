from modules.snowflake_db import TrackingDB
from modules.llm_coach import LLMCoach
import time

def verify():
    print("--- 1. Creating Tracking DB Connection ---")
    track_db = TrackingDB()
    if not track_db.connect():
        print("Failed to connect to DB")
        return

    print("--- 2. Creating Dummy Match ---")
    match_id = track_db.create_new_match("test_video.mp4", "Test Player 1", "Test Player 2")
    print(f"Match ID: {match_id}")

    print("--- 3. Inserting Dummy Tracking Data ---")
    # Simulate 50 frames
    for i in range(50):
        # Bounce at frame 25
        is_bounce = (i == 25)
        event_type = "bounce" if is_bounce else "tracking"
        
        # Fake ball moving
        ball_pos = (100 + i*2, 200 + i*3)
        
        track_db.add_event(match_id, i, ball_pos, event_type=event_type)
    
    # Force flush
    track_db.flush()
    print("Data flushed to Snowflake")

    print("--- 4. Generating AI Insight ---")
    coach = LLMCoach()
    # Wait a moment for data to be available (usually instant for inserts, but good practice)
    time.sleep(2)
    
    insight = coach.get_ai_insight(match_id)
    print(insight)

if __name__ == "__main__":
    verify()
