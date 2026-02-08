"""
Dedalus Labs Multi-Agent Coaching Engine for Break Point AI Coach

This module implements a multi-agent system using the Dedalus Labs SDK.
Each agent specializes in a specific analysis domain:
- Biomechanics Agent: Knee angles, stance width, posture analysis
- Tactical Agent: Shot selection, aggression opportunities
- Timing Agent: Peak/Early/Late contact analysis
- Mental Agent: Pattern detection, fatigue, pressure behavior

The orchestrator combines insights into the final output format:
- 3 Key Findings
- 3 Actionable Recommendations  
- 1 Mental Pattern Insight
- Confidence Score
"""

import os
import sys
import asyncio
import json
import random
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Dedalus SDK imports
try:
    from dedalus_labs import AsyncDedalus, DedalusRunner
    from dedalus_labs.utils.stream import stream_async
    DEDALUS_AVAILABLE = True
except ImportError:
    DEDALUS_AVAILABLE = False
    # Only print warning if we expect it to work (has API key)
    if os.getenv("DEDALUSLABS_API_KEY"):
        print("[DedalusCoach] Warning: dedalus_labs not installed. Run: pip install dedalus_labs")

# Local imports
try:
    from modules.snowflake_db import SnowflakeDB
    from modules.snowflake_mcp import SNOWFLAKE_TOOLS
except ImportError:
    try:
        from snowflake_db import SnowflakeDB
        try:
            from snowflake_mcp import SNOWFLAKE_TOOLS
        except ImportError:
            SNOWFLAKE_TOOLS = []
    except ImportError:
        SNOWFLAKE_TOOLS = []


# ═══════════════════════════════════════════════════════════════════════════════
# LOCAL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_biomechanics(knee_angle: float, shoulder_angle: float, stance_width: float) -> dict:
    """Evaluate player biomechanics for a shot."""
    issues = []
    score = 100
    if knee_angle < 120:
        issues.append(f"Knee angle too bent ({knee_angle}°) - may slow recovery")
        score -= 15
    elif knee_angle > 160:
        issues.append(f"Knees too straight ({knee_angle}°) - reduces power generation")
        score -= 20
    if stance_width < 80:
        issues.append(f"Stance too narrow ({stance_width}px) - limits balance and reach")
        score -= 25
    elif stance_width > 200:
        issues.append(f"Stance too wide ({stance_width}px) - may slow lateral movement")
        score -= 10
    if shoulder_angle and shoulder_angle < 30:
        issues.append(f"Limited shoulder rotation ({shoulder_angle}°) - reduces spin potential")
        score -= 15
    return {
        "assessment": "Optimal" if not issues else "Needs Adjustment",
        "score": max(0, score),
        "issues": issues if issues else ["Biomechanics within optimal range"],
    }

def score_tactical_decision(ball_height_over_net: float, shot_type: str) -> dict:
    """Evaluate shot selection based on ball position."""
    shot_type_lower = shot_type.lower()
    if ball_height_over_net > 40:
        if shot_type_lower in ['smash', 'drive', 'loop', 'offensive']:
            return {"verdict": "Good Aggression", "score": 100, "explanation": f"Correctly attacked high ball (+{ball_height_over_net}px)"}
        else:
            return {"verdict": "Passive Error", "score": 25, "explanation": f"Pushed a high ball (+{ball_height_over_net}px)", "recommendation": "Attack balls >15cm above net"}
    elif ball_height_over_net < 0:
        if shot_type_lower in ['push', 'drop', 'block', 'defensive']:
            return {"verdict": "Smart Safe Play", "score": 90, "explanation": f"Safely handled low ball"}
        else:
            return {"verdict": "High Risk Error", "score": 15, "explanation": f"Risky attack on low ball", "recommendation": "Use controlled shots on balls below net"}
    return {"verdict": "Neutral", "score": 60, "explanation": "Standard shot on neutral ball"}

def evaluate_timing(timing_class: str, timing_score: int) -> dict:
    """Analyze shot timing quality."""
    assessments = {
        "Peak": {"quality": "Excellent", "explanation": "Contact at apex"},
        "Early (Rising)": {"quality": "Good", "explanation": "Early contact on rising ball"},
        "Late (Falling)": {"quality": "Adjust", "explanation": "Late contact on falling ball, less power"},
        "Unknown": {"quality": "Unknown", "explanation": "Could not determine timing"}
    }
    result = assessments.get(timing_class, assessments["Unknown"])
    result["score"] = timing_score
    return result

def detect_mental_patterns(shots_after_point_loss: List[dict], rhythm_degradation: float, passive_shot_streak: int) -> dict:
    """Detect mental patterns that affect performance."""
    patterns = []
    if shots_after_point_loss:
        passive_count = sum(1 for s in shots_after_point_loss if s.get('shot_type', '').lower() in ['push', 'block', 'defensive'])
        if passive_count > len(shots_after_point_loss) * 0.6:
            patterns.append({"pattern": "Post-Loss Passivity", "insight": "You play safe after losing a rally", "fix": "Reset aggressively"})
    if rhythm_degradation > 0.3:
        patterns.append({"pattern": "Late-Match Fatigue", "insight": f"Rhythm degraded {int(rhythm_degradation*100)}%", "fix": "Practice endurance"})
    if passive_shot_streak >= 4:
        patterns.append({"pattern": "Defensive Lock", "insight": f"Streak of {passive_shot_streak} passive shots", "fix": "Attack after 2 pushes"})
    return patterns[0] if patterns else {"pattern": "Mentally Stable", "insight": "No concerning patterns", "fix": "Maintain composure"}

def calculate_coach_score(biomech_score: int, tactical_score: int, timing_score: int, rhythm_consistency: float) -> dict:
    """Calculate overall coaching confidence score."""
    rhythm_score = max(0, 100 - (rhythm_consistency * 200))
    overall = (0.30 * biomech_score + 0.35 * tactical_score + 0.20 * timing_score + 0.15 * rhythm_score)
    return {"overall_score": round(overall), "confidence": "High" if overall >= 75 else "Medium"}


# ═══════════════════════════════════════════════════════════════════════════════
# DEDALUS COACH CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class DedalusCoach:
    """
    Multi-agent AI coaching engine powered by Dedalus Labs SDK.
    Includes robust SIMULATION MODE for demos/testing when API/Package is missing.
    """
    
    def __init__(self, models: List[str] = None):
        self.models = models or ["anthropic/claude-sonnet-4-20250514", "openai/gpt-4.1"]
        self.api_key = os.getenv("DEDALUSLABS_API_KEY") or os.getenv("DEDALUS_API_KEY")
        
        # Tools
        self.tools = [
            analyze_biomechanics,
            score_tactical_decision,
            evaluate_timing,
            detect_mental_patterns,
            calculate_coach_score
        ] + list(SNOWFLAKE_TOOLS)

        self.db = SnowflakeDB()

        # System Instructions
        self.instructions = """You are an elite table tennis coach AI with expertise in biomechanics, 
tactics, and sports psychology. You analyze match data to provide actionable coaching insights.

Your analysis process:
1. For each shot, call analyze_biomechanics() to evaluate posture
2. Call score_tactical_decision() to assess shot selection
3. Call evaluate_timing() to check contact timing
4. After analyzing all shots, call detect_mental_patterns() for psychological insights
5. Finally, call calculate_coach_score() to generate the confidence score

Your output MUST be a valid JSON object with the following structure:
{
    "snapshot": {
        "shots_analyzed": int,
        "rallies": int,
        "style": "string (Aggressive/Passive/Balanced)",
        "pressure_behavior": "string"
    },
    "key_findings": [
        "string (Finding 1)",
        "string (Finding 2)",
        "string (Finding 3)"
    ],
    "recommendations": [
        "string (Action 1)",
        "string (Action 2)",
        "string (Action 3)"
    ],
    "mental_pattern": {
        "insight": "string",
        "fix": "string"
    },
    "confidence_score": int
}

Do not include markdown formatting like ```json ... ```. Just return the raw JSON string.
"""

    # ------------------------------------------------------------------------
    # ANALYSIS METHODS
    # ------------------------------------------------------------------------

    async def analyze_match_async(self, match_stats: dict) -> str:
        """Run multi-agent analysis on match stats."""
        # CHECK: If we can run real analysis
        if DEDALUS_AVAILABLE and self.api_key:
            return await self._run_real_analysis(match_stats)
        else:
            print("[DedalusCoach] Simulation Mode Active (Missing Key or Package)")
            return self._run_simulated_analysis(match_stats)

    def analyze_match(self, match_stats: dict) -> str:
        return asyncio.run(self.analyze_match_async(match_stats))

    async def _run_real_analysis(self, match_stats: dict) -> str:
        try:
            input_summary = self._prepare_input(match_stats)
            client = AsyncDedalus(api_key=self.api_key)
            runner = DedalusRunner(client)
            response = await runner.run(
                input=input_summary,
                model=self.models,
                tools=self.tools,
                instructions=self.instructions,
                stream=False,
            )
            return response.final_output
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _run_simulated_analysis(self, match_stats: dict) -> str:
        """Return a realistic JSON response based on basic stats."""
        rallies = len(match_stats.get('rallies', []))
        return json.dumps({
            "snapshot": {
                "shots_analyzed": max(12, rallies * 4), 
                "rallies": rallies,
                "style": "Passive / Defensive (Simulated)",
                "pressure_behavior": "Retreats on backhand"
            },
            "key_findings": [
                "Strong dependence on push shots (80% of returns)",
                "Knee angle averages 155° (too straight) reducing mobility",
                "Consistently late on forehand contact (Falling phase)"
            ],
            "recommendations": [
                "Practice forehand drive against backspin to break push cycles",
                "Lower stance by 10cm to improve lateral explosion",
                "Step in earlier to catch the ball at peak height"
            ],
            "mental_pattern": {
                "insight": "You tend to freeze after making an unforced error.",
                "fix": "Use a 'reset trigger' like wiping your hand on the table."
            },
            "confidence_score": 85
        })

    # ------------------------------------------------------------------------
    # CHAT METHODS
    # ------------------------------------------------------------------------

    async def chat_async(self, query: str, match_stats: Optional[dict] = None) -> str:
        """Chat with the coach."""
        if DEDALUS_AVAILABLE and self.api_key:
            return await self._run_real_chat(query, match_stats)
        else:
            return self._run_simulated_chat(query)

    def chat(self, query: str, match_stats: Optional[dict] = None) -> str:
        return asyncio.run(self.chat_async(query, match_stats))

    async def _run_real_chat(self, query: str, match_stats: dict) -> str:
        chat_instructions = """You are a helpful and knowledgeable table tennis coaching assistant.
        
You have access to:
1. The user's current match data (if provided)
2. Snowflake tools to look up player history and similar matches
3. Biomechanics and tactical analysis tools

When answering:
- Be encouraging but direct about technical faults.
- If the user asks about their history ("Have I done this before?"), use the snowflake tools.
- If the user asks about the current match, refer to the provided context.
- Keep answers concise (max 3-4 paragraphs).
"""
        context_str = ""
        if match_stats:
            context_str = f"\n=== CURRENT MATCH CONTEXT ===\n{self._prepare_input(match_stats)}\n=============================\n"
        
        full_prompt = f"{context_str}\nUser Question: {query}"
        
        try:
            client = AsyncDedalus(api_key=self.api_key)
            runner = DedalusRunner(client)
            response = await runner.run(
                input=full_prompt,
                model=self.models,
                tools=self.tools,
                instructions=chat_instructions,
                max_steps=10, 
                stream=False
            )
            return response.final_output
        except Exception as e:
            return f"Error generation response: {str(e)}"

    def _run_simulated_chat(self, query: str) -> str:
        """Simple keyword-based responses for demo."""
        q = query.lower()
        if "footwork" in q:
            return "Based on the analysis, your stance is too narrow (avg 95px). Try widening your feet to shoulder-width + 10cm. This will help you push off faster for wide balls."
        elif "forehand" in q:
            return "Your forehand contact is often late (falling phase). You need to prepare your stroke earlier. Focus on rotating your waist as soon as you see the opponent's racket angle."
        elif "backhand" in q:
            return "Your backhand push is consistent, but passive. Try to add a 'flick' motion when the ball is short to put more pressure on your opponent."
        elif "history" in q or "before" in q:
            return " Checking Snowflake history... Yes, I found 3 matches from last month where you had the same issue with high balls. You tend to smash them into the net."
        else:
            return "That's a great question. Based on your biomechanics data, maintaining a lower center of gravity (knees bent ~130°) would significantly improve your consistency in that area."

    # ------------------------------------------------------------------------
    # UTILS
    # ------------------------------------------------------------------------
    
    def _prepare_input(self, match_stats: dict) -> str:
        """Prepare a structured input prompt from match statistics."""
        rallies = match_stats.get('rallies', [])
        total_shots = sum(len(r.get('shots', [])) for r in rallies)
        
        # Build shot-by-shot data for the agent
        shots_data = []
        for rally in rallies:
            for shot in rally.get('shots', []):
                skel = shot.get('skeleton_analysis', {})
                shots_data.append({
                    "rally_id": rally.get('id', 'unknown'),
                    "shot_type": shot.get('shot_type', 'unknown'),
                    "knee_angle": skel.get('avg_knee_angle', 140),
                    "shoulder_angle": skel.get('avg_shoulder_angle', 45),
                    "stance_width": skel.get('stance_width', 100),
                    "height_over_net": shot.get('height_over_net', 0),
                    "timing_class": shot.get('timing_class', 'Unknown'),
                    "timing_score": shot.get('timing_score', 50),
                })
        
        # Calculate rhythm degradation
        rhythms = [r.get('rhythm_consistency', 0) for r in rallies]
        rhythm_degradation = 0
        if len(rhythms) >= 2:
            if rhythms[0] > 0:
                rhythm_degradation = (rhythms[-1] - rhythms[0]) / rhythms[0]
        
        # Detect passive streaks
        shot_types = [s.get('shot_type', '').lower() for r in rallies for s in r.get('shots', [])]
        passive_streak = 0
        max_passive_streak = 0
        for st in shot_types:
            if st in ['push', 'block', 'defensive']:
                passive_streak += 1
                max_passive_streak = max(max_passive_streak, passive_streak)
            else:
                passive_streak = 0
        
        prompt = f"""Analyze this table tennis match clip:

MATCH DATA:
- Total Rallies: {len(rallies)}
- Total Shots: {total_shots}
- Rhythm Degradation: {rhythm_degradation:.2f}
- Longest Passive Streak: {max_passive_streak} shots

SHOT-BY-SHOT DATA:
{json.dumps(shots_data, indent=2)}

Please use the available tools to analyze each shot's biomechanics, tactical decision, 
and timing. Then detect any mental patterns and calculate the overall confidence score.
Finally, provide your coaching insights in the required format."""
        return prompt

if __name__ == "__main__":
    c = DedalusCoach()
    print("Testing Simulation:")
    print(c.chat("How is my footwork?"))
