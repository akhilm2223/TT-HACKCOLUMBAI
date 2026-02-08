# Break Point AI - Architecture Diagrams

Below are the detailed Mermaid flowcharts for the DedalusLabs "Multi-Agent Coaching Brain" and the Snowflake "Intelligent Data Pipeline". You can view these directly in GitHub's markdown viewer.

## 1. DedalusLabs AI: Multi-Agent Coaching System

This diagram illustrates how the **Dedalus Orchestrator** receives a user query, delegates analysis to specialized sub-agents, cross-references with historical data via the Snowflake MCP tool, and synthesizes a final coaching report.

```mermaid
graph TD
    %% Nodes
    User([User / Player])
    Query[Targeted Query]
    Orchestrator{{Dedalus Orchestrator}}

    %% Agents
    Bio[Biomechanics Agent]
    Tac[Tactical Agent]
    Men[Mental Agent]

    %% Snowflake Tools
    MCP[Snowflake MCP Tool]
    History[(Player History DB)]

    %% Output
    Synthesis[Insight Synthesis]
    Report[Coaching Report]

    %% Connections
    User --> Query
    Query --> Orchestrator

    Orchestrator -->|Delegates| Bio
    Orchestrator -->|Delegates| Tac
    Orchestrator -->|Delegates| Men

    Bio -->|Returns Analysis| Orchestrator
    Tac -->|Returns Analysis| Orchestrator
    Men -->|Returns Analysis| Orchestrator

    Orchestrator -.->|Tool Call| MCP
    MCP <-->|SQL & Vector Search| History
    MCP -.->|Returns Context| Orchestrator

    Orchestrator --> Synthesis
    Synthesis --> Report
    Report --> User
```

---

## 2. Snowflake: Intelligent Data Pipeline

This diagram shows the flow from raw video capture to the final user dashboard, highlighting how **VARIANT** data types, **Snowpark**, and **Cortex AI** work together within the Snowflake Data Cloud.

```mermaid
graph TD
    %% Ingestion
    Video[Raw Video]
    CV[Computer Vision Pipeline]
    JSON[Raw JSON Stream]

    %% Snowflake Data
    RawTable[(TRACKING_EVENTS - VARIANT)]

    %% Compute
    Snowpark[[Snowpark Metric Calc]]
    StatsTable[(MATCH_STATS - Structured)]

    %% AI
    Cortex[[Cortex AI Embeddings]]
    VectorIndex[(Vector Search Index)]

    %% App
    SiS[Streamlit in Snowflake]
    UserNode([User / Coach])

    %% Flow
    Video --> CV
    CV --> JSON
    JSON -->|Snowpipe| RawTable

    RawTable --> Snowpark
    Snowpark --> StatsTable

    StatsTable --> Cortex
    Cortex --> VectorIndex

    StatsTable --> SiS
    VectorIndex -.->|Semantic Search| SiS
    SiS --> UserNode
```
