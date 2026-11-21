# ADR-009: Durable Execution and Checkpoint Strategy

## Status
Accepted

## Context

AgentOS executes stateful agent workflows that may involve multiple steps, external tool invocations, human approvals, retries, and long-running operations.

Workflow execution may be interrupted by process crashes, infrastructure failures, timeouts, deployment changes, or external dependency failures.

Keeping workflow state exclusively in process memory would make recovery from execution interruptions unreliable.

Restarting workflows from the beginning may result in duplicated operations, inconsistent state, repeated external side effects, or unnecessary model and tool costs.

AgentOS requires a persistence and recovery strategy that enables interrupted workflows to resume safely while preserving execution integrity.

## Decision

AgentOS will implement durable workflow execution through persistent workflow state and checkpointing integrated with its orchestration and persistence architecture.

LangGraph checkpointing will be integrated with the platform's persistence strategy using PostgreSQL-backed durable storage.

Workflow execution state required for recovery will be persisted at defined checkpoints.

The execution architecture will support recovery of eligible interrupted workflows from persisted state rather than relying exclusively on process memory.

Workflow state recovery must be coordinated with governance, execution status, approval state, and external side-effect handling.

Retries and recovery must not assume that external operations are automatically safe to repeat.

AgentOS will use explicit execution identifiers and appropriate idempotency mechanisms to control duplicate execution risks.

Human approval workflows must be able to persist their state while awaiting approval and resume through controlled execution transitions.

The durable execution design will initially use the capabilities provided by the selected orchestration and persistence components rather than introducing a separate distributed workflow engine without demonstrated need.

## Alternatives Considered

### In-Memory Execution State

Maintain workflow state exclusively within application memory.

Rejected because execution state would be lost when application processes terminate or restart.

### Restart Workflows from the Beginning

Restart interrupted workflows from their initial execution steps.

Rejected as the default recovery strategy because it may repeat completed operations, increase execution costs, and create duplicate external side effects.

This approach may still be appropriate for specific workflows when restart behavior is explicitly safe.

### Durable Checkpoint-Based Execution

Persist workflow state and recover eligible interrupted workflows from defined checkpoints.

Selected because it provides a foundation for controlled recovery, long-running workflows, approval interruptions, and failure handling.

### Separate Distributed Workflow Engine

Introduce an independent distributed workflow orchestration platform immediately.

Not selected for the initial MVP because it would increase infrastructure, integration, and operational complexity before the platform demonstrates a requirement for a separate workflow engine.

It may be reconsidered if future workload requirements justify it.

## Rationale

- Persistent workflow state.
- Recovery after application interruptions.
- Supports long-running workflows.
- Supports approval-based suspension and resumption.
- Reduces unnecessary workflow restarts.
- Improves execution observability.
- Enables controlled retries.
- Integrates with PostgreSQL persistence.
- Avoids introducing a separate workflow engine prematurely.

## Consequences

### Positive

- Workflow state can survive process interruptions.
- Enables controlled recovery.
- Supports long-running workflows.
- Supports human approval suspension and resumption.
- Reduces reliance on in-memory execution state.
- Provides a foundation for execution continuity.
- Supports persisted execution history.

### Negative

- Checkpoint persistence introduces additional complexity.
- Recovery logic requires careful implementation.
- Persistent state may require schema evolution.
- Checkpointing may introduce storage and latency overhead.
- Recovery does not automatically guarantee exactly-once external execution.
- External side effects require additional idempotency and reconciliation strategies.

### Constraints

Workflow state required for recovery must be persisted.

Recovery must validate persisted state before resuming execution.

Retries must be bounded and explicitly defined.

External side effects must not be assumed to be exactly-once.

Idempotency mechanisms must be implemented where duplicate execution could cause harmful or inconsistent outcomes.

Human approval state must be persisted and independently validated before resuming protected operations.

Checkpoint data must follow tenant isolation and access control requirements.

Checkpoint persistence must not replace authoritative governance or execution status validation.

The initial implementation must avoid introducing a separate distributed workflow engine unless justified by measurable requirements.

## Related Requirements

- FR-006
- FR-007
- FR-008
- FR-009
- FR-016
- NFR-001
- NFR-004
- NFR-005
- NFR-006

## Related ADRs

- ADR-001
- ADR-002
- ADR-003
- ADR-004
- ADR-007
- ADR-008
- ADR-010