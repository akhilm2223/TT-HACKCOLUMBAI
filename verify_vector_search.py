from modules.snowflake_db import SnowflakeDB

def test_vector_search():
    db = SnowflakeDB()
    if not db.connect():
        print("Connection failed")
        return

    # Search for something relevant to table tennis
    query = "forehand topspin error"
    print(f"Searching for: '{query}'...")
    
    results = db.find_similar_matches(query, top_k=3)
    
    if results:
        print(f"\nFound {len(results)} matches:")
        for r in results:
            print(f"- Match {r['match_id']}")
            print(f"  Similarity: {r['similarity']:.4f}")
            print(f"  Summary: {r['semantic_summary'][:100]}...")
    else:
        print("\nNo results found. (Is data vectorized?)")

    db.close()

if __name__ == "__main__":
    test_vector_search()
