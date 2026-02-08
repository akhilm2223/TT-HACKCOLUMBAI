"""
Snowflake MCP Server for Break Point AI Coach

This module creates a custom MCP (Model Context Protocol) server that exposes
Snowflake queries as tools that can be called by the Dedalus agent.

Tools provided:
- query_similar_matches: Find historically similar matches using vector search
- get_player_history: Retrieve player's performance history
- search_match_patterns: Find common patterns in past matches
"""

import os
import sys
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import Snowflake connection
try:
    from modules.snowflake_db import SnowflakeDB
except ImportError:
    from snowflake_db import SnowflakeDB


class SnowflakeMCPServer:
    """
    Custom MCP-style server for Snowflake queries.
    
    Note: This is a simplified implementation. For a full MCP server,
    you would use the MCP Python SDK to create a proper server that
    Dedalus can connect to via 'mcp_servers' parameter.
    
    For hackathon, we expose these as local tools instead.
    """
    
    def __init__(self):
        self.db = SnowflakeDB()
        self.connected = False
        
    def connect(self) -> bool:
        """Establish Snowflake connection."""
        if not self.connected:
            self.connected = self.db.connect()
        return self.connected
    
    def query_similar_matches(
        self, 
        player_style: str, 
        shot_pattern: str,
        limit: int = 5
    ) -> dict:
        """
        Find historically similar matches using vector similarity.
        
        Args:
            player_style: Detected playing style (Aggressive, Passive, Balanced)
            shot_pattern: Dominant shot pattern (e.g., "push-heavy", "loop-dominant")
            limit: Maximum matches to return
        
        Returns:
            dict with similar matches and their insights
        """
        if not self.connect():
            return {"error": "Could not connect to Snowflake", "matches": []}
        
        # Build semantic query for vector search
        semantic_query = f"Table tennis match with {player_style} style, {shot_pattern} pattern"
        
        try:
            # Use Cortex vector search
            query = """
            SELECT 
                MATCH_ID,
                SEMANTIC_SUMMARY,
                VECTOR_COSINE_SIMILARITY(
                    SEMANTIC_VECTOR,
                    SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', %s)
                ) AS similarity
            FROM ANALYSIS_OUTPUT
            WHERE SEMANTIC_VECTOR IS NOT NULL
            ORDER BY similarity DESC
            LIMIT %s
            """
            
            cursor = self.db.execute_query(query, (semantic_query, limit))
            if not cursor:
                return {"error": "Query failed", "matches": []}
            
            matches = []
            for row in cursor.fetchall():
                matches.append({
                    "match_id": row[0],
                    "summary": row[1],
                    "similarity": round(row[2], 3)
                })
            
            cursor.close()
            return {"matches": matches, "query": semantic_query}
            
        except Exception as e:
            return {"error": str(e), "matches": []}
    
    def get_player_history(
        self,
        player_id: Optional[str] = None,
        match_limit: int = 10
    ) -> dict:
        """
        Retrieve player's recent performance history.
        
        Args:
            player_id: Optional player identifier (if known)
            match_limit: Number of recent matches to analyze
        
        Returns:
            dict with aggregated player stats
        """
        if not self.connect():
            return {"error": "Could not connect to Snowflake", "history": {}}
        
        try:
            query = """
            SELECT 
                COUNT(*) as total_matches,
                AVG(FULL_ANALYSIS:summary:avg_timing_score::FLOAT) as avg_timing,
                AVG(FULL_ANALYSIS:summary:avg_tactical_score::FLOAT) as avg_tactical,
                AVG(FULL_ANALYSIS:summary:avg_knee_angle::FLOAT) as avg_knee,
                MODE(FULL_ANALYSIS:summary:dominant_style::STRING) as common_style
            FROM ANALYSIS_OUTPUT
            WHERE CREATED_AT >= DATEADD('day', -30, CURRENT_TIMESTAMP())
            LIMIT %s
            """
            
            cursor = self.db.execute_query(query, (match_limit,))
            if not cursor:
                return {"error": "Query failed", "history": {}}
            
            row = cursor.fetchone()
            if not row:
                return {"error": "No data found", "history": {}}
            
            cursor.close()
            return {
                "history": {
                    "total_matches": row[0] or 0,
                    "avg_timing_score": round(row[1] or 0, 1),
                    "avg_tactical_score": round(row[2] or 0, 1),
                    "avg_knee_angle": round(row[3] or 0, 1),
                    "common_style": row[4] or "Unknown"
                }
            }
            
        except Exception as e:
            return {"error": str(e), "history": {}}
    
    def search_match_patterns(
        self,
        pattern_type: str,
        threshold: float = 0.5
    ) -> dict:
        """
        Find common patterns in past matches.
        
        Args:
            pattern_type: Type of pattern to search (e.g., "passive_error", "late_timing")
            threshold: Minimum occurrence threshold (0-1)
        
        Returns:
            dict with pattern statistics and examples
        """
        if not self.connect():
            return {"error": "Could not connect to Snowflake", "patterns": []}
        
        pattern_queries = {
            "passive_error": """
                SELECT MATCH_ID, 
                       FULL_ANALYSIS:summary:passive_error_count::INT as count
                FROM ANALYSIS_OUTPUT 
                WHERE FULL_ANALYSIS:summary:passive_error_count::INT > 0
                ORDER BY count DESC LIMIT 5
            """,
            "late_timing": """
                SELECT MATCH_ID,
                       FULL_ANALYSIS:summary:late_timing_pct::FLOAT as pct
                FROM ANALYSIS_OUTPUT
                WHERE FULL_ANALYSIS:summary:late_timing_pct::FLOAT > %s
                ORDER BY pct DESC LIMIT 5
            """,
            "fatigue": """
                SELECT MATCH_ID,
                       FULL_ANALYSIS:summary:rhythm_degradation::FLOAT as degradation
                FROM ANALYSIS_OUTPUT
                WHERE FULL_ANALYSIS:summary:rhythm_degradation::FLOAT > %s
                ORDER BY degradation DESC LIMIT 5
            """
        }
        
        query = pattern_queries.get(pattern_type)
        if not query:
            return {"error": f"Unknown pattern type: {pattern_type}", "patterns": []}
        
        try:
            cursor = self.db.execute_query(query, (threshold,))
            if not cursor:
                return {"error": "Query failed", "patterns": []}
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    "match_id": row[0],
                    "value": row[1]
                })
            
            cursor.close()
            return {"pattern_type": pattern_type, "patterns": patterns}
            
        except Exception as e:
            return {"error": str(e), "patterns": []}
    
    def get_coaching_insights(self, match_id: str) -> dict:
        """
        Retrieve previously saved coaching insights for a match.
        
        Args:
            match_id: The match identifier
        
        Returns:
            dict with coaching insights
        """
        if not self.connect():
            return {"error": "Could not connect to Snowflake", "insights": None}
        
        try:
            query = """
            SELECT 
                INSIGHT_TEXT,
                PROCESSED_JSON,
                CREATED_AT
            FROM COACHING_INSIGHTS
            WHERE MATCH_ID = %s
            ORDER BY CREATED_AT DESC
            LIMIT 1
            """
            
            cursor = self.db.execute_query(query, (match_id,))
            if not cursor:
                return {"error": "Query failed", "insights": None}
            
            row = cursor.fetchone()
            if not row:
                return {"error": "No insights found", "insights": None}
            
            cursor.close()
            return {
                "insights": {
                    "text": row[0],
                    "structured": json.loads(row[1]) if row[1] else None,
                    "created_at": str(row[2])
                }
            }
            
        except Exception as e:
            return {"error": str(e), "insights": None}


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL FUNCTIONS FOR DEDALUS
# These are standalone functions that can be passed to DedalusRunner
# ═══════════════════════════════════════════════════════════════════════════════

_mcp_server = None

def _get_server():
    """Lazy initialization of MCP server."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = SnowflakeMCPServer()
    return _mcp_server


def query_similar_matches(player_style: str, shot_pattern: str, limit: int = 5) -> dict:
    """
    Find historically similar matches from Snowflake using vector search.
    
    Args:
        player_style: Playing style (Aggressive, Passive, Balanced)
        shot_pattern: Shot pattern (push-heavy, loop-dominant, etc.)
        limit: Max results
    
    Returns:
        Similar matches with similarity scores
    """
    return _get_server().query_similar_matches(player_style, shot_pattern, limit)


def get_player_history(player_id: str = None, match_limit: int = 10) -> dict:
    """
    Get player's recent performance averages from Snowflake.
    
    Args:
        player_id: Optional player identifier
        match_limit: Number of recent matches to analyze
    
    Returns:
        Aggregated player statistics
    """
    return _get_server().get_player_history(player_id, match_limit)


def search_match_patterns(pattern_type: str, threshold: float = 0.5) -> dict:
    """
    Search for common patterns in past matches.
    
    Args:
        pattern_type: One of 'passive_error', 'late_timing', 'fatigue'
        threshold: Minimum occurrence threshold
    
    Returns:
        Pattern statistics and examples
    """
    return _get_server().search_match_patterns(pattern_type, threshold)


def get_coaching_insights(match_id: str) -> dict:
    """
    Retrieve stored coaching insights for a match.
    
    Args:
        match_id: Match identifier
    
    Returns:
        Previous coaching insights if available
    """
    return _get_server().get_coaching_insights(match_id)


# ═══════════════════════════════════════════════════════════════════════════════
# ALL SNOWFLAKE TOOLS FOR EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

SNOWFLAKE_TOOLS = [
    query_similar_matches,
    get_player_history,
    search_match_patterns,
    get_coaching_insights
]


if __name__ == "__main__":
    # Test the server
    print("=== Testing Snowflake MCP Server ===\n")
    
    server = SnowflakeMCPServer()
    
    print("1. Testing query_similar_matches...")
    result = query_similar_matches("Passive", "push-heavy", 3)
    print(f"   Result: {result}\n")
    
    print("2. Testing get_player_history...")
    result = get_player_history(match_limit=5)
    print(f"   Result: {result}\n")
    
    print("3. Testing search_match_patterns...")
    result = search_match_patterns("passive_error", 0.3)
    print(f"   Result: {result}\n")
