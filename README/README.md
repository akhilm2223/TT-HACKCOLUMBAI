# Break Point AI - Architecture Diagrams

Below are the detailed Mermaid flowcharts for the DedalusLabs "Multi-Agent Coaching Brain" and the Snowflake "Intelligent Data Pipeline". You can view these directly in GitHub's markdown viewer.

## 1. DedalusLabs AI: Multi-Agent Coaching System

This diagram illustrates how the **Dedalus Orchestrator** receives a user query, delegates analysis to specialized sub-agents, cross-references with historical data via the Snowflake MCP tool, and synthesizes a final coaching report.

```mermaid
graph TD
    %% Nodes
    User([User / Player])
    Orchestrator{"Dedalus Orchestrator<br/>(The Head Coach)"}

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
graph TD
    %% Global Styling
    classDef box fill:#fff,stroke:#333,stroke-width:1px,color:#333;
    classDef snow fill:#29B5E8,stroke:#005c87,stroke-width:2px,color:white;
    classDef process fill:#e1f5fe,stroke:#0277bd,stroke-width:1px,color:#0277bd;

    %% ---------------------------------------------------------
    %% LAYER 1: INGESTION
    %% ---------------------------------------------------------
    subgraph Ingest [Ingestion Layer]
        direction LR
        Video[Raw Video] --> CV["Computer Vision (Python)"]
        CV --> JSON{"Raw JSON Stream"}
    end

    %% ---------------------------------------------------------
    %% LAYER 2: SNOWFLAKE DATA CLOUD
    %% ---------------------------------------------------------
    subgraph Cloud [Snowflake Data Cloud]
        direction TB
        
        subgraph Storage [Storage Layer]
            direction TB
            RawTable[("TRACKING_EVENTS (VARIANT)")]
        end
        
        subgraph Intelligence [Intelligence Layer]
            direction TB
            Snowpark[["Snowpark (Feature Eng.)"]]
            StatsTable[("MATCH_STATS (Structured)")]
            Cortex[["Cortex AI (Embeddings)"]]
        end
        
        subgraph Serving [App Layer]
            direction TB
            VectorIndex[("Vector Index")]
            SiS["Streamlit in Snowflake"]
        end
    end

    %% ---------------------------------------------------------
    %% CONNECTIONS
    %% ---------------------------------------------------------
    JSON -->|Snowpipe| RawTable
    
    RawTable --> Snowpark
    Snowpark --> StatsTable
    
    StatsTable --> Cortex
    Cortex --> VectorIndex
    
    StatsTable --> SiS
    VectorIndex -.->|Semantic Search| SiS

    %% Output
    User([User])
    SiS --> User

    %% Apply Styles
    class RawTable,StatsTable,VectorIndex snow;
    class CV,Snowpark,Cortex,SiS process;
    class Video,JSON,User box;
```
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
