"""Run Gemini coaching on all 3 matches in Snowflake. Save results."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.llm_coach import GeminiCoach, print_coaching_result
from modules.snowflake_db import SnowflakeDB

db = SnowflakeDB()
db.connect()

# Get latest version of each video (dedup by VIDEO_FILE, take newest)
cursor = db.execute_query("""
    SELECT a.MATCH_ID, m.VIDEO_FILE
    FROM ANALYSIS_OUTPUT a
    JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID
    ORDER BY a.CREATED_AT DESC
""")
rows = cursor.fetchall()
cursor.close()

# Dedup: keep first (newest) per video
seen = set()
matches = []
for mid, vf in rows:
    if vf not in seen:
        seen.add(vf)
        matches.append((mid, vf))

print(f"Found {len(matches)} unique matches to coach:\n")
for mid, vf in matches:
    print(f"  {mid[:12]}... -> {vf}")

coach = GeminiCoach()
coach.db = db

all_results = {}
for mid, vf in matches:
    print(f"\n{'='*60}")
    print(f"COACHING: {vf}")
    print(f"{'='*60}")
    result = coach.analyze_match(mid)
    print_coaching_result(result)
    all_results[vf] = result

    # Save individual coaching JSON
    safe_name = vf.replace(" ", "_").replace(".mp4", "")
    out_path = f"output_videos/coaching_{safe_name}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved: {out_path}")

# Save combined
with open("output_videos/all_coaching_insights.json", 'w', encoding='utf-8') as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)
print(f"\nAll insights saved: output_videos/all_coaching_insights.json")

db.close()
