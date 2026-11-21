# ADR-004: Redis for Selected Ephemeral and Cache Use Cases

## Status
Accepted

## Context

AgentOS may require low-latency data access for selected operational use cases, including caching, temporary coordination, rate limiting, and idempotency-related coordination.

Not all platform data requires permanent relational storage or transactional relationships.

However, using Redis as the primary source of truth for persistent operational records would introduce additional consistency, persistence, recovery, and data ownership concerns.

The platform requires a clear separation between authoritative persistent data and auxiliary low-latency operational data.

## Decision

AgentOS will use Redis for selected ephemeral, cache, and low-latency coordination use cases.

Redis may be used for:

- Cache entries.
- Rate-limiting counters.
- Short-lived coordination data.
- Temporary execution metadata.
- Selected idempotency coordination mechanisms.
- Other bounded ephemeral workloads when justified.

Redis will not serve as the authoritative source of truth for core persistent operational records.

Persistent execution records, approval records, authoritative audit records, and other designated durable platform data will remain backed by PostgreSQL.

Redis usage must include appropriate expiration, failure handling, and consistency considerations based on the specific workload.

Redis availability must not be assumed for operations that require authoritative persistent data.

## Alternatives Considered

### PostgreSQL Only

Use PostgreSQL for all persistence, caching, and coordination use cases.

Not rejected entirely. PostgreSQL remains the authoritative database and may support many workloads without Redis.

However, selected low-latency workloads may benefit from Redis where measured performance or operational requirements justify the additional infrastructure.

### Redis as the Primary Database

Use Redis as the primary storage layer for operational platform data.

Rejected because PostgreSQL provides the required authoritative relational persistence, transactional integrity, and structured data management.

### PostgreSQL with Selected Redis Usage

Use PostgreSQL for authoritative records and Redis for specifically justified auxiliary workloads.

Selected because it preserves data ownership boundaries while supporting low-latency operations where beneficial.

## Rationale

- Low-latency access for selected workloads.
- Supports cache-based performance optimization.
- Supports rate-limiting mechanisms.
- Supports temporary coordination.
- Reduces unnecessary database load where caching is justified.
- Preserves PostgreSQL as the authoritative source of truth.
- Avoids unnecessary dependence on Redis for critical persistent data.

## Consequences

### Positive

- Low-latency cache operations.
- Supports selected coordination patterns.
- Can reduce repeated database queries.
- Enables expiration-based temporary storage.
- Clear separation between persistent and auxiliary data.
- PostgreSQL remains the authoritative persistence layer.

### Negative

- Introduces additional infrastructure.
- Cache invalidation requires careful design.
- Redis failures may affect dependent functionality.
- Cached data may become stale.
- Operational complexity increases.
- Idempotency mechanisms require careful handling of expiration, concurrency, and failure scenarios.

### Constraints

Redis must not become an undocumented source of truth.

Cache entries must have appropriate expiration and invalidation strategies.

Redis-dependent functionality must define behavior during Redis outages.

Critical authorization decisions must not rely solely on stale cached information.

Idempotency mechanisms must be designed with concurrency, retry, expiration, and failure scenarios in mind.

Redis must not be introduced into a workflow unless its use is justified by a defined requirement.

## Related Requirements

- FR-006
- FR-008
- FR-010
- NFR-001
- NFR-002
- NFR-004

## Related ADRs

- ADR-001
- ADR-003
- ADR-007
- ADR-009