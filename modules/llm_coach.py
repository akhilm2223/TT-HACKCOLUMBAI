"""
Cortex-Powered Coaching Engine for Break Point
All reasoning happens inside Snowflake via Cortex COMPLETE.
Cross-match context is pulled via Cortex vector search (EMBED_TEXT_768 + VECTOR_COSINE_SIMILARITY).
No external LLM calls — everything stays in Snowflake.
"""
import json
import os
import sys
import requests
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Load environment variables
load_dotenv()

# Import dependencies
try:
    from modules.snowflake_db import SnowflakeDB
except ImportError:
    from .snowflake_db import SnowflakeDB


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
        
        # Initialize Kimi K2 Client
        self.api_key = os.getenv("KIMI_K2_THINKING_API_KEY")
        self.api_url = "https://api.k2think.ai/v1/chat/completions"
        self.model_id = "MBZUAI-IFM/K2-Think-v2" # As specified in curl
        
        if not self.api_key:
            print("Warning: KIMI_K2_THINKING_API_KEY not found in environment variables.")

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
            if not isinstance(match_data, dict):
                # Fallback: maybe it's just a 'raw_data' wrapper event
                if 'raw_data' in match_data: 
                    match_data = match_data['raw_data']
                else:
                    return "Error: DB data format does not match expected JSON structure."
            
            # Additional check for new structure
            if "frames" not in match_data and "frame_level_perception" not in match_data:
                 return "Error: JSON missing critical 'frames' or 'frame_level_perception' keys."
                    
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
        Implements the 'Biomechanical Engine' persona for forensic audit.
        """
        summary = match_stats.get('match_summary', {})
        rallies = match_stats.get('rallies', [])
        
        # Sort by shot count to prioritize interesting rallies
        # Increased limit for broader analysis as requested
        key_rallies = sorted(rallies, key=lambda x: x.get('shot_count', 0), reverse=True)[:20]

        prompt = f"""
# ROLE & OBJECTIVE
You are the **"Biomechanical Engine,"** an elite, data-driven Table Tennis Analyst. Your goal is to perform a **comprehensive, shot-by-shot forensic audit** of a player's match performance based on computer vision telemetry.

**CRITICAL INSTRUCTION:** Do NOT summarize. Do NOT select only the "top" moments. You must analyze **EVERY** rally and relevant shot provided in the `key_rallies` JSON array to build a complete picture of the player's consistency and failure points.

# DATA INTERPRETATION LOGIC
You will receive JSON data containing `Match Diagnostics`, `Shot Metrics`, and `Key Rallies`. Use the following logic to interpret the numbers:

1.  **Biomechanics (The "Engine"):**
    * **Knee Angle:** < 140° is ideal (athletic stance). > 150° is "Standing too straight" (bad leverage).
    * **Stance Width:** > 100px is stable. < 50px is "Narrow/Off-balance."
    * **Shoulder Angle:** Measures rotation. Low numbers (<50°) usually indicate poor backswing or arm-only shots.
2.  **Timing (The "Contact"):**
    * **Phase:** "Peak" (100 score) is optimal. "Late/Falling" is a defensive leak. "Early/Rising" is aggressive but risky.
3.  **Tactics (The "Brain"):**
    * **Gap Analysis:** Compare `height_over_net` vs. `shot_type`.
        * *Major Error:* Pushing a ball with `height_over_net` > 20 (should be attacked).
        * *Good Play:* Pushing a ball with `height_over_net` < 0 (low/difficult).

# INPUT DATA

## MATCH DIAGNOSTICS (Global Stats)
* **Biomechanics Average:** 
    - Knees: {summary.get('avg_knee_angle', 'N/A')} deg
    - Stance Width: {summary.get('avg_stance_width', 'N/A')} px
    - Shoulders: {summary.get('avg_shoulder_angle', 'N/A')} deg
* **Tactical Aggression Score:** {summary.get('avg_tactical_score', 0)}/100
* **Rhythm Consistency:** {summary.get('avg_rhythm_score', 0)}
* **Shot Speed Avg:** {summary.get('avg_shot_speed', 0)} px/s

## SHOT METRICS
* **Distribution:** {json.dumps(summary.get('shot_type_distribution', {}), indent=2)}
* **Placement Heatmap:** {json.dumps(summary.get('landing_zone_heatmap', {}), indent=2)}

## KEY RALLIES (Source Data)
```json
{json.dumps(key_rallies, indent=2)}
```

# OUTPUT STRUCTURE
Generate a detailed report in the following format:

## PART 1: GLOBAL METRICS ANALYSIS
*Analyze the aggregate stats first.*
* **Biomechanics Average:** (Analyze the player's average knee angle and stance width across the whole match. Are they generally too high or too narrow?)
* **Tactical Aggression Score:** (Explain what the score of {summary.get('avg_tactical_score', 0)}/100 implies about their mindset.)
* **Rhythm Consistency:** (Interpret the variance. Is the player robotic (good) or chaotic (bad)?)

## PART 2: FULL RALLY-BY-RALLY LOG
*Iterate through EVERY rally in the JSON. For each rally, output the following details:*

### 📍 Rally [ID] (Duration: [X]s)
* **Sequence:** Describe the flow (e.g., "Opponent Push -> Self Push -> Error").
* **Player Shot Analysis:** (Focus on shots where `player` is "self")
    * **Shot [ID] ([Shot Type]):**
        * **Biometrics:** "Knees: [Angle]° | Shoulders: [Angle]° | Stance: [Width]px"
        * **Timing:** "[Timing Class] (Score: [Score])"
        * **Tactical Verdict:**
            * *If Score > 80:* "✅ **Efficient:** [Explain why based on height/landing]"
            * *If Score < 50:* "⚠️ **CRITICAL ERROR:** [Explain the mismatch. E.g., 'You pushed a high ball (+70 height). This was a smash opportunity. Your knees were locked straight at 155°, preventing explosive movement.']"

## PART 3: PATTERN RECOGNITION & CORRELATION
*Look across all the rallies you just analyzed and find the connection.*
* **The "Death Spiral":** When the player misses, what is the common variable? (e.g., "In 100% of your errors, your Stance Width dropped below 50px.")
* **The "Winning Formula":** When the player scores >90, what are they doing right?

## PART 4: TRAINING PRESCRIPTION
*Based on the Full Audit:*
1.  **Technical Correction:** (Specific biomechanical adjustment).
2.  **Tactical Adjustment:** (Specific decision-making change).
3.  **The Drill:** (One specific drill to address the most frequent error found in the logs).
"""
        return prompt

    # ----------------------------------------------------------
    # Main entry: analyze a match and generate coaching insight
    # ----------------------------------------------------------
    def analyze_match(self, match_id, save_insight=True):
        """
        Full pipeline: fetch analysis from Snowflake -> find similar matches ->
        build prompt -> Cortex COMPLETE -> save insight.
        Returns the coaching text.
        """
        print(f"Generating insight for Match {match_id}...")
        
        # 1. Get Stats (fetching raw -> calc -> save)
        stats = self.get_match_summary(match_id, db_save=db_save)
        if isinstance(stats, str): # Error message
            return stats
            
        # 2. Build Prompt
        prompt = self.generate_coach_prompt(stats)
        
        # 3. Call LLM (Kimi K2 CURL Request)
        print("--- Generated Prompt for LLM ---")
        print("(Prompt generated successfully)")
        print(f"Calling Kimi K2 Thinking (Endpoint: {self.api_url})...")
        
        response_text = "Error: LLM API Key Missing."
        
        if self.api_key:
            try:
                headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": self.model_id,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                }
                
                response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result['choices'][0]['message']['content']
                    print("--- LLM Response Received ---")
                else:
                    print(f"LLM API Error: {response.status_code} - {response.text}")
                    response_text = f"Error calling Kimi K2: {response.text}"
                    
            except Exception as e:
                print(f"LLM Connection Error: {e}")
                response_text = f"Error connecting to Kimi K2: {e}"
        else:
            print("Simulation Mode due to missing API Key.")
            response_text = "Simulated LLM Response: Player 1 demonstrates strong forehand loops..."
        
        # 4. Save Insight (New Step)
        if db_save:
            try:
                # Basic post-processing placeholder
                processed_json = {"raw_response": response_text[:200] + "..."} 
                
                self.db.insert_coaching_insight(
                    match_id,
                    prompt,
                    response_text,
                    processed_json=processed_json
                )
                print(f"[Cortex] Insight saved to COACHING_INSIGHTS")
            except Exception as e:
                print(f"[Cortex] Failed to save insight: {e}")

        return response

    # ----------------------------------------------------------
    # Quick query: ask a question about a match
    # ----------------------------------------------------------
    def ask(self, match_id, question):
        """
        Ask a specific question about a match. Pulls analysis + similar matches,
        adds the question to the prompt, and returns Cortex's answer.
        """
        if not self.db.conn:
            if not self.db.connect():
                return "Error: Could not connect to Snowflake."

        analysis = self.db.get_analysis(match_id)
        if not analysis:
            return f"No analysis for match {match_id}."

        semantic = analysis.get("semantic_summary", "")
        similar = []
        if semantic:
            try:
                similar = self.db.find_similar_matches(question, top_k=3)
                similar = [m for m in similar if m["match_id"] != match_id]
            except Exception:
                pass

        base_prompt = self._build_prompt(analysis, similar_matches=similar if similar else None)
        full_prompt = base_prompt + f"\n\n=== USER QUESTION ===\n{question}\n\nAnswer concisely and specifically."

        return self.db.cortex_complete(full_prompt, model=self.model)


# Backwards compatibility alias
LLMCoach = CortexCoach
