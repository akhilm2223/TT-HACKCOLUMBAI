import numpy as np
import json
from collections import defaultdict
from scipy.signal import savgol_filter

class StatsEngine:
    def __init__(self, fps=30):
        self.fps = fps
        self.dt = 1.0 / fps
        # Table dimensions (standard ITTF)
        self.TABLE_LENGTH = 274.0  # cm (or relative units)
        self.TABLE_WIDTH = 152.5   # cm
        
    def process_match(self, match_data):
        """
        Main pipeline: Enriched JSON -> Enhanced Stats
        match_data: Single JSON object containing 'frames', 'shots', 'rallies', 'court'
        """
        if not match_data:
            return {"error": "Invalid match data format"}

        # Extract core data
        self.court = match_data.get("court", {})
        self.net_y = self.court.get("net_y", 335.0) # Default if missing
        
        # 1. Enrich Shots with Advanced Metrics
        enriched_rallies = []
        
        # Process rallies existing in the input
        # Handle new format where rallies is a list of dicts with 'shots' as IDs
        for rally in match_data.get("rallies", []):
            rally_id = rally.get("rally_id")
            # Find shots for this rally
            rally_shot_ids = rally.get("shots", [])
            
            # Get actual shot objects from the top-level 'shots' list
            all_shots = match_data.get("shots", [])
            rally_shots_data = [
                s for s in all_shots 
                if s.get("shot_id") in rally_shot_ids
            ]
            
            # Analyze this rally
            stats = self._analyze_rally_enriched(rally_id, rally, rally_shots_data, match_data)
            enriched_rallies.append(stats)
            
        # 2. Aggregated Match Stats
        match_summary = self._aggregate_match_stats(enriched_rallies)
        
        return {
            "match_summary": match_summary,
            "rallies": enriched_rallies
        }

    def _analyze_rally_enriched(self, rally_id, rally_meta, shots_data, full_data):
        """
        Compute shot-by-shot metrics using the pre-detected shots and adding new physics metrics.
        """
        # Calculate Rhythm (Inter-shot intervals)
        intervals = []
        if len(shots_data) > 1:
            # Sort by time just in case
            sorted_shots = sorted(shots_data, key=lambda x: x.get('t_contact', 0))
            for i in range(1, len(sorted_shots)):
                interval = sorted_shots[i]['t_contact'] - sorted_shots[i-1]['t_contact']
                intervals.append(interval) 
            rhythm_consistency = np.std(intervals) if intervals else 0
        else:
            rhythm_consistency = 0

        # Enhance each shot with new metrics
        enriched_shots = []
        for shot in shots_data:
            # 1. Contact Height & Timing Analysis
            # We need ball trajectory AROUND the contact time to find peak
            contact_t = shot.get('t_contact')
            # Handle list vs dict for samples (JSON structure check)
            samples = full_data.get('frame_level_perception', {}).get('samples', [])
            trajectory = self._get_trajectory_segment(samples, contact_t - 0.5, contact_t + 0.5)
            
            # Timing Score
            timing_stats = self._calculate_timing_metrics(shot, trajectory)
            
            # Aggression/Tactical Score
            tactical_stats = self._calculate_aggression_opportunity(shot, timing_stats['contact_height'])
            
            # Merge into shot object
            shot_enriched = shot.copy()
            shot_enriched.update(timing_stats)
            shot_enriched.update(tactical_stats)
            
            # Add Skeleton Analysis if available (at contact frame)
            # Make sure shot dict has 'skeleton_analysis' key
            shot_enriched['skeleton_analysis'] = self._analyze_skeleton(full_data, contact_t)
            
            enriched_shots.append(shot_enriched)

        return {
            "id": rally_id,
            "duration_sec": rally_meta.get('t_end', 0) - rally_meta.get('t_start', 0),
            "shot_count": len(shots_data),
            "rhythm_consistency": round(rhythm_consistency, 2),
            "shots": enriched_shots
        }

    def _get_trajectory_segment(self, frames, t_start, t_end):
        """Extract ball sequence [t, x, y] for a time window."""
        segment = []
        for f in frames:
            if t_start <= f['t'] <= t_end:
                b = f.get('ball', {})
                # Handle simplified ball object in new JSON
                if b and b.get('x') is not None:
                    segment.append({'t': f['t'], 'y': b['y'], 'x': b['x']})
        return segment

    def _calculate_timing_metrics(self, shot, trajectory):
        """
        Calculate if shot was taken at Peak, Early (Rising), or Late (Falling).
        Input: shot dict, trajectory list [{'t', 'y', 'x'}]
        """
        if not trajectory:
            return {"timing": "Unknown", "contact_height": 0, "timing_score": 0}
            
        # Find contact frame (closest matching timestamp)
        contact_t = shot.get('t_contact', 0)
        contact_point = min(trajectory, key=lambda p: abs(p['t'] - contact_t))
        contact_y = contact_point['y']
        
        # Find Peak Height (Minimum Y value in image coords) in this trajectory segment
        # We search a bit before contact to find the bounce peak
        peak_point = min(trajectory, key=lambda p: p['y'])
        peak_y = peak_point['y']
        
        # Calculate Height Diff (Positive = Hit below peak)
        # Image coords: Peak Y is smaller. So Contact Y - Peak Y = drop amount in pixels
        drop_pixels = contact_y - peak_y
        
        # Heuristics (Pixels)
        if drop_pixels < 15: # < ~5-10cm
            timing = "Peak"
            score = 100
        elif contact_point['t'] < peak_point['t']: 
            timing = "Early (Rising)"
            score = 80 # Taking it early is often good for aggression
        else:
            timing = "Late (Falling)"
            score = max(0, 100 - (drop_pixels / 2)) # Penalty for dropping too low
            
        # Ball Height relative to Net (Positive = Above Net)
        height_over_net = self.net_y - contact_y
            
        return {
            "timing_class": timing,
            "timing_score": round(score),
            "height_over_net": height_over_net,
            "contact_height": contact_y
        }

    def _calculate_aggression_opportunity(self, shot, contact_height_y):
        """
        Detect Tactical Errors: Passive shot on High Ball vs Risky shot on Low Ball.
        """
        # Height relative to Net
        rel_height = self.net_y - contact_height_y # Positive = Above net
        
        shot_type = shot.get('shot_type', 'unknown').lower()
        
        tactical_assessment = "Neutral"
        opportunity_score = 50 # 0=Bad Choice, 50=Neutral, 100=Great Choice
        
        # Scenario 1: High Ball Opportunity (> 40px above net ~ 15cm)
        if rel_height > 40:
            if shot_type in ['smash', 'drive', 'offensive']:
                tactical_assessment = "Good Aggression"
                opportunity_score = 100
            elif shot_type in ['push', 'block', 'defensive']:
                tactical_assessment = "Passive Error" # Missed opportunity
                opportunity_score = 20
        
        # Scenario 2: Low Ball Risk (< 0px, below net)
        elif rel_height < 0:
            if shot_type in ['smash', 'flat hit']:
                tactical_assessment = "High Risk Error"
                opportunity_score = 10
            elif shot_type in ['loop', 'push', 'drop']:
                tactical_assessment = "Smart Safe Play"
                opportunity_score = 90
                
        return {
            "tactical_class": tactical_assessment,
            "tactical_score": opportunity_score
        }

    def _analyze_skeleton(self, full_data, contact_t):
        """
        Extract pre-calculated Knee/Shoulder angles at contact time if available.
        """
        # Find frame samples near contact
        samples = full_data.get('frame_level_perception', {}).get('samples', [])
        frame = min(samples, key=lambda f: abs(f['t'] - contact_t), default=None)
        
        if not frame: return {}
        
        player = frame.get('player', {})
        if not player: return {}
        
        # New format has explicit angles
        knee_left = player.get('knee_angle_left')
        knee_right = player.get('knee_angle_right')
        shoulder_left = player.get('shoulder_angle_left')
        shoulder_right = player.get('shoulder_angle_right')
        
        # Calculate averages if both present, or use single value
        avg_knee = None
        if knee_left and knee_right:
            avg_knee = (knee_left + knee_right) / 2
        elif knee_left: avg_knee = knee_left
        elif knee_right: avg_knee = knee_right
            
        avg_shoulder = None
        if shoulder_left and shoulder_right:
            avg_shoulder = (shoulder_left + shoulder_right) / 2
        elif shoulder_left: avg_shoulder = shoulder_left
        elif shoulder_right: avg_shoulder = shoulder_right
            
        stance_width = player.get('stance_width', 0)
            
        return {
            "has_skeleton": True if avg_knee is not None else False,
            "avg_knee_angle": round(avg_knee, 1) if avg_knee else None,
            "avg_shoulder_angle": round(avg_shoulder, 1) if avg_shoulder else None,
            "stance_width": stance_width
        }

    def _aggregate_match_stats(self, rally_stats):
        if not rally_stats:
            return {}
            
        total_shots = sum(r['shot_count'] for r in rally_stats)
        
        # Rhythm consistency (lower is better)
        rhythms = [r['rhythm_consistency'] for r in rally_stats]
        avg_rhythm = np.mean(rhythms) if rhythms else 0
        
        # Timing Stats
        timings = [s.get('timing_score', 0) for r in rally_stats for s in r['shots']]
        avg_timing = np.mean(timings) if timings else 0

        # Tactical Stats
        tactics = [s.get('tactical_score', 0) for r in rally_stats for s in r['shots']]
        avg_tactics = np.mean(tactics) if tactics else 0

        # Shot stats
        shot_types = defaultdict(int)
        landing_zones = defaultdict(int)
        difficulty_scores = []
        knee_angles = []
        shoulder_angles = []
        stance_widths = []
        speeds = []
        
        for r in rally_stats:
            for s in r['shots']:
                shot_types[s.get('shot_type', 'unknown')] += 1
                # Estimate difficulty if not present (could be added to _analyze_rally_enriched)
                difficulty_scores.append(s.get('difficulty_score', 0))
                
                # Biomechanics
                skel = s.get('skeleton_analysis', {})
                if skel.get('has_skeleton'):
                    if skel.get('avg_knee_angle'): knee_angles.append(skel['avg_knee_angle'])
                    if skel.get('avg_shoulder_angle'): shoulder_angles.append(skel['avg_shoulder_angle'])
                    if skel.get('stance_width'): stance_widths.append(skel['stance_width'])
                    
                # Speed
                # If speed is in shot object
                if s.get('speed'): speeds.append(s['speed'])
                # Or try to extract from raw JSON if available (but 's' here is the shot object)
                
                # Landing Zone Heatmap
                landing = s.get('landing', {})
                if landing and landing.get('zone'):
                    landing_zones[landing['zone']] += 1

        return {
            "total_rallies": len(rally_stats),
            "total_shots": total_shots,
            "avg_rhythm_score": round(avg_rhythm, 2),
            "avg_timing_score": round(avg_timing, 1),
            "avg_tactical_score": round(avg_tactics, 1),
            "avg_shot_speed": round(np.mean(speeds), 1) if speeds else 0,
            "avg_knee_angle": round(np.mean(knee_angles), 1) if knee_angles else 0,
            "avg_shoulder_angle": round(np.mean(shoulder_angles), 1) if shoulder_angles else 0,
            "avg_stance_width": round(np.mean(stance_widths), 1) if stance_widths else 0,
            "shot_type_distribution": dict(shot_types),
            "landing_zone_heatmap": dict(landing_zones),
            "avg_shot_difficulty": round(np.mean(difficulty_scores), 1) if difficulty_scores else 0
        }
