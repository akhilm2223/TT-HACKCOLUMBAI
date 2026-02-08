# Hackathon Submission: Break Point 🏓

Use this content to fill out your submission form.

## Project Name

Break Point

## Tagline (Elevator Pitch)

_Option 1 (Descriptive - 98 chars):_
"AI-Powered Performance & Mental Intelligence for Athletes. Turning raw video into forensic insights."

_Option 2 (Punchy - 58 chars):_
"The AI Coach that sees what human eyes miss."

_Option 3 (Technical ~200 chars):_
"Break Point turns your raw match video into forensic biomechanical and mental insights. Combining Computer Vision with GenAI, we detect invisible patterns—like hesitation and rhythm—that decide matches."

_Option 4 (Alternative ~200 chars):_
"Elite athletes have teams of analysts. You have Break Point. Our AI Coach transforms your match video into professional-grade stats and mental patterns, finally democratizing sports intelligence."

## Inspiration

Elite athletes have entire departments for performance analysis, mental coaching, and biomechanics. Amateur racket sport players have... nothing but their own faulty memory. We wanted to bridge this "Analytics Gap."

In tennis and table tennis, matches are often decided not by technique, but by invisible mental patterns—hesitation under pressure, robotic rhythm, or passive decision-making. We built Break Point to be the "Forensic Audit" for these critical moments, democratizing Hawk-Eye level precision and sports psychology for everyone.

## What it does

Break Point is a comprehensive AI coaching platform that ingests raw match video and outputs professional-grade coaching reports.

1.  **See the Invisible**: Tracks the ball at >100km/h using a custom 6D Kalman Filter, even when occluded.
2.  **Mental Intelligence**: Detects "choking" (pressure response) by analyzing rhythm consistency and aggression changes after lost points.
3.  **Cross-Match Memory**: Uses Vector Search to find similar historical matches (e.g., "Find other matches where I struggled against high loops") to give context-aware advice.
4.  **AI Coach**: A multi-agent system that doesn't just show stats, but gives actionable drills (e.g., "Your knee bend was 162° on missed forehands; target 140°").

## How we built it (The Stack)

We built a hybrid pipeline combining high-speed Computer Vision with Reasoning LLMs.

1.  **Snowflake (The Brain)**: We store complex tracking data (JSON) in `VARIANT` columns. We use **Cortex** functions to embed match summaries (`EMBED_TEXT_768`) and **Vector Search** to retrieve similar playing styles. **Streamlit in Snowflake** hosts our specialized dashboard.
2.  **Dedalus Labs (The Coach)**: We used the Dedalus Agent SDK to orchestrate 5 specialized tools (Biomechanics, Tactics, Timing, Mental Patterns). The agent "reasons" over the data to generate the final coaching report.
3.  **IFM K2-Think (The Eyes)**: We used the K2-Think reasoning model to solve the complex geometry of table detection, converting visual line segments into a text-based geometry problem to distinguish the table from the scoreboard.
4.  **Flowglad (The Business)**: Logic implemented for tier-gated analysis (Free vs. Pro vs. Elite) to demonstrate monetization potential.

## Challenges we ran into

- **Fast Ball Tracking**: Table tennis balls move across the entire frame in 0.2 seconds. Standard trackers failed. We built a physics-aware **6D Kalman Filter** (tracking position + velocity + acceleration) to predict the ball's location even during occlusion.
- **Defining "Mental State"**: You can't train a model on "fear." We had to derive proxy metrics from sports psychology (Rhythm Variance, Pressure Response Index) to quantify mental states from tracking data.
- **Hardware Constraints**: Running YOLO, Pose Estimation, and LLMs simultaneously is heavy. We built a fallback chain (Kimi K2 -> TTNet -> Classical CV) to ensure the pipeline never crashes, just degrades gracefully.

## Accomplishments that we're proud of

- **Rhythm Score**: Successfully quantifying "flow state" vs. "robotic play" using purely mathematical variance of shot timing.
- **The "Desperate Mode" Tracker**: Our ball tracker can recover the ball even after it's been hidden behind a player's body for 1.5 seconds (45 frames).
- **Zero-Latency Dashboard**: By moving heavy stats aggregation into Snowflake SQL Views, our Streamlit dashboard loads instantly even with thousands of data points.

## What we learned

- **Hybrid AI is King**: Pure Computer Vision is precise but dumb. Pure LLMs are smart but blind. Combining them (Vision for data, LLMs for reasoning) unlocks capabilities neither can do alone.
- **Formulas Build Trust**: Showing users _how_ we calculated their "Tactical Score" made them trust the AI's advice much more than a black-box output.

## What's next for Break Point

- **Real-Time Mode**: Moving from batch processing to Snowpipe Streaming for live match analysis.
- **Voice Coaching**: Integrating ElevenLabs to give real-time audio feedback during practice ("Bend your knees!", "Faster reset!").
- **Global Leaderboard**: Using Snowflake Dynamic Tables to rank players worldwide not just by wins, but by "Mental Resilience" scores.
