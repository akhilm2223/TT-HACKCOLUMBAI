"""
Push all analysis JSONs to Snowflake ANALYSIS_OUTPUT.
For each JSON:
  1. Creates a MATCH row (MATCHES table)
  2. Stores the full JSON as VARIANT in ANALYSIS_OUTPUT
  3. Generates a 768-dim Cortex embedding from semantic_summary
  4. Stores the embedding in SEMANTIC_VECTOR for similarity search
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Add project root for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.snowflake_db import SnowflakeDB
import uuid

# The 4 analysis JSONs
JSON_FILES = [
    ("output_videos/analysis_134224.json",    "Recording 2026-02-07 134224.mp4"),
    ("output_videos/analysis_153355.json",    "Recording 2026-02-07 153355.mp4"),
    ("output_videos/table_tennis_analysis.json", "Recording 2026-02-07 192747.mp4"),
    ("output_videos/analysis_224148.json",    "Recording 2026-02-07 224148.mp4"),
]

def main():
    db = SnowflakeDB()
    if not db.connect():
        print("FAILED: Could not connect to Snowflake. Check .env credentials.")
        return

    print(f"Connected to Snowflake: {db.account} / {db.database}.{db.schema}")
    print(f"{'='*60}")

    for json_path, video_name in JSON_FILES:
        print(f"\n--- {video_name} ---")

        if not os.path.exists(json_path):
            print(f"  SKIP: {json_path} not found")
            continue

        # Load the analysis JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            analysis = json.load(f)

        # Summary stats
        n_frames = analysis.get("frames", 0)
        n_shots = len(analysis.get("shots", []))
        n_rallies = len(analysis.get("rallies", []))
        semantic = analysis.get("semantic_summary", "")[:200]
        print(f"  Frames: {n_frames}, Shots: {n_shots}, Rallies: {n_rallies}")
        print(f"  Summary: {semantic}...")

        # Step 1: Create match row
        match_id = str(uuid.uuid4())
        db.insert_match(match_id, "Player 1", "Player 2", video_name)
        print(f"  [1/3] MATCH created: {match_id}")

        # Step 2 + 3: Push full analysis + generate Cortex embedding
        # insert_full_analysis() does:
        #   - Stores FULL_ANALYSIS (entire JSON as VARIANT)
        #   - Stores SEMANTIC_SUMMARY (text)
        #   - Calls SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', summary)
        #     to create a 768-dim float vector
        #   - Stores vector in SEMANTIC_VECTOR column
        success = db.insert_full_analysis(match_id, analysis)
        if success:
            print(f"  [2/3] ANALYSIS_OUTPUT stored (JSON + 768-dim vector embedding)")
            print(f"  [3/3] SEMANTIC_VECTOR = Cortex EMBED of semantic_summary")
        else:
            print(f"  FAILED to push analysis")

    # Verify what's in Snowflake now
    print(f"\n{'='*60}")
    print("VERIFICATION: Querying ANALYSIS_OUTPUT...")
    cursor = db.execute_query("""
        SELECT a.MATCH_ID, m.VIDEO_FILE, a.SEMANTIC_SUMMARY,
               CASE WHEN a.SEMANTIC_VECTOR IS NOT NULL THEN 'YES' ELSE 'NO' END AS HAS_VECTOR
        FROM ANALYSIS_OUTPUT a
        JOIN MATCHES m ON a.MATCH_ID = m.MATCH_ID
        ORDER BY a.CREATED_AT DESC
    """)
    if cursor:
        rows = cursor.fetchall()
        print(f"Found {len(rows)} matches in ANALYSIS_OUTPUT:\n")
        for r in rows:
            print(f"  Match: {r[0][:12]}...")
            print(f"  Video: {r[1]}")
            print(f"  Vector: {r[3]}")
            print(f"  Summary: {r[2][:120]}...")
            print()
        cursor.close()

    # Test vector similarity search
    if rows and len(rows) >= 2:
        print(f"{'='*60}")
        print("VECTOR SIMILARITY TEST:")
        print("  Query: 'strong forehand with footwork drop'")
        similar = db.find_similar_matches("strong forehand with footwork drop", top_k=3)
        for s in similar:
            print(f"  {s['video_file']} -> similarity: {s['similarity']:.4f}")
        print()

    # Run Gemini coaching on the first match (the one with most shots)
    if rows and len(rows) > 0:
        print(f"{'='*60}")
        print("GEMINI COACHING (on first match)...")
        first_match_id = rows[0][0]  # most recent
        try:
            from modules.llm_coach import GeminiCoach, print_coaching_result
            coach = GeminiCoach()
            coach.db = db  # reuse connection
            result = coach.analyze_match(first_match_id)
            print_coaching_result(result)

            # Save the result as JSON too
            coaching_path = "output_videos/coaching_insight.json"
            with open(coaching_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Coaching JSON saved: {coaching_path}")
        except Exception as e:
            print(f"Coaching failed: {e}")

    db.close()
    print("Done!")


if __name__ == "__main__":
    main()
