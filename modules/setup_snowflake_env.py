import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_setup():
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    
    # Check if credentials are placeholders
    if "your_" in user or "your_" in account:
        print("Error: Please update .env with your actual Snowflake credentials.")
        return

    print(f"Connecting to Snowflake account: {account} as user: {user}...")
    
    try:
        # Connect without specifying database/schema initially
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account
        )
        cursor = conn.cursor()
        
        # Read the SQL file
        with open("setup_snowflake.sql", "r") as f:
            sql_script = f.read()
            
        # Split into individual statements (simple split by semicolon)
        # Note: This is a basic split, might fail on complex SQL, but fine for our simple ddl
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        for stmt in statements:
            # Skip comments
            lines = [l for l in stmt.split('\n') if not l.strip().startswith('--')]
            clean_stmt = '\n'.join(lines).strip()
            if not clean_stmt:
                continue
                
            print(f"Executing: {clean_stmt[:50]}...")
            try:
                cursor.execute(clean_stmt)
            except Exception as e:
                print(f"  Error executing statement: {e}")
                
        print("\nSnowflake environment setup complete!")
        conn.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_setup()
