# ADR-001: Modular Monolith Initially

## Status

Accepted

## Context

AgentOS is an enterprise agent execution
and governance platform.

The platform requires multiple logical
components, including:

- API
- Workflow orchestration
- Governance
- Tool execution
- State management
- Memory
- Observability
- Human approval

Deploying each component as an independent
microservice during the initial MVP would
introduce additional infrastructure,
network boundaries, operational overhead,
deployment complexity, and debugging challenges.

The initial project requires clear architectural
boundaries without unnecessary distributed
system complexity.

## Decision

AgentOS will initially be implemented
as a modular monolith.

The application will maintain explicit
logical boundaries between major components.

Modules must communicate through
defined interfaces and controlled
dependency boundaries.

The initial deployment will package
the application into a containerized
deployment unit.

Modules must not assume that they
will always remain in the same
deployment unit.

## Alternatives Considered

### Microservices

Each major component would be deployed
as an independent service.

Rejected for the initial MVP because
of additional operational complexity,
network communication overhead,
deployment coordination, and
distributed debugging requirements.

### Unstructured Monolithic Application

All functionality would be implemented
without explicit module boundaries.

Rejected because it would create
tight coupling, reduce testability,
and make future architectural evolution
more difficult.

### Modular Monolith

A single deployable application
with explicit internal module boundaries.

Selected because it provides
architectural separation without
unnecessary distributed infrastructure.

## Rationale

- Simplifies initial deployment.
- Reduces infrastructure complexity.
- Enables local development.
- Improves integration testing.
- Enables clear component boundaries.
- Supports incremental development.
- Allows future service extraction
  when justified by evidence.

## Consequences

### Positive

- Simpler deployment.
- Easier debugging.
- Reduced infrastructure overhead.
- Faster development.
- Easier local testing.
- Clear logical boundaries.

### Negative

- Modules share a deployment lifecycle.
- Scaling individual modules independently
  is initially limited.
- Poor module boundaries may create coupling.
- Future extraction requires migration work.

### Constraints

Modules must maintain explicit interfaces.

Cross-module dependencies must be controlled.

Shared infrastructure must not become
a substitute for proper module boundaries.

Service extraction must be justified
by measurable operational or scaling needs.

## Related Requirements

- FR-001
- FR-007
- NFR-001
- NFR-009

## Related ADRs

- ADR-002
- ADR-003
- ADR-009
- ADR-010