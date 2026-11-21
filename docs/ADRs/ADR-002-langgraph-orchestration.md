# ADR-002: LangGraph for Agent Orchestration

## Status
Accepted

## Context

AgentOS requires a stateful agent orchestration layer capable of coordinating execution workflows, tool invocation, control flow, retries, state transitions, and human approval processes.

The platform must support multiple agent workflows, including Finance and Support reference workloads.

Agent execution must be observable, controllable, testable, and capable of recovering from interrupted workflows.

Unstructured agent loops or application-level orchestration implemented without explicit workflow boundaries would make execution behavior difficult to control, test, and maintain.

## Decision

AgentOS will use LangGraph as its initial agent orchestration framework.

Agent workflows will be modeled using explicit state, nodes, transitions, and conditional routing.

The orchestration layer will coordinate execution but will not independently authorize sensitive operations.

Governance decisions, permissions, approval requirements, and execution constraints will remain enforced by deterministic components outside the LLM's decision-making process.

Workflow state and checkpointing responsibilities will be integrated with the platform's durable execution and persistence strategy.

LangGraph will be used behind AgentOS orchestration interfaces to reduce unnecessary framework coupling.

## Alternatives Considered

### Custom Python Orchestration

Implement orchestration using custom Python functions, loops, and state management.

Rejected as the initial primary orchestration approach because implementing workflow state transitions, checkpointing integrations, conditional execution, recovery, and graph-level control would increase development and maintenance effort.

Custom orchestration may still be appropriate for simple deterministic workflows.

### LangChain Agent Abstractions Alone

Use higher-level agent abstractions without explicitly modeling the overall execution workflow.

Not selected as the primary orchestration architecture because AgentOS requires explicit workflow control, state transitions, governance boundaries, execution paths, and recovery behavior.

Individual LangChain components may still be used where appropriate.

### LangGraph

Use a graph-based orchestration framework with explicit state, nodes, transitions, conditional routing, and checkpoint integration.

Selected because it supports stateful workflows, controlled execution paths, agent coordination, and integration with persistence and recovery mechanisms.

## Rationale

- Explicit workflow state and transitions.
- Conditional routing and controlled execution paths.
- Support for stateful agent workflows.
- Integration with checkpointing.
- Easier workflow testing.
- Better visibility into agent execution.
- Support for multi-agent coordination when justified.
- Separation between orchestration and governance.
- Reduced need to implement core graph orchestration primitives from scratch.

## Consequences

### Positive

- Explicit orchestration structure.
- Easier debugging and workflow inspection.
- Supports stateful agent execution.
- Supports conditional workflow routing.
- Enables checkpoint integration.
- Facilitates testing individual workflow nodes.
- Supports coordinated multi-agent workflows.

### Negative

- Introduces framework dependency.
- Requires developers to understand graph-based execution.
- Incorrect graph design can create unnecessary complexity.
- Framework-specific state and execution abstractions may create migration costs.
- Framework behavior and version changes require compatibility testing.

### Constraints

LangGraph must not be treated as the governance or security enforcement layer.

LLM decisions must not directly bypass deterministic authorization controls.

Workflow graphs must have bounded execution, controlled retry behavior, and explicit failure handling.

AgentOS orchestration interfaces should avoid unnecessary coupling to framework-specific implementation details.

Simple workflows must not be converted into multi-agent graphs without a measurable reason.

## Related Requirements

- FR-002
- FR-003
- FR-004
- FR-005
- NFR-002
- NFR-003
- NFR-005

## Related ADRs

- ADR-001
- ADR-003
- ADR-007
- ADR-009