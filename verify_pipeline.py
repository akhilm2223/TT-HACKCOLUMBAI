from modules.snowflake_db import TrackingDB
from modules.dedalus_coach import DedalusCoach
import time
import json

def verify():
    print("--- 1. Creating Tracking DB Connection ---")
    track_db = TrackingDB()
    if not track_db.connect():
        print("Failed to connect to DB")
        # Proceed anyway for simulation test if DB fails
    
    print("--- 2. Creating Dummy Match ---")
    match_id = "test_match_verify_123"
    
    print("--- 3. Preparing Mock Stats (Skipping DB insert for speed) ---")
    # Mock data structure expected by DedalusCoach
    mock_stats = {
        "rallies": [
            {
                "id": "rally_1",
                "shots": [
                    {"shot_type": "serve", "skeleton_analysis": {"avg_knee_angle": 135}},
                    {"shot_type": "push", "skeleton_analysis": {"avg_knee_angle": 155}},
                    {"shot_type": "loop", "skeleton_analysis": {"avg_knee_angle": 140}}
                ],
                "rhythm_consistency": 0.8
            }
        ]
    }

    print("--- 4. Generating AI Insight with DedalusCoach ---")
    coach = DedalusCoach()
    
    # Force simulation mode if no API key, or real if available
    print(f"API Key present: {bool(coach.api_key)}")
    
    insight_json = coach.analyze_match(mock_stats)
    print("\n[Result JSON]:")
    print(insight_json)
    
    try:
        parsed = json.loads(insight_json)
        print("\n✅ Verification SUCCESS: Valid JSON received")
        print(f"Confidence Score: {parsed.get('confidence_score')}")
    except json.JSONDecodeError:
        print("\n❌ Verification FAILED: Invalid JSON")

if __name__ == "__main__":
    verify()
