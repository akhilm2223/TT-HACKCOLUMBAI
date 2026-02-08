"""
Push all 4 analysis JSONs to Snowflake + run Gemini coaching on each.
Identity: RED (near/bottom) = You | BLUE (far/top) = Opponent
"""
import os, sys, json, uuid
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.snowflake_db import SnowflakeDB

# All 4 videos
JSON_FILES = [
    ("output_videos/analysis_134224.json",  "Recording_134224"),
    ("output_videos/analysis_153355.json",  "Recording_153355"),
    ("output_videos/analysis_192747.json",  "Recording_192747"),
    ("output_videos/analysis_224148.json",  "Recording_224148"),
]

def main():
    db = SnowflakeDB()
    if not db.connect():
        print("FAILED: Could not connect to Snowflake.")
        return

    print(f"Connected: {db.account} / {db.database}.{db.schema}")
    print("=" * 60)

    match_ids = []

    for json_path, label in JSON_FILES:
        print(f"\n--- {label} ---")
        if not os.path.exists(json_path):
            print(f"  SKIP: {json_path} not found")
            continue

        with open(json_path, 'r', encoding='utf-8') as f:
            analysis = json.load(f)

        n_frames = analysis.get("frames", 0)
        n_shots = len(analysis.get("shots", []))
        n_rallies = len(analysis.get("rallies", []))
        print(f"  Frames: {n_frames}, Shots: {n_shots}, Rallies: {n_rallies}")

        match_id = str(uuid.uuid4())
        db.insert_match(match_id, "You (Red/Near)", "Opponent (Blue/Far)", label)
        print(f"  MATCH: {match_id[:12]}...")

        success = db.insert_full_analysis(match_id, analysis)
        if success:
            print(f"  JSON + 768-dim vector stored")
        else:
            print(f"  FAILED to store")

        match_ids.append((match_id, label, json_path))

    # Now run Gemini coaching for ALL 4
    print(f"\n{'=' * 60}")
    print("GEMINI COACHING FOR ALL 4 MATCHES")
    print("Identity: RED (near) = You | BLUE (far) = Opponent")
    print("=" * 60)

    all_coaching = []
    try:
        from modules.llm_coach import GeminiCoach, print_coaching_result
        coach = GeminiCoach()
        coach.db = db

        for match_id, label, json_path in match_ids:
            print(f"\n{'─' * 50}")
            print(f"COACHING: {label}")
            print(f"{'─' * 50}")
            try:
                result = coach.analyze_match(match_id)
                print_coaching_result(result)
                result["video_label"] = label
                all_coaching.append(result)

                # Save individual coaching
                safe_label = label.replace(" ", "_")
                out_path = f"output_videos/coaching_{safe_label}.json"
                with open(out_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"  Saved: {out_path}")
            except Exception as e:
                print(f"  Coaching failed: {e}")

    except Exception as e:
        print(f"Coach import failed: {e}")

    # Save combined coaching
    if all_coaching:
        combined_path = "output_videos/all_coaching_4videos.json"
        with open(combined_path, 'w', encoding='utf-8') as f:
            json.dump(all_coaching, f, indent=2, ensure_ascii=False)
        print(f"\nAll coaching saved: {combined_path}")

    db.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
