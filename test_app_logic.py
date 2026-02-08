import json
import pandas as pd
import os
import numpy as np

def test_logic():
    print("Testing App Logic...")
    json_path = "output_videos/table_tennis_analysis.json"
    
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)
        
    print("JSON Loaded.")
    
    all_shots_raw = data.get("shots", [])
    behavioral = data.get("behavioral_metrics", {})
    
    # 1. KPI Extraction (Calculated)
    knee_angles = []
    stance_widths = []
    tactical_scores = []
    landing_heatmap = {}
    
    shot_map = {s['shot_id']: s for s in all_shots_raw if 'shot_id' in s}

    for s in all_shots_raw:
        # Biometrics
        skel = s.get('skeleton_analysis', {})
        if skel and isinstance(skel, dict) and skel.get('has_skeleton'):
            k = skel.get('avg_knee_angle')
            w = skel.get('stance_width')
            if k: knee_angles.append(k)
            if w: stance_widths.append(w)
            
        # Tactics
        speed = s.get('speed', 0)
        depth = 1 if s.get('landing',{}).get('depth') == 'deep' else 0.5
        tactical_scores.append(speed * depth if speed else 50)
        
        # Heatmap
        landing = s.get('landing', {})
        if landing:
            zone = landing.get('zone')
            if zone:
                landing_heatmap[zone] = landing_heatmap.get(zone, 0) + 1

    # Aggregations
    avg_knee = np.mean(knee_angles) if knee_angles else 0
    avg_width = np.mean(stance_widths) if stance_widths else 0
    
    aggression = behavioral.get('player', {}).get('aggression_index', {}).get('value', 0)
    avg_tactical = aggression * 100 if aggression else (np.mean(tactical_scores) if tactical_scores else 50)
    
    print(f"KPIs Calculated: IQ={avg_tactical:.1f}, Knee={avg_knee:.1f}, Width={avg_width:.1f}")
    print(f"Heatmap Keys: {landing_heatmap.keys()}")

    # Rhythm
    rallies = data.get("rallies", [])
    intervals = []
    for r in rallies:
        shots = r.get('shots', [])
        if len(shots) > 1:
            r_shots = [shot_map.get(sid) for sid in shots if shot_map.get(sid)]
            r_shots.sort(key=lambda x: x.get('t_contact', 0))
            for i in range(1, len(r_shots)):
                intervals.append(r_shots[i]['t_contact'] - r_shots[i-1]['t_contact'])
    
    avg_rhythm = np.std(intervals) if intervals else 0.0
    print(f"Rhythm: {avg_rhythm:.2f}")

    print("Test Complete.")

if __name__ == "__main__":
    test_logic()
