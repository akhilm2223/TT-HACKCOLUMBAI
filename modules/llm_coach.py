"""
Cortex-Powered Coaching Engine for Break Point
All reasoning happens inside Snowflake via Cortex COMPLETE.
Cross-match context is pulled via Cortex vector search (EMBED_TEXT_768 + VECTOR_COSINE_SIMILARITY).
No external LLM calls — everything stays in Snowflake.
"""
import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

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
        self.model = model

    def connect(self):
        return self.db.connect()

    # ----------------------------------------------------------
    # Build the coaching prompt from structured analysis JSON
    # ----------------------------------------------------------
    def _build_prompt(self, analysis, similar_matches=None):
        """
        Build a Cortex-ready prompt from the pipeline's analysis JSON.
        Includes cross-match context if similar matches are found.
        """
        bm = analysis.get("behavioral_metrics", {})
        player_bm = bm.get("player", {})
        match_bm = bm.get("match", {})
        court = analysis.get("court", {})
        shots = analysis.get("shots", [])
        rallies = analysis.get("rallies", [])
        semantic = analysis.get("semantic_summary", "")

        # Shot breakdown
        fh = [s for s in shots if s.get("hand") == "forehand"]
        bh = [s for s in shots if s.get("hand") == "backhand"]
        short = [s for s in shots if s.get("landing", {}).get("depth") == "short"]
        deep = [s for s in shots if s.get("landing", {}).get("depth") == "long"]

        # Landing zone distribution
        zone_counts = {}
        for s in shots:
            z = s.get("landing", {}).get("zone")
            if z:
                zone_counts[z] = zone_counts.get(z, 0) + 1

        # Cross-match context
        cross_match_ctx = ""
        if similar_matches:
            cross_match_ctx = "\n=== SIMILAR PAST MATCHES ===\n"
            for m in similar_matches[:3]:
                cross_match_ctx += f"- {m['video_file']} (similarity: {m['similarity']:.2f}): {m['semantic_summary']}\n"

        prompt = f"""You are an elite Table Tennis Performance Analyst and Mental Coach.
Analyze this match data and provide specific, actionable coaching advice.

=== MATCH OVERVIEW ===
{semantic}

=== COURT GEOMETRY ===
Table width: {court.get('width_px', 'N/A')}px, height: {court.get('height_px', 'N/A')}px
Net Y: {court.get('net_y', 'N/A')}

=== BEHAVIORAL METRICS (Player) ===
- Footwork drop %: {player_bm.get('footwork_drop_pct', 'N/A')}
- Avg footwork speed: {player_bm.get('avg_footwork_speed', 'N/A')} px/f
- Avg arm speed: {player_bm.get('avg_arm_speed', 'N/A')} px/f
- Aggression index: {player_bm.get('aggression_index', {}).get('value', 'N/A')} (0-1 scale)

=== MATCH STATS ===
- Total shots: {match_bm.get('total_shots', 0)}
- Total rallies: {match_bm.get('total_rallies', 0)}
- Forehand %: {match_bm.get('forehand_pct', 0)}, Backhand %: {match_bm.get('backhand_pct', 0)}
- Short %: {match_bm.get('short_pct', 0)}, Long %: {match_bm.get('long_pct', 0)}
- Avg rally duration: {match_bm.get('avg_rally_duration', 0)}s

=== SHOT PLACEMENT ZONES ===
{json.dumps(zone_counts, indent=2)}

=== TOP RALLIES (longest) ===
{json.dumps(sorted(rallies, key=lambda r: r.get('length', 0), reverse=True)[:3], indent=2)}
{cross_match_ctx}
=== COACHING TASK ===
Based ONLY on the data above:
1. **Main Weakness**: Identify the primary tactical or mental leak (timing, footwork, passivity, placement).
2. **Pattern Analysis**: What patterns emerge from shot placement and rally outcomes?
3. **Pressure Response**: How does the player perform in longer rallies (pressure)? Is there footwork or aggression drop?
4. **Corrective Action**: Give 2-3 specific, actionable drills or tactical changes.
5. **Opponent Strategy**: Based on landing zones and rally patterns, what is the opponent exploiting?

Be concise, data-driven, and specific. Reference actual numbers from the metrics above."""

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
        if not self.db.conn:
            if not self.db.connect():
                return "Error: Could not connect to Snowflake."

        # 1. Fetch this match's analysis
        print(f"[Cortex] Fetching analysis for match {match_id}...")
        analysis = self.db.get_analysis(match_id)
        if not analysis:
            return f"Error: No analysis found for match {match_id}."

        # 2. Find similar past matches via vector search
        print("[Cortex] Searching for similar matches (vector similarity)...")
        semantic = analysis.get("semantic_summary", "")
        similar = []
        if semantic:
            try:
                similar = self.db.find_similar_matches(semantic, top_k=5)
                # Exclude self
                similar = [m for m in similar if m["match_id"] != match_id]
                if similar:
                    print(f"[Cortex] Found {len(similar)} similar matches")
            except Exception as e:
                print(f"[Cortex] Vector search skipped: {e}")

        # 3. Build prompt with cross-match context
        prompt = self._build_prompt(analysis, similar_matches=similar if similar else None)

        # 4. Call Cortex COMPLETE (reasoning happens inside Snowflake)
        print(f"[Cortex] Calling COMPLETE({self.model})...")
        response = self.db.cortex_complete(prompt, model=self.model)

        if not response:
            return "Error: Cortex COMPLETE returned no response."

        print(f"[Cortex] Response received ({len(response)} chars)")

        # 5. Save insight to Snowflake
        if save_insight:
            try:
                self.db.insert_coaching_insight(
                    match_id, prompt, response,
                    processed_json={"model": self.model, "similar_matches": len(similar)}
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
