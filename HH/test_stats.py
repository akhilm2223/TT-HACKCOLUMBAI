import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from HH.stats_engine import StatsEngine
import json
import numpy as np

def generate_dummy_data():
    """Create a fake match with 2 rallies."""
    events = []
    frame_idx = 0
    
    # Rally 1: 3 shots (L->R, R->L, L->R)
    # Shot 1: L->R (P1 serve)
    for i in range(20):
        events.append({
            "raw_data": {
                "frame": frame_idx, 
                "timestamp": i*0.033,
                "ball": {"x": 100 + i*15, "y": 300 - i*2} # Moving Right
            }
        })
        frame_idx += 1
        
    # Shot 2: R->L (P2 return)
    for i in range(25):
        events.append({
            "raw_data": {
                "frame": frame_idx,
                "timestamp": frame_idx*0.033,
                "ball": {"x": 400 - i*12, "y": 260 + i*1} # Moving Left
            }
        })
        frame_idx += 1

    # Gap (Walking to pick up ball)
    frame_idx += 100 
    
    # Rally 2: Short serve
    for i in range(15):
        events.append({
            "raw_data": {
                "frame": frame_idx,
                "timestamp": frame_idx*0.033,
                "ball": {"x": 100 + i*10, "y": 300} 
            }
        })
        frame_idx += 1
        
    return events

def test_engine():
    print("--- Testing Stats Engine ---")
    
    # 1. Generate Data
    data = generate_dummy_data()
    print(f"Generated {len(data)} raw frames.")
    
    # 2. Initialize Engine
    engine = StatsEngine()
    
    # 3. Process
    result = engine.process_match(data)
    
    # 4. Verify Output
    print("\n--- Match Summary ---")
    print(json.dumps(result['match_summary'], indent=2))
    
    print(f"\n--- Rallies Found: " + str(len(result['rallies'])) + " ---")
    for r in result['rallies']:
        print(f"Rally {r['id']}: {r['shot_count']} shots, Duration: {r['duration_sec']}s")
        print(f"  Intensity: {r['intensity_score']} | P1 Dist: {r['player_stats']['p1_distance']}")
        for s in r['shots']:
            print(f"  -> Shot: {s['direction']} [{s['type']}] | Speed: {s['speed']}")
            print(f"     Zone: {s['placement_zone']} | Arc: {s['net_clearance']} | Difficulty: {s['difficulty_score']}")

if __name__ == "__main__":
    test_engine()
