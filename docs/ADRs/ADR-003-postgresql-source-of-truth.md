# ADR-003: PostgreSQL as Source of Truth

## Status
Accepted

## Context

AgentOS requires persistent storage for execution records, workflow metadata, tenant information, approval requests, policy-related metadata, audit events, and other operational data.

Agent execution may involve retries, interruptions, concurrent requests, approval workflows, and recovery from failures.

The platform requires a reliable persistence layer that supports transactional operations, data integrity, structured querying, and durable records.

Using multiple databases as independent sources of truth during the initial MVP would increase operational complexity and make consistency management more difficult.

## Decision

PostgreSQL will serve as the primary relational database and authoritative source of truth for AgentOS operational data.

Persistent platform records will be stored in PostgreSQL according to defined schemas and data ownership boundaries.

The database will enforce appropriate integrity constraints, transaction boundaries, and tenant-related data isolation requirements.

The platform will use PostgreSQL transactions for operations requiring atomicity and consistency.

Checkpoint storage, execution records, approval metadata, audit records, and other persistent operational data will follow the platform's defined persistence architecture.

Other infrastructure components must not independently become authoritative sources for the same operational records without an explicitly documented architectural decision.

## Alternatives Considered

### SQLite

Use SQLite as the primary persistent database.

Rejected for the initial production-oriented platform because AgentOS requires concurrent workloads, centralized persistence, transactional coordination, and deployment flexibility.

SQLite may still be useful for isolated tests or lightweight local experimentation.

### MongoDB

Use a document-oriented database as the primary operational persistence layer.

Not selected because the initial AgentOS operational data model requires relational integrity, transactional relationships, structured querying, and consistent ownership boundaries.

Document storage may be considered for specialized workloads if future requirements justify it.

### PostgreSQL

Use a relational database supporting transactions, constraints, structured querying, and concurrent workloads.

Selected because it provides the required transactional consistency, relational integrity, operational maturity, and deployment flexibility.

## Rationale

- Transactional consistency.
- Relational integrity constraints.
- Structured querying.
- Reliable persistence.
- Support for concurrent workloads.
- Suitable for execution and approval records.
- Supports tenant-aware data models.
- Mature backup and recovery capabilities.
- Simplifies the initial infrastructure stack.
- Provides a foundation for durable execution.

## Consequences

### Positive

- Centralized authoritative operational data.
- Strong transactional guarantees.
- Reduced database infrastructure complexity.
- Reliable persistence for platform records.
- Easier data integrity enforcement.
- Simplified backup and recovery strategy.
- Supports structured operational reporting.

### Negative

- Database scaling may eventually become a bottleneck.
- Schema migrations require careful management.
- Database availability becomes critical to platform operations.
- Large workloads may require partitioning, replication, or other scaling strategies.
- Poor query design can degrade execution performance.

### Constraints

PostgreSQL will remain the authoritative source of truth for designated persistent operational records.

Database transactions must remain appropriately scoped.

Tenant isolation must be enforced through application-level controls and appropriate database-level safeguards where applicable.

Schema changes must use controlled migration procedures.

Database backups and recovery procedures must be validated.

Redis and other auxiliary infrastructure must not silently replace PostgreSQL as the authoritative persistence layer.

## Related Requirements

- FR-006
- FR-007
- FR-008
- FR-009
- NFR-001
- NFR-004
- NFR-006

## Related ADRs

- ADR-001
- ADR-004
- ADR-009
- ADR-010