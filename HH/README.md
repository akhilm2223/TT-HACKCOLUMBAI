# Break Point 🏓

> **AI-Powered Performance & Mental Intelligence for Single-Sport Athletes**

_Columbia DevFest Hackathon 2026_

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Snowflake](https://img.shields.io/badge/Snowflake-Cortex-29B5E8.svg)](https://snowflake.com)
[![Dedalus Labs](https://img.shields.io/badge/Dedalus-Multi--Agent-8B5CF6.svg)](https://dedalus.ai)
[![Kimi K2](https://img.shields.io/badge/Kimi-K2_Think-FF6B35.svg)](https://moonshot.ai)

---

## Inspiration

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
│                                                                              │
│  PROVEN SOLUTIONS IN OTHER SPORTS:                                          │
│  • Hawk-Eye → Tennis millimeter precision                                   │
│  • F1 Telemetry → Sub-second reaction analysis                              │
│  • Team Analytics → Entire departments for pattern recognition              │
│                                                                              │
│  ❓ WHY NOT RACKET SPORTS?                                                   │
│     The most mentally demanding, pressure-critical individual competitions  │
│     remain without accessible intelligence tools.                           │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  💡 BREAK POINT = Forensic audit of the moments that decide matches         │
│     When hesitation, fear, or poor decisions silently change outcomes       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💡 What It Does

Break Point is a **real-time AI coaching platform** that combines four core technologies:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Break Point AI Coach                                 │
│                    Streamlit Dashboard + Python Backend                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  BALL TRACKING      │   TABLE DETECTION     │    POSE ESTIMATION            │
│  LAYER              │   LAYER               │    LAYER                      │
│                     │                       │                               │
│  • YOLO Detection   │   • Kimi K2 Think    │    • MediaPipe 33-pt          │
│  • 6D Kalman Filter │   • TTNet Fallback    │    • 2-4 Player Support       │
│  • Bounce Detection │   • Classical CV      │    • Joint Angle Calc         │
├─────────────────────┴───────────────────────┴───────────────────────────────┤
│                              ↓                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                         STATS ENGINE (HH/)                                   │
│                                                                              │
│  • Tactical Scoring    • Timing Analysis    • Biomechanics                  │
│  • Mental Patterns     • Rally Detection    • Shot Classification           │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ↓                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                     INTELLIGENCE LAYER (Snowflake)                           │
│                                                                              │
│  ┌─────────────────────┐    ┌─────────────────────┐                         │
│  │  Cortex EMBED       │    │  Cortex COMPLETE    │                         │
│  │  768-dim vectors    │───▶│  LLM Reasoning      │                         │
│  └─────────────────────┘    └─────────────────────┘                         │
│           │                          │                                       │
│           ▼                          ▼                                       │
│  ┌─────────────────────┐    ┌─────────────────────┐                         │
│  │  Vector Search      │    │  Dedalus Multi-Agent│                         │
│  │  Similar Matches    │    │  5 Specialized Tools│                         │
│  └─────────────────────┘    └─────────────────────┘                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ↓                                               │
│  ┌────────────────────────────┐    ┌────────────────────────────┐           │
│  │     Coaching Report        │    │     Annotated Video        │           │
│  │  • Biomechanics Grade      │    │  • Ball Trail Overlay      │           │
│  │  • Tactical Insights       │    │  • Skeleton Visualization  │           │
│  │  • Mental Pattern Alerts   │    │  • Mini-Map Display        │           │
│  └────────────────────────────┘    └────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1. Hawk-Eye Level Perception

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🎯 BALL TRACKING SYSTEM                               │
│                                                                              │
│   WHY IS IT HARD?                                                           │
│   ───────────────                                                           │
│   • Ball travels at 100+ km/h (appears as tiny 5-10 pixel blob)             │
│   • Crosses entire frame in just 6 frames (~0.2 seconds)                    │
│   • Gets hidden behind players, net, and table edges                        │
│                                                                              │
│   OUR SOLUTION: 6D Kalman Filter                                            │
│   ──────────────────────────────                                            │
│   Instead of just tracking WHERE the ball is, we track:                     │
│                                                                              │
│   Position (x, y)  +  Velocity (vx, vy)  +  Acceleration (ax, ay)           │
│       ↓                    ↓                       ↓                        │
│   Where is it?       How fast?             Spin/gravity effects             │
│                                                                              │
│   This lets us PREDICT where the ball will be even when we can't see it!    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### How It Works (Step by Step)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   STEP 1: DETECT                    STEP 2: PREDICT                         │
│   ─────────────────                 ───────────────                         │
│   ┌─────────────┐                   ┌─────────────┐                         │
│   │   Video     │                   │   Kalman    │                         │
│   │   Frame     │  ───YOLO───▶      │   Filter    │                         │
│   │      ●      │   finds ball      │   predicts  │                         │
│   └─────────────┘                   └─────────────┘                         │
│                                           │                                  │
│                                           ▼                                  │
│   STEP 4: OUTPUT                    STEP 3: TRACK                           │
│   ──────────────                    ──────────────                          │
│   ┌─────────────┐                   ┌─────────────┐                         │
│   │ Mini-Map    │                   │  Even if    │                         │
│   │ ●───●───●   │  ◀────────────    │  ball is    │                         │
│   │ ═══net═══   │   trajectory      │  hidden,    │                         │
│   │   ●───●     │                   │  we know    │                         │
│   └─────────────┘                   │  where it   │                         │
│                                     │  will be!   │                         │
│                                     └─────────────┘                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Smart Re-Acquisition (When Ball is Lost)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   Ball visible? ───▶ YES ───▶ TRACKING MODE (tight focus, 100px radius)     │
│        │                                                                     │
│        ▼                                                                     │
│       NO (lost 5+ frames)                                                   │
│        │                                                                     │
│        ▼                                                                     │
│   SEARCHING MODE (wider search, 200px radius)                               │
│        │                                                                     │
│        ▼                                                                     │
│   Still lost? (12+ frames)                                                  │
│        │                                                                     │
│        ▼                                                                     │
│   DESPERATE MODE (search entire table area)                                 │
│                                                                              │
│   ✅ Result: Tracks ball through 1.5 seconds of occlusion (45 frames!)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Bounce Detection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   How do we know when the ball bounces?                                     │
│                                                                              │
│        Ball falling ↓         Ball rising ↑                                 │
│              ●                     ●                                        │
│               ╲                   ╱                                         │
│                ╲                 ╱                                          │
│   ═══════════════●═══════════════════════════ table surface                 │
│                  ↑                                                          │
│              BOUNCE!                                                        │
│                                                                              │
│   Detection Rule:                                                           │
│   • Ball was moving DOWN (vy > 0)                                           │
│   • Ball is now moving UP (vy < 0)                                          │
│   • Contact point is ON the table                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Mental Intelligence Engine

Break Point detects **invisible behavioral patterns** that players miss:

- **Rhythm Consistency**: Tracks timing variance across rallies to detect when a player becomes robotic or chaotic under pressure
- **Pressure Handling**: Analyzes shot selection changes after losing critical points
- **Passive Streak Detection**: Identifies consecutive defensive shots when attack opportunities exist

#### Mental Pattern Detection

We quantify mental state through multiple metrics:

```
RHYTHM SCORE
─────────────
Rhythm = 1 - σ(Δt_shots) / μ(Δt_shots)

Where:
  σ = standard deviation of inter-shot timing
  μ = mean of inter-shot timing

Lower variance = more consistent rhythm
Score range: [0, 1] where 1 = perfectly consistent
```

```
PRESSURE RESPONSE INDEX (PRI)
─────────────────────────────
         Aggression(after_loss) - Aggression(baseline)
PRI  =  ─────────────────────────────────────────────────
                    Aggression(baseline)

Interpretation:
  PRI < -0.2  →  Player becomes passive under pressure (flag!)
  PRI ≈ 0     →  Stable mental state
  PRI > 0.2   →  Player increases aggression (potentially reckless)
```

### 3. AI-Powered Coaching

A multi-agent system provides **forensic-level analysis**:

#### Multi-Factor Coaching Score

Each shot is evaluated across four dimensions:

```
COACHING SCORE FORMULA
──────────────────────
Score = 0.30 × S_biomech + 0.35 × S_tactical + 0.20 × S_timing + 0.15 × S_rhythm

┌──────────────┬────────┬─────────────────────────────────────────────────┐
│ Factor       │ Weight │ Description                                     │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ Biomechanics │  30%   │ Knee bend (ideal: 130-150°), stance width,      │
│              │        │ shoulder rotation                               │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ Tactical     │  35%   │ Shot selection given ball position              │
│              │        │ (attacking high balls, defending low balls)     │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ Timing       │  20%   │ Contact point classification (Peak/Early/Late)  │
├──────────────┼────────┼─────────────────────────────────────────────────┤
│ Rhythm       │  15%   │ Consistency of movement patterns                │
└──────────────┴────────┴─────────────────────────────────────────────────┘
```

#### Tactical Decision Scoring

Shot quality is evaluated based on the ball's position relative to the net:

```
TACTICAL SCORING MATRIX
───────────────────────
Ball Height (h)    Shot Type              Score    Reasoning
───────────────────────────────────────────────────────────────
h > 50px          smash, drive, loop       95     Aggressive on opportunity
h > 50px          push                     70     Missed opportunity (flag!)
h < 0px           push, block              85     Appropriate defense
h < 0px           smash, loop              40     High-risk poor decision
───────────────────────────────────────────────────────────────

Where h = ball height above net (in pixels)
```

#### Timing Classification

Shot timing is classified based on ball trajectory phase:

```
TIMING CLASSIFICATION
─────────────────────
                    │ Apex (peak)
                   ╱│╲
                  ╱ │ ╲
         Rising ╱  │  ╲ Falling
               ╱   │   ╲
              ╱    │    ╲
─────────────╱─────│─────╲──────────── net

Contact Point Classification:
┌─────────────┬──────────────────────────┬───────┐
│ Class       │ Condition                │ Score │
├─────────────┼──────────────────────────┼───────┤
│ Peak        │ |y_contact - y_apex| < ε │  95   │  ← Optimal
├─────────────┼──────────────────────────┼───────┤
│ Early       │ vy < 0 at contact        │  80   │  ← Ball rising
├─────────────┼──────────────────────────┼───────┤
│ Late        │ vy > 0 at contact        │  65   │  ← Ball falling
└─────────────┴──────────────────────────┴───────┘
```

### 4. Cross-Match Intelligence

The system **remembers** and **learns** from every match:

- **Vector Embedding**: Each match summary is converted to a 768-dimensional semantic vector using Snowflake Cortex
- **Pattern Retrieval**: When analyzing a new match, the system finds the 3-5 most similar historical matches
- **RAG-Powered Insights**: The LLM receives both current match stats AND similar past matches for context-aware coaching

#### Similarity Search

```
VECTOR SIMILARITY (Cosine Distance)
───────────────────────────────────
                    e_A · e_B
Similarity(A, B) = ─────────────
                   |e_A| × |e_B|

Where e = 768-dimensional Cortex embedding

Process:
1. Match summary → Cortex EMBED_TEXT_768 → 768-dim vector
2. Query: "Find matches where player became passive after losing set 1"
3. VECTOR_COSINE_SIMILARITY returns top-k similar matches
4. LLM receives: current stats + similar match context → coaching
```

---

## 🛠️ How We Built It

### Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SPONSOR TECHNOLOGIES                                  │
├───────────────────┬───────────────────┬───────────────────┬─────────────────┤
│    SNOWFLAKE      │   DEDALUS LABS    │     KIMI K2       │    FLOWGLAD     │
│    ❄️ Cortex       │   🤖 Multi-Agent   │    🌙 Think        │    💳 Payments   │
│                   │                   │                   │                 │
│ • EMBED_TEXT_768  │ • 5 Local Tools   │ • Vision API      │ • Subscription  │
│ • COMPLETE (LLM)  │ • Agent SDK       │ • Hybrid CV+AI    │   Management    │
│ • VECTOR Search   │ • Claude/GPT-4.5  │ • Table Detection │   (planned)     │
├───────────────────┴───────────────────┴───────────────────┴─────────────────┤
│                                                                              │
│    ELEVEN LABS          FIGMA                                               │
│    🔊 Voice              🎨 Design                                           │
│    (planned)            UI/UX Prototyping                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CORE TECHNOLOGIES                                    │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│     Python      │     OpenCV      │    MediaPipe    │        YOLO           │
│    3.10+        │   Video/CV      │   Pose Est.     │    Object Det.        │
├─────────────────┼─────────────────┼─────────────────┼───────────────────────┤
│   Streamlit     │     NumPy       │     SciPy       │      filterpy         │
│   Dashboard     │    Arrays       │    Signals      │    Kalman Filter      │
└─────────────────┴─────────────────┴─────────────────┴───────────────────────┘
```

### Key Technical Innovations

#### 1. Adaptive Re-Acquisition System

Unlike simple trackers that lose the ball permanently, our system uses a **three-mode tracking approach**:

```python
# Re-acquisition modes with dynamic thresholds
MODE_TRACKING = 0    # Normal: tight outlier (80px), narrow search (100px)
MODE_SEARCHING = 1   # Lost 5+ frames: relaxed (250px), wider search (200px)
MODE_DESPERATE = 2   # Lost 12+ frames: accept anything in table ROI

def get_outlier_threshold(self):
    if self.mode == MODE_TRACKING:
        return 80 + self.missing_frames * 8  # Gradually relax
    elif self.mode == MODE_SEARCHING:
        return 250
    else:
        return 9999  # Accept any candidate
```

**Result**: Ball tracking continuity even through 45 frames of occlusion (1.5 seconds at 30fps).

#### 2. Bounce Detection Physics

```
BOUNCE DETECTION ALGORITHM
──────────────────────────
Bounce = True  IF:
    vy[k-1] > 0.3          (ball was moving downward)
    AND vy[k] < 0          (ball is now moving upward)
    AND (x, y) ∈ Table     (contact within table bounds)
    AND gap > 8 frames     (prevent duplicate detection)
```

#### 3. Multi-Strategy Table Detection

Detection follows a priority cascade:

```
┌──────────────────────────────────────────────────────────────────┐
│                    TABLE DETECTION CASCADE                        │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  Kimi K2 Think API Available? │
              └───────────────────────────────┘
                     │              │
                    Yes            No
                     │              │
                     ▼              ▼
        ┌─────────────────┐  ┌───────────────────────────┐
        │ Direct frame →  │  │  TTNet Segmentation       │
        │ corners extract │  │  Available?               │
        └─────────────────┘  └───────────────────────────┘
                │                   │              │
             Success              Yes            No
                │                   │              │
                ▼                   ▼              ▼
        ┌─────────────┐    ┌─────────────┐  ┌─────────────┐
        │  CORNERS +  │    │ Deep Learn  │  │ Classical   │
        │    NET      │    │ Table Mask  │  │ CV Pipeline │
        └─────────────┘    └─────────────┘  └─────────────┘
                                │                   │
                             Success            Success
                                │                   │
                                └─────────┬─────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │  CORNERS +  │
                                   │    NET      │
                                   └─────────────┘
                                          │
                                        Fail
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │ Manual JSON │
                                   │ Calibration │
                                   └─────────────┘
```

#### 4. Dedalus Multi-Agent Analysis

Five specialized local tools power the analysis:

```python
LOCAL_TOOLS = [
    analyze_biomechanics,     # Knee angle, stance width, shoulder rotation
    score_tactical_decision,  # Ball height vs shot selection
    evaluate_timing,          # Peak/Early/Late classification
    detect_mental_patterns,   # Rhythm degradation, passive streaks
    calculate_coach_score,    # Weighted aggregate (30/35/20/15)
]

# Agent orchestration via Dedalus SDK
# Using Kimi K2 Think for reasoning-intensive tasks (sponsor track!)
agent = Agent(
    model=["kimi-k2-think", "claude-sonnet-4-20250514"],  # Kimi K2 Think = primary
    tools=LOCAL_TOOLS + SNOWFLAKE_MCP_TOOLS,
    system_prompt=BIOMECHANICAL_ENGINE_PROMPT
)
```

---

## 🧗 Challenges We Faced

```
┌─ CHALLENGE 1: Fast Ball Tracking ─────────────────────────────────────────────┐
│                                                                                │
│  ❌ PROBLEM    Ball travels 100+ km/h, appears as 5-10px blob                  │
│                Crosses entire frame in ~6 frames                              │
│                Standard trackers fail on occlusion                            │
│                                                                                │
│  💡 INSIGHT    Balls undergo significant acceleration (spin + air resistance) │
│                                                                                │
│  ✅ SOLUTION   6D Kalman Filter with acceleration modeling                     │
│                + Temporal confirmation (3 of 5 frames to lock)                │
│                                                                                │
│  📊 RESULT     Tracks through 45-frame occlusions (1.5 seconds @ 30fps)       │
└────────────────────────────────────────────────────────────────────────────────┘

┌─ CHALLENGE 2: Multi-Strategy Table Detection ─────────────────────────────────┐
│                                                                                │
│  ❌ PROBLEM    Tables vary: blue/green/wood, lighting, LED barriers           │
│                Initial Hough detector: 1024+ pixel errors in tournaments      │
│                                                                                │
│  💡 INSIGHT    Semantic understanding + pixel precision needed together       │
│                                                                                │
│  ✅ SOLUTION   Cascading detection: Kimi K2 → TTNet → Classical CV            │
│                K2 = "that's the table, not scoreboard"                        │
│                CV = pixel-precise corner detection                            │
│                                                                                │
│  📊 RESULT     Robust detection across tournament/training footage            │
└────────────────────────────────────────────────────────────────────────────────┘

┌─ CHALLENGE 3: Mental Pattern Detection ───────────────────────────────────────┐
│                                                                                │
│  ❌ PROBLEM    "Mental state" has no ground truth labels                       │
│                Can't train supervised model on "choking under pressure"       │
│                                                                                │
│  💡 INSIGHT    Use proxy metrics from sports psychology research              │
│                                                                                │
│  ✅ SOLUTION   Compute from tracking data automatically:                       │
│                • Rhythm variance      → decision hesitation                   │
│                • Post-loss aggression → pressure response                     │
│                • Passive shot streaks → fear of errors                        │
│                                                                                │
│  📊 RESULT     Fully automatic, no human labeling required                    │
└────────────────────────────────────────────────────────────────────────────────┘

┌─ CHALLENGE 4: Multi-AI Integration ───────────────────────────────────────────┐
│                                                                                │
│  ❌ PROBLEM    Kimi K2 + Snowflake Cortex + Dedalus multi-agent               │
│                Different latencies, failure modes, output formats              │
│                                                                                │
│  ✅ SOLUTION   Every AI has a fallback chain:                                  │
│                • Kimi K2 fails    → Classical CV + TTNet                      │
│                • Cortex unavail   → Local analysis only                       │
│                • Dedalus timeout  → Direct Cortex COMPLETE                    │
│                                                                                │
│  📊 RESULT     Graceful degradation with feature availability logging         │
└────────────────────────────────────────────────────────────────────────────────┘

┌─ CHALLENGE 5: Actionable Coaching ────────────────────────────────────────────┐
│                                                                                │
│  ❌ PROBLEM    "Be more consistent" is useless advice                          │
│                Athletes need specific, drillable corrections                  │
│                                                                                │
│  ✅ SOLUTION   "Biomechanical Engine" coaching persona:                        │
│                • Timestamp-specific: "At 2:34, knee was 162°"                  │
│                • One concrete drill per weakness                              │
│                • Compare to athlete's own history, not abstract ideals        │
│                                                                                │
│  📊 RESULT     Personalized, actionable weekly training focus                 │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## What We Learned

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🔧 TECHNICAL INSIGHTS                              │
├────────────────────────────────────┬────────────────────────────────────────┤
│ Insight                            │ Why It Matters                         │
├────────────────────────────────────┼────────────────────────────────────────┤
│ State modeling > detection accuracy│ Kalman compensates for noisy detects   │
│ AI + CV hybrid beats either alone  │ Semantic + pixel precision together    │
│ Fallback chains are essential      │ Hackathon demo: anything can fail      │
└────────────────────────────────────┴────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           🎨 DESIGN LESSONS                                  │
├────────────────────────────────────┬────────────────────────────────────────┤
│ Lesson                             │ Why It Matters                         │
├────────────────────────────────────┼────────────────────────────────────────┤
│ Formulas build trust               │ Shows domain expertise, not just APIs  │
│ Visualizations > numbers           │ Mini-map >> JSON dump                  │
│ Pressure moments = the product     │ "Rhythm tripled at break point" > stats│
└────────────────────────────────────┴────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           📋 PROCESS LEARNINGS                               │
├────────────────────────────────────┬────────────────────────────────────────┤
│ Learning                           │ Why It Matters                         │
├────────────────────────────────────┼────────────────────────────────────────┤
│ Pick mature sponsor tools          │ Snowflake + Dedalus = solid docs       │
│ Build demo video backwards         │ Show-first, then build toward it       │
└────────────────────────────────────┴────────────────────────────────────────┘
```

---

## What's Next

```
═══════════════════════════════════════════════════════════════════════════════
                              🚀 ROADMAP
═══════════════════════════════════════════════════════════════════════════════

    NOW                    Q2 2026               Q3 2026              FUTURE
     │                        │                     │                    │
     ▼                        ▼                     ▼                    ▼
┌─────────┐            ┌───────────┐          ┌──────────┐        ┌──────────┐
│ 📹      │            │ 📈        │          │ 🔊       │        │ 🌍       │
│ Real-   │───────────▶│ Multi-    │─────────▶│ Voice    │───────▶│ Global   │
│ Time    │            │ Match     │          │ Coaching │        │ Platform │
│ Mode    │            │ Trends    │          │          │        │          │
└─────────┘            └───────────┘          └──────────┘        └──────────┘
  Live cam               Week/month            Eleven Labs          Flowglad
  feeds                  dashboards            integration          payments

═══════════════════════════════════════════════════════════════════════════════
                           🎯 LONG-TERM VISION
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  Club player in Mumbai = Same depth as Olympic training center          │
  │  Junior athletes = Build self-awareness before bad habits form          │
  │  Remote coaches = AI-analyzed match videos from anywhere                │
  └─────────────────────────────────────────────────────────────────────────┘

         The technology exists. The need is urgent. Break Point bridges it.
```

---

## Impact Potential

### Quantifiable Benefits

| Metric                    | Impact                                                                              |
| ------------------------- | ----------------------------------------------------------------------------------- |
| **Reduced Coaching Cost** | AI analysis at ~$5/match vs. $100+/hour for human analysts                          |
| **Faster Improvement**    | Data-driven feedback accelerates skill acquisition by targeting specific weaknesses |
| **Mental Awareness**      | Players gain insight into invisible patterns they'd never notice themselves         |
| **Remote Coaching**       | Coaches can analyze athletes anywhere in the world                                  |

### Sports Analytics Equity

The ITF estimates millions of competitive players worldwide lack access to professional-level analytics. Break Point could:

- Enable **remote coaching relationships** via shared AI analysis
- Help **junior athletes** develop mental resilience earlier
- Give **club-level competitors** the edge to compete at higher levels

---

## Built With

**Sponsor Technologies**:
`Snowflake` `Dedalus Labs` `Kimi K2` `Flowglad` `Eleven Labs` `Figma`

**Core Stack**:
`Python` `OpenCV` `MediaPipe` `YOLO` `Streamlit` `NumPy` `SciPy` `filterpy`

---

## Installation & Usage

### Prerequisites

- Python 3.10+
- Snowflake account (optional, for cloud features)
- Kimi K2 API key (optional, for AI detection)

### Setup

```bash
# Clone the repository
git clone https://github.com/akhilm2223/TT-HACKCOLUMBAI.git
cd TT-HACKCOLUMBAI

# Install dependencies
pip install -r requirements.txt

# Configure environment (optional)
cp .env.example .env
# Edit .env with your Snowflake/Kimi credentials
```

### Running Analysis

```bash
# Basic analysis (local CV only)
python main.py --video "path/to/match.mp4"

# With Kimi K2 AI detection
python main.py --video "path/to/match.mp4" --kimi

# With Snowflake Cortex coaching
python main.py --video "path/to/match.mp4" --coach

# Full pipeline
python main.py --video "path/to/match.mp4" --kimi --coach
```

### Output

- **Annotated Video**: `output_videos/table_tennis_analysis.mp4`
- **JSON Analysis**: `table_tennis_analysis.json`
- **Coaching Insights**: Console output + Snowflake storage (if configured)

---

## Try It Out

| Resource              | Link                                                                        |
| --------------------- | --------------------------------------------------------------------------- |
| **GitHub Repository** | [akhilm2223/TT-HACKCOLUMBAI](https://github.com/akhilm2223/TT-HACKCOLUMBAI) |
| **Demo Application**  | Coming Soon                                                                 |

---

> **Built for Columbia DevFest 2026** — Demonstrating the power of AI in democratizing sports analytics.
