# 🏓 Break Point AI - Snowflake Implementation Pitch

## 1. The "Break Point" Story: How We Built It on Snowflake

_For the Product Demo / Hackathon Pitch_

**The Core Problem**: Table tennis happens too fast for the human eye (ball speeds >100km/h). Video is great for watching, but terrible for analyzing. We needed a way to query "speed", "tactics", and "form" directly from pixels.

**Our Solution**: We built a hybrid Computer Vision + LLM pipeline that feeds directly into Snowflake. Here is exactly how we used Snowflake’s unique features to make this possible:

### Feature 1: Handling Chaos with `VARIANT`

**How We Used It**:
Our CV pipeline outputs massive, messy JSON blobs—frame-by-frame ball coordinates (`x,y`), skeleton joints, and event flags.

- **Old Way**: Defining a rigid schema `(frame_id, ball_x, ball_y, left_elbow_x...)` would have been a nightmare.
- **Our Snowflake Way**: We stream the entire raw JSON into `TRACKING_EVENTS` using the `VARIANT` data type.
- **The Win**: We changed our upstream Python code to add "wrist_speed" and didn't have to change a single line of SQL DDL. We just query it: `SELECT raw_data:wrist_speed FROM TRACKING_EVENTS`.

### Feature 2: Feature Engineering via SQL Views

**How We Used It**:
Instead of recalculating "average rhythm" in Python every time we load a dashboard, we pushed the logic down to the data.

- **Implementation**: We built `MATCH_METRICS_VIEW` which automatically flattens our nested `MATCH_STATS` JSON.
- **Specifics**: It extracts `avg_rhythm_score`, `total_rallies`, and `avg_tactical_score` instantly.
- **The Win**: Our Streamlit app loads instantly because the heavy aggregation happens in Snowflake's elastic compute layer, not in the single-threaded Python app.

### Feature 3: Semantic "Style Search" with Cortex

**How We Used It**:
We wanted coaches to find similar matches based on _feel_, not just stats.

- **Implementation**: We used `SNOWFLAKE.CORTEX.EMBED_TEXT_768` to generate vector embeddings for every match summary.
- **The Query**: We built a UDTF `FIND_SIMILAR_MATCHES`. If a user queries "aggressive forehand loops", Cortex understands the semantic meaning and returns matches where the AI Coach observed that specific style—even if the word "loop" wasn't explicitly logged.
- **The Win**: Truly intelligent retrieval that understands table tennis terminology.

### Feature 4: The "SiS" Dashboard (Streamlit in Snowflake)

**How We Used It**:
We deployed our entire user interface inside Snowflake.

- **Implementation**: A `streamlit_app.py` that imports `snowflake.snowpark.context`. It visualizes the `MATCH_METRICS_VIEW` and allows interactive filtering.
- **The Win**: Security and Simplicity. We didn't need a separate web server 2. The data never leaves the secure Snowflake environment.

---

## 2. Technical Q&A (Specific to Break Point AI)

**Q: Why store the raw frame data in Snowflake? Isn't that too much?**
**A:** Not for Snowflake. Table tennis is high frequency (60Hz). Storing the raw `x,y` coordinates in `TRACKING_EVENTS` allows us to go back and retrain our models later. If we develop a new "spin detection" algorithm, we can run it against the historical raw data stored in Snowflake without re-processing the videos.

**Q: How does the AI Coach verify the data?**
**A:** The AI (Cortex/Dedalus) reads the statistics we generated (`MATCH_STATS`). We store the _Prompt_ and the _Response_ in `COACHING_INSIGHTS`. This creates an audit trail. We can see exactly what data the LLM saw and what advice it gave.

**Q: Could this work for real-time coaching?**
**A:** Yes. Currently, we batch process match videos. To go real-time, we would simply switch to **Snowpipe Streaming** to ingest the JSON frames directly from the cameras into the `TRACKING_EVENTS` table with low latency, and have a Dynamic Table update the leaderboard every minute.

**Q: What is the most complex query you run?**
**A:** The vector similarity search. We join `MATCHES` with `ANALYSIS_OUTPUT`, compute the cosine similarity between the query embedding and stored embeddings, and rank them—all in a single SQL statement. This would require a dedicated Vector DB in any other stack; in Snowflake, it's just a `SELECT`.
