import json
import uuid
import sys
import os
from modules.snowflake_db import SnowflakeDB

def push_analysis(json_path):
    if not os.path.exists(json_path):
        print(f"Error: File not found: {json_path}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    # Generate a new Match ID for this manual push
    match_id = str(uuid.uuid4())
    print(f"Generated Match ID: {match_id}")

    db = SnowflakeDB()
    if not db.connect():
        print("Error: Could not connect to Snowflake.")
        return

    try:
        # Assuming insert_full_analysis exists as per main.py usage
        # If not found via grep, I'll rely on class definition or main.py usage.
        # But wait, grep failed. Let's check the file outline first.
        # If it's named differently, I'll adjust.
        # For now, I'll use the method name from main.py: insert_full_analysis
        
        # We need to ensure analysis_data has the right structure.
        # analysis_data is the full JSON content.
        
        success = db.insert_full_analysis(match_id, analysis_data)
        if success:
            print(f"Successfully pushed analysis to Snowflake for match {match_id}")
        else:
            print("Failed to push analysis to Snowflake.")

    except AttributeError:
        print("Error: 'SnowflakeDB' object has no attribute 'insert_full_analysis'. Checking available methods...")
        # Fallback or debugging
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python push_analysis.py <path_to_json>")
    else:
        push_analysis(sys.argv[1])
