from modules.snowflake_db import SnowflakeDB

def run_create_tables():
    print("Connecting to Snowflake...")
    db = SnowflakeDB()
    if not db.connect():
        print("Failed to connect.")
        return

    print("Creating/Verifying tables...")
    try:
        db.create_tables()
        print("Successfully created/verified all tables.")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_create_tables()
