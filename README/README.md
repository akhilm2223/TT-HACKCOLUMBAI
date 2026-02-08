# Break Point AI - Architecture Diagrams

Below are the detailed Mermaid flowcharts for the DedalusLabs "Multi-Agent Coaching Brain" and the Snowflake "Intelligent Data Pipeline". You can view these directly in GitHub's markdown viewer.

## 1. DedalusLabs AI: Multi-Agent Coaching System

This diagram illustrates how the **Dedalus Orchestrator** receives a user query, delegates analysis to specialized sub-agents, cross-references with historical data via the Snowflake MCP tool, and synthesizes a final coaching report.

```mermaid
graph TD
    %% 1. USER INTERFACE LAYER
    subgraph UI [USER INTERFACE]
        direction TB
        User([USER / PLAYER])
        Query[/"MATCH QUERY"/]
        Response[/"COACHING REPORT"/]
    end

    %% 2. INTELLIGENCE LAYERS
    subgraph Brain [DEDALUS ORCHESTRATION]
        direction TB
        Orchestrator{{HEAD COACH AGENT}}

        subgraph Agents [SPECIALIZED SUB-AGENTS]
            direction LR
            Bio[BIOMECHANICS]
            Tac[TACTICAL]
            Men[MENTAL]
        end

        Synthesizer[INSIGHT SYNTHESIZER]
    end

    %% 3. KNOWLEDGE LAYER (SNOWFLAKE)
    subgraph Memory [KNOWLEDGE BASE]
        direction TB
        MCP((SNOWFLAKE MCP))
        Vectors[(VECTOR STORE)]
        History[(MATCH HISTORY)]
    end

    %% CONNECTIONS
    User --> Query
    Query --> Orchestrator

    Orchestrator -- "DELEGATE" --> Bio
    Orchestrator -- "DELEGATE" --> Tac
    Orchestrator -- "DELEGATE" --> Men

    Bio -- "ANGLE/STANCE" --> Orchestrator
    Tac -- "AGGRESSION" --> Orchestrator
    Men -- "FATIGUE" --> Orchestrator

    Orchestrator -.->|TOOL CALL| MCP
    MCP <--> Vectors
    MCP <--> History
    MCP -.->|RETRIEVAL| Orchestrator

    Orchestrator --> Synthesizer
    Synthesizer --> Response
    Response --> User
```

---

## 2. Snowflake: Intelligent Data Pipeline

This diagram shows the flow from raw video capture to the final user dashboard, highlighting how **VARIANT** data types, **Snowpark**, and **Cortex AI** work together within the Snowflake Data Cloud.

```mermaid
graph TD
    %% 1. INGESTION LAYER (EDGE)
    subgraph Edge [EDGE PROCESSING]
        direction TB
        Camera[CAMERA INPUT]
        CV[[COMPUTER VISION PIPELINE]]
        JSON[RAW JSON STREAM]
    end

    %% 2. DATA CLOUD (SNOWFLAKE)
    subgraph Snowflake [SNOWFLAKE DATA CLOUD]
        direction TB

        subgraph Storage [VARIANT STORAGE]
            RawTable[(TRACKING_EVENTS)]
        end

        subgraph Compute [SNOWPARK COMPUTE]
            FeatureEng[[METRIC CALCULATION]]
            StatsTable[(MATCH_STATS_VIEW)]
        end

        subgraph AI [CORTEX INTELLIGENCE]
            Embed[[CORTEX EMBEDDING]]
            VectorIndex[(VECTOR STORE)]
        end
    end

    %% 3. SERVING LAYER (SIS)
    subgraph App [SERVING LAYER]
        SiS{{STREAMLIT IN SNOWFLAKE}}
        Dashboard[INTERACTIVE DASHBOARD]
    end

    %% CONNECTIONS
    Camera --> CV
    CV --> JSON
    JSON -->|SNOWPIPE| RawTable

    RawTable --> FeatureEng
    FeatureEng --> StatsTable

    StatsTable --> Embed
    Embed --> VectorIndex

    StatsTable --> SiS
    VectorIndex -.->|SEMANTIC SEARCH| SiS
    SiS --> Dashboard
```
