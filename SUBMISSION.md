# Hackathon Submission: Break Point 🏓

**Use this content for your Devpost/Hackathon submission.**

## Tagline (Elevator Pitch)

- **Option 1 (~200 chars):** "Break Point turns your raw match video into forensic biomechanical and mental insights. Combining Computer Vision with GenAI, we detect invisible patterns—like hesitation and rhythm—that decide matches."
- **Option 2 (Punchy):** "The AI Coach that sees what human eyes miss."

---

## Inspiration

Elite athletes have entire departments for performance analysis, mental coaching, and biomechanics. Amateur racket sport players have... nothing but their own faulty memory. We wanted to bridge this **"Analytics Gap."**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE SPORTS ANALYTICS GAP                                  │
├─────────────────────────────────┬───────────────────────────────────────────┤
│       🏆 ELITE ATHLETES          │       🎾 AMATEUR ATHLETES                 │
├─────────────────────────────────┼───────────────────────────────────────────┤
│  ✓ Dedicated performance analysts│  ✗ Self-diagnose after losses            │
│  ✓ Mental coaches on staff       │  ✗ Repeat same mistakes vs same opponent │
│  ✓ Biomechanics experts          │  ✗ No data on pressure moments           │
│  ✓ Video analysis teams          │  ✗ Can't detect invisible patterns       │
├─────────────────────────────────┴───────────────────────────────────────────┤
│  💡 BREAK POINT = Forensic audit of the moments that decide matches         │
└─────────────────────────────────────────────────────────────────────────────┘
```

In tennis and table tennis, matches are often decided not by technique, but by invisible mental patterns—hesitation under pressure, robotic rhythm, or passive decision-making. We built Break Point to utilize **Snowflake Cortex** and **Computer Vision** to democratize specific, Hawk-Eye level precision and sports psychology for everyone.

---

## What it does

Break Point is a **real-time AI coaching platform** that ingests raw match video and outputs professional-grade coaching reports. It combines four core layers:

### 1. Hawk-Eye Level Perception (The Eyes)

Tracks the ball at >100km/h using a custom **6D Kalman Filter** (x, y, vx, vy, ax, ay). This allows us to predict the ball's location even when it's occluded by a player's body.

### 2. Mental Intelligence Engine (The Brain)

We don't just track _where_ the ball goes, but _how_ the player feels. We quantify mental states using physics-based proxies:

**Rhythm Score Formula:**

```
Rhythm = 1 - σ(Δt_shots) / μ(Δt_shots)
```

- **Lower variance** = more consistent rhythm (Flow State)
- **Higher variance** = hesitation or panic (Choking)

**Pressure Response Index (PRI):**

```
PRI = (Aggression_after_loss - Aggression_baseline) / Aggression_baseline
```

- **PRI < -0.2**: Player becomes passive under pressure (Flag!)

### 3. Cross-Match Intelligence (The Memory)

The system remembers every match you've ever played. using **Snowflake Cortex Vector Search**:

- **Embed**: Convert match summary → 768-dim vector.
- **Retrieve**: "Find matches where I struggled against high loops."
- **Reason**: The LLM uses past mistakes to inform current advice.

### 4. Specialized AI Coach (The Voice)

A **Dedalus Multi-Agent System** orchestrates 5 specialized tools (Biomechanics, Tactics, Timing, Mental Patterns) to generate actionable advice like: _"Your knee bend was 162° on missed forehands; target 140°."_

---

## How we built it

We built a **Hybrid Vision-Reasoning Pipeline** that combines the speed of CV with the intelligence of LLMs.

### Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SPONSOR TECHNOLOGIES                                  │
├───────────────────┬───────────────────┬───────────────────┬─────────────────┤
│    SNOWFLAKE      │   DEDALUS LABS    │   IFM K2-THINK    │    FLOWGLAD     │
│    ❄️ Cortex       │   🤖 Multi-Agent   │    🌙 Reasoning    │    💳 Payments   │
├───────────────────┴───────────────────┴───────────────────┴─────────────────┤
│ • EMBED_TEXT_768: Semantic search for match history                         │
│ • COMPLETE: LLM reasoning for coaching insights                             │
│ • Dedalus Agent SDK: Orchestrating 5 local analysis tools                   │
│ • K2-Think: Spatial reasoning for complex table detection                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Technical Innovations

#### 1. "Desperate Mode" Ball Tracking

Standard trackers fail when the ball is hidden. We implemented a 3-stage re-acquisition system:

1.  **Tracking Mode**: Tight focus (80px radius).
2.  **Searching Mode**: Lost >5 frames? Widen search (200px).
3.  **Desperate Mode**: Lost >12 frames? Scan entire table ROI.
    _Result: We track the ball through 1.5 seconds (45 frames) of total occlusion._

#### 2. Physics-Based Bounce Detection

We define a bounce mathematically to distinguish it from volleys:

```python
Bounce = True IF:
  vy[k-1] > 0.3          (Ball moving DOWN)
  AND vy[k] < 0          (Ball moving UP)
  AND (x,y) ∈ Table      (Impact on table surface)
  AND gap > 8 frames     (Debounce filter)
```

#### 3. Spatial Reasoning for Table Detection

We used **IFM K2-Think** to solve a common CV problem: is that blue shape the table or the scoreboard?

- **CV**: Finds lines and blobs.
- **K2-Think**: "Given the perspective, the trapezoid at the bottom must be the table."
- **Result**: Robust detection across different venues and lighting.

---

## Challenges we ran into

- **Fast Ball Tracking**: Table tennis balls move across the entire 1080p frame in just 0.2 seconds. A standard webcam sees a blur.
  - _Solution_: We modeled **acceleration** (drag + spin), not just velocity, allowing our Kalman Filter to "hallucinate" the ball's position accurately between frames.
- **Defining "Mental State"**: You can't train a supervised model on "fear."
  - _Solution_: We derived **proxy metrics** from sports psychology. "Hesitation" isn't a label; it's a measurable variance in shot timing (`Rhythm Score`).
- **Integration Latency**: Running YOLO, Pose Estimation, and LLMs simultaneously is heavy.
  - _Solution_: We built a **Fallback Chain**. If Kimi K2 times out, we fall back to TTNet. If Cortex is unreachable, we do local stats. The pipeline degrades gracefully rather than crashing.

---

## Accomplishments that we're proud of

- **Zero-Latency Dashboard**: By moving heavy stats aggregation into **Snowflake SQL Views** (`MATCH_STATS_VIEW`), our Streamlit dashboard loads instantly even with thousands of data points.
- **The "Desperate Mode" Tracker**: Successfully recovering the ball after it has been hidden behind a player's back for 1.5 seconds feels like magic.
- **Quantifying the Intangible**: Giving a player a concrete number for their "Mental Resilience" (PRI Score) turns a vague feeling into a trainable metric.

---

## What we learned

- **Hybrid AI is King**: Pure Computer Vision is precise but "dumb" (no context). Pure LLMs are smart but "blind" (no spatial awareness). Combining them (**Vision for data, LLMs for reasoning**) unlocks capabilities neither can do alone.
- **Formulas Build Trust**: Showing users _how_ we calculated their "Tactical Score" made them trust the AI's advice much more than a black-box output.
- **The Power of Memory**: Adding **Vector Search** transformed the tool from a "match analyzer" to a "career coach." Context matters.

---

## What's next for Break Point

```
     NOW                    Q2 2026               Q3 2026              FUTURE
      │                        │                     │                    │
      ▼                        ▼                     ▼                    ▼
┌─────────┐            ┌───────────┐          ┌──────────┐        ┌──────────┐
│ 📹      │            │ 📈        │          │ 🔊       │        │ 🌍       │
│ Real-   │───────────▶│ Multi-    │─────────▶│ Voice    │───────▶│ Global   │
│ Time    │            │ Match     │          │ Coaching │        │ Platform │
│ Mode    │            │ Trends    │          │          │        │          │
└─────────┘            └───────────┘          └──────────┘        └──────────┘
```

1.  **Real-Time Mode**: Moving from batch processing to **Snowpipe Streaming** for live match analysis.
2.  **Voice Coaching**: Integrating **ElevenLabs** to give real-time audio feedback during practice ("Bend your knees!", "Faster reset!").
3.  **Global Leaderboard**: Using **Snowflake Dynamic Tables** to rank players worldwide not just by wins, but by "Mental Resilience" scores.
