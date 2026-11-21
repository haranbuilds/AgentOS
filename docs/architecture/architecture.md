# AgentOS — System Architecture

## 1. Purpose

This document defines the internal architecture
of AgentOS, including its major components,
responsibilities, interactions, and execution flow.

AgentOS is designed as a modular,
governed agent execution platform.

The architecture prioritizes:

- Security
- Reliability
- Observability
- Durable execution
- Extensibility
- Testability
- Operational simplicity

---

## 2. Architectural Style

AgentOS follows a modular application architecture
with explicit component boundaries.

The initial MVP is deployed as a containerized
application rather than a distributed microservice
architecture.

Components are separated logically to ensure
independent responsibilities, testability,
and maintainability.

Distributed services may be introduced later
when justified by scalability or isolation needs.

---

## 3. Major Architectural Components

### 3.1 API Layer

Responsibilities:

- Expose workflow execution APIs
- Validate API request schemas
- Authenticate requests
- Resolve tenant context
- Validate access permissions
- Return execution identifiers
- Expose workflow status
- Handle cancellation requests

The API layer must not contain agent reasoning
or business workflow logic.

### 3.2 Orchestration Engine

Responsibilities:

- Execute agent workflows
- Manage workflow transitions
- Route execution between nodes
- Coordinate agents and tools
- Manage workflow lifecycle
- Handle bounded loops
- Coordinate execution interruption
- Coordinate recovery

LangGraph is the initial orchestration framework.

### 3.3 Governance Engine

Responsibilities:

- Evaluate execution permissions
- Enforce tool authorization
- Apply policy restrictions
- Validate execution context
- Enforce execution limits
- Determine approval requirements
- Prevent unauthorized operations

Governance decisions must not rely solely
on LLM-generated decisions.

### 3.4 Tool Execution Gateway

Responsibilities:

- Receive tool execution requests
- Validate tool contracts
- Enforce authorization
- Apply execution timeouts
- Enforce resource limits
- Handle tool errors
- Record execution events
- Support controlled MCP integrations

Tools must not be directly executed
without the required governance checks.

### 3.5 State and Checkpoint Manager

Responsibilities:

- Persist workflow state
- Persist execution checkpoints
- Support workflow resumption
- Maintain execution metadata
- Handle state transitions
- Support recovery after interruptions

PostgreSQL is the initial persistence backend.

### 3.6 Context and Memory Manager

Responsibilities:

- Construct execution context
- Manage context boundaries
- Control context size
- Handle context compaction
- Retrieve relevant memory
- Persist approved memory
- Prevent unauthorized memory access

Memory must follow tenant isolation
and security policies.

### 3.7 Human Approval Manager

Responsibilities:

- Identify approval-required actions
- Create approval requests
- Persist approval status
- Validate approval identity
- Process approval or rejection
- Resume or terminate workflows
- Record approval events

Approval must be bound to the specific
action being approved.

### 3.8 Observability Manager

Responsibilities:

- Record structured logs
- Track workflow execution
- Track tool execution
- Record security events
- Track workflow failures
- Measure latency
- Track token usage
- Track execution costs
- Support debugging and evaluation

### 3.9 Evaluation Engine

Responsibilities:

- Evaluate workflow outcomes
- Measure task success
- Measure tool selection accuracy
- Evaluate policy compliance
- Measure execution reliability
- Benchmark performance
- Identify regression failures

Evaluation must support repeatable experiments.

---

## 4. Logical Architecture

```mermaid
flowchart TD

    CLIENT[Client Applications]

    subgraph PLATFORM["AgentOS"]
        API[API Layer]

        subgraph CORE["Execution Core"]
            ORCH[Orchestration Engine]
            GOV[Governance Engine]
            TOOL[Tool Execution Gateway]
            CTX[Context and Memory Manager]
            APPROVAL[Human Approval Manager]
        end

        STATE[State and Checkpoint Manager]
        OBS[Observability Manager]
        EVAL[Evaluation Engine]
    end

    LLM[LLM Provider]
    MCP[MCP Servers and Enterprise Tools]
    DB[(PostgreSQL)]

    CLIENT --> API
    API --> ORCH

    ORCH --> GOV
    ORCH --> CTX
    ORCH --> APPROVAL
    ORCH --> STATE
    ORCH --> OBS

    GOV --> TOOL
    TOOL --> MCP
    ORCH --> LLM

    STATE --> DB
    OBS --> DB
    APPROVAL --> DB
    CTX --> DB

    EVAL --> ORCH
    EVAL --> OBS