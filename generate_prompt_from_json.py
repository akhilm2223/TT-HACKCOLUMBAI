import sys
import os
import json

# Ensure root directory is in path
sys.path.append(os.getcwd())

from modules.llm_coach import LLMCoach
from HH.stats_engine import StatsEngine

def generate_and_save_prompt():
    print("=== Generating Prompt from Raw JSON ===")
    
    # 1. Load the JSON file
    json_path = "output_videos/table_tennis_analysis.json"
    if not os.path.exists(json_path):
        print(f"Error: File {json_path} not found.")
        return

    with open(json_path, 'r') as f:
        match_data = json.load(f)
    print(f"Loaded JSON: {match_data.get('video', 'Unknown Video')}")

    # 2. Process with StatsEngine
    print("Processing metrics...")
    engine = StatsEngine()
    stats = engine.process_match(match_data)
    
    if "error" in stats:
        print(f"Error processing stats: {stats['error']}")
        return

    # 3. Generate Prompt
    print("Generating LLM Coach Prompt...")
    coach = LLMCoach()
    prompt = coach.generate_coach_prompt(stats)
    
    # 4. Save to File
    output_file = "generated_prompt.txt"
    with open(output_file, "w") as f:
        f.write(prompt)
        
    print(f"\n[SUCCESS] Prompt saved to: {os.path.abspath(output_file)}")
    print("\n--- Preview of Generated Content ---")
    print(prompt)

if __name__ == "__main__":
    generate_and_save_prompt()
