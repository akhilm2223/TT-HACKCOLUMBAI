import json
import os
import sys

# Ensure root directory is in path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import dependencies
try:
    from modules.snowflake_db import SnowflakeDB
    from HH.stats_engine import StatsEngine
except ImportError:
    # Fallback for different run contexts
    from .snowflake_db import SnowflakeDB
    # If HH is not a package, we might need dynamic import or assume path is set
    import importlib.util
    spec = importlib.util.spec_from_file_location("StatsEngine", os.path.join(project_root, "HH", "stats_engine.py"))
    stats_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stats_module)
    StatsEngine = stats_module.StatsEngine


try:
    from HH.stats_engine import StatsEngine
except ImportError:
    # Fallback if running from root
    from HH.stats_engine import StatsEngine


class CortexCoach:
    """
    AI coaching engine powered entirely by Snowflake Cortex.
    - Pulls match data from ANALYSIS_OUTPUT (VARIANT)
    - Finds similar past matches via vector search
    - Reasons via Cortex COMPLETE (llama3.1-70b)
    - Stores insights in COACHING_INSIGHTS
    """

    def __init__(self, model='llama3.1-70b'):

        self.db = SnowflakeDB()
        self.engine = StatsEngine()

    def get_match_summary(self, match_id, db_save=True):
        """
        Fetch raw tracking data, summarize it, and optionally save to DB.
        Assumes data is stored as a single JSON blob or handles chunk errors.
        """
        # 1. Fetch data
        query = """
        SELECT RAW_DATA 
        FROM TRACKING_EVENTS 
        WHERE MATCH_ID = %s 
        ORDER BY TIMESTAMP ASC
        """
        cursor = self.db.execute_query(query, (match_id,))
        rows = cursor.fetchall()
        
        if not rows:
            return "No tracking data found for this match."

        # 2. Reconstruct Match Data (Handle full JSON vs Stream)
        match_data = None
        try:
            # We assume the first row contains the full JSON for this unified structure
            # (or we would need logic to merge multiple rows if it was streamed)
            payload = rows[0][0]
            if isinstance(payload, str):
                match_data = json.loads(payload)
            else:
                match_data = payload
                
            # Basic validation
            if not isinstance(match_data, dict) or "frames" not in match_data:
                # Fallback: maybe it's just a 'raw_data' wrapper event
                if 'raw_data' in match_data: 
                    match_data = match_data['raw_data']
                else:
                    return "Error: DB data format does not match expected JSON structure."
                    
        except Exception as e:
            return f"Error parsing DB data: {e}"

        processed_stats = self.engine.process_match(match_data)
        
        if "error" in processed_stats:
            return processed_stats["error"]

        # 3. Save to DB
        if db_save:
            try:
                self.db.insert_match_stats(
                    match_id, 
                    processed_stats['match_summary'], 
                    processed_stats['rallies']
                )
            except Exception as e:
                print(f"Warning: Failed to save stats to DB: {e}")

        return processed_stats

    def generate_coach_prompt(self, match_stats):
        """
        Create the prompt for the LLM using comprehensive match stats based on 30FPS metrics.
        """
        summary = match_stats.get('match_summary', {})
        rallies = match_stats.get('rallies', [])
        
        # Sort top rallies
        top_rallies = sorted(rallies, key=lambda x: x.get('shot_count', 0), reverse=True)[:3]

        prompt = f"""
        You are an elite Table Tennis Coach (Scientific/Data-Driven).
        
        === MATCH DIAGNOSTICS ===
        1. **Timing & Efficiency** (Score: {summary.get('avg_timing_score', 0)}/100)
           - Tells if player hits at 'Peak' bounce (100) or 'Late/Falling' (<50).
        2. **Tactical Aggression** (Score: {summary.get('avg_tactical_score', 0)}/100)
           - Tells if player attacks High Balls (Good) or is Passive (Bad).
        3. **Rhythm Consistency**: {summary.get('avg_rhythm_score', 0)} (Lower < 0.2 is Pro, > 0.5 is Amateur).
        
        === SHOT METRICS ===
        - Distribution: {json.dumps(summary.get('shot_type_distribution', {}), indent=2)}
        - Avg Shot Difficulty: {summary.get('avg_shot_difficulty', 0)}

        === KEY RALLIES (Logic Check) ===
        {json.dumps(top_rallies, indent=2)}

        === COACHING TASK ===
        Based ONLY on the metrics above, write a brief, punchy coaching assessment:
        1. **Identify the Main Leak**: Is it Timing (hitting late), Tactics (passive), or Consistency?
        2. **Valid vs Invalid Shots**: Specifically mention if they played a "Passive Error" (Push on High Ball) or "High Risk Error" (Smash on Low Ball).
        3. **Corrective Drill**: Give ONE specific drill.
        """
        return prompt

    def get_ai_insight(self, match_id, db_save=True):
        """
        Main entry point: Get stats, build prompt, call LLM, save result.
        """
        print(f"Generating insight for Match {match_id}...")
        
        # 1. Get Stats (fetching raw -> calc -> save)
        stats = self.get_match_summary(match_id, db_save=db_save)
        if isinstance(stats, str): # Error message
            return stats
            
        # 2. Build Prompt
        prompt = self.generate_coach_prompt(stats)
        
        # 3. Call LLM (Simulated)
        # TODO: Integrate actual LLM call (OpenAI/Anthropic)
        print("--- Generated Prompt for LLM ---")
        # print(prompt) # Reduced verbosity
        print("(Prompt generated successfully)")
        print("--------------------------------")
        
        response_text = "Simulated LLM Response: Player 1 demonstrates strong forehand loops..."
        
        # 4. Save Insight (New Step)
        if db_save:
            try:
                self.db.insert_coaching_insight(
                    match_id,
                    prompt,
                    response_text,
                    processed_json={"summary": "Player 1 is consistent", "drill": "Forehand loop"} # Placeholder post-processing
                )
            except Exception as e:
                print(f"Warning: Failed to save insight to DB: {e}")
        
        return response_text
