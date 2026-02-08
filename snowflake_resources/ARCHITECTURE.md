# Break Point AI - Architecture Diagrams

Below are the detailed Mermaid flowcharts for the DedalusLabs "Multi-Agent Coaching Brain" and the Snowflake "Intelligent Data Pipeline". You can view these directly in GitHub's markdown viewer.

## 1. DedalusLabs AI: Multi-Agent Coaching System

This diagram illustrates how the **Dedalus Orchestrator** receives a user query, delegates analysis to specialized sub-agents, cross-references with historical data via the Snowflake MCP tool, and synthesizes a final coaching report.

```mermaid
graph TD
    %% Nodes
    User([User / Player])
    Orchestrator{Dedalus Orchestrator<br/>(The Head Coach)}

    subgraph "Specialized Agents (The Team)"
        Bio[Biomechanics Agent]
        Tac[Tactical Agent]
        Men[Mental Agent]
    end

    subgraph "External Memory (Snowflake)"
        MCP[(Snowflake MCP Tool)]
        History[(Player History DB)]
    end

    Synthesis[Insight Synthesis]
    Report([Final Coaching Report])

    %% Flows
    User -->|Targeted Query: 'Why is my forehand weak?'| Orchestrator

    Orchestrator -->|Analyze Posture| Bio
    Bio -->|Calculate: Knee Angle, Stance Width| Orchestrator

    Orchestrator -->|Analyze Choices| Tac
    Tac -->|Calculate: Aggression Index, Shot Placement| Orchestrator

    Orchestrator -->|Analyze Psychology| Men
    Men -->|Detect: Passive Streaks, Fatigue| Orchestrator

    Orchestrator -.->|Tool Call: query_similar_matches| MCP
    MCP <-->|SQL Query & Vector Search| History
    MCP -.->|Return: Context from Past Matches| Orchestrator

    Orchestrator -->|Aggregate All Insights| Synthesis
    Synthesis -->|Generate Recommendations| Report
    Report -->|Display Advice| User

    %% Styling
    classDef main fill:#f9f,stroke:#333,stroke-width:2px;
    classDef sub fill:#bbf,stroke:#333,stroke-width:1px;
    classDef db fill:#29B5E8,stroke:#333,stroke-width:2px,color:white;

    class Orchestrator,Synthesis main;
    class Bio,Tac,Men sub;
    class MCP,History db;
```

---

## 2. Snowflake: Intelligent Data Pipeline

This diagram shows the flow from raw video capture to the final user dashboard, highlighting how **VARIANT** data types, **Snowpark**, and **Cortex AI** work together within the Snowflake Data Cloud.

```mermaid
graph LR
    %% Inputs
    Video[Raw Match Video]

    subgraph "Edge / Local Processing"
        CV[Computer Vision Pipeline<br/>(Python/Mediapipe)]
        JSON{Raw JSON Stream<br/>(Ball x,y, Skeleton)}
    end

    subgraph "Snowflake Data Cloud (Secure Boundary)"
        %% Storage
        RawTable[(TRACKING_EVENTS Table<br/>Data Type: VARIANT)]

        %% Compute / Transformation
        Snowpark[[Snowpark Python<br/>Metric Calculation]]
        StatsTable[(MATCH_STATS_VIEW<br/>Structured Data)]

        %% AI Enrichment
        Cortex[[Cortex AI<br/>Vector Embeddings]]
        VectorIndex[(Vector Search Index)]

        %% Application Logic
        SiS[Streamlit in Snowflake<br/>(Dashboard App)]
    end

    %% Flow Connections
    Video --> CV
    CV -->|Extracts| JSON
    JSON -->|Snowpipe Streaming| RawTable

    RawTable -->|Flatten & Compute| Snowpark
    Snowpark -->|Save Metrics| StatsTable

    StatsTable -->|Generate Semantic Embeddings| Cortex
    Cortex -->|Store Vectors| VectorIndex

    StatsTable -->|Query Metrics| SiS
    VectorIndex -.->|Semantic Search Query| SiS

    %% Output
    User([End User / Coach])
    SiS -->|Interactive Dashboard| User

    %% Styling
    classDef source fill:#e1e1e1,stroke:#333,stroke-width:1px;
    classDef ingest fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef snow fill:#29B5E8,stroke:#005c87,stroke-width:2px,color:white;
    classDef app fill:#FF4B4B,stroke:#990000,stroke-width:2px,color:white;

    class Video,CV,JSON source;
    class RawTable,StatsTable,VectorIndex snow;
    class Snowpark,Cortex ingest;
    class SiS app;
```
