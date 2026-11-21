# ADR-005: Provider-Agnostic Model Adapter

## Status
Accepted

## Context

AgentOS requires access to language models for reasoning, structured outputs, agent decisions, and workflow execution.

The platform may use different model providers, hosted APIs, or locally deployed models depending on cost, latency, availability, capabilities, privacy requirements, and workload characteristics.

Directly coupling orchestration logic to a specific model provider would make provider migration, testing, configuration, and model selection more difficult.

The platform requires a controlled abstraction between agent orchestration and model provider implementations without eliminating provider-specific capabilities where necessary.

## Decision

AgentOS will implement a provider-agnostic model adapter boundary.

Agent orchestration components will interact with models through defined model interfaces rather than directly depending on provider-specific SDK implementations.

Provider adapters will encapsulate provider-specific API calls, configuration, request translation, response handling, error normalization, and supported capability mapping.

The model adapter boundary will support configuration-driven model selection.

Provider-specific capabilities that cannot be represented through the common interface may be exposed through explicitly defined extensions without unnecessarily coupling the orchestration layer to a provider.

The model adapter will not independently determine governance permissions or authorize tool execution.

## Alternatives Considered

### Direct Provider SDK Integration

Integrate provider SDKs directly into agent orchestration and workflow components.

Rejected because provider-specific dependencies would spread across the application, increasing coupling and making provider changes more difficult.

### Single Provider Permanently

Use one provider and intentionally avoid an abstraction layer.

Rejected because AgentOS may require different model providers or deployment options based on workload requirements, cost, reliability, and privacy considerations.

### Provider-Agnostic Adapter

Implement a shared model interface with provider-specific adapters.

Selected because it enables provider flexibility while maintaining controlled integration boundaries.

## Rationale

- Reduces provider coupling.
- Supports multiple model providers.
- Simplifies model configuration.
- Enables provider substitution.
- Facilitates testing with mock model adapters.
- Supports local and hosted model deployment options.
- Enables workload-specific model selection.
- Centralizes provider-specific error handling and integration logic.

## Consequences

### Positive

- Provider-independent orchestration interfaces.
- Easier provider substitution.
- Simplified mock-based testing.
- Centralized integration logic.
- Improved configuration flexibility.
- Potentially enables cost and latency optimization across providers.

### Negative

- Introduces abstraction complexity.
- Common interfaces may not represent every provider capability.
- Provider-specific features may require extensions.
- Abstraction maintenance becomes necessary as providers evolve.
- Poor abstraction design may hide important model behavior.

### Constraints

The adapter must not attempt to abstract every provider capability into an unnecessarily complex universal interface.

Provider-specific functionality must be exposed through clearly defined extensions when required.

Provider credentials must be handled through secure configuration and secret management practices.

Model selection must not bypass platform governance.

Provider failures must be normalized appropriately without losing diagnostic information.

Model adapters must support testing without requiring live provider API calls.

## Related Requirements

- FR-002
- FR-003
- FR-011
- NFR-002
- NFR-003
- NFR-007

## Related ADRs

- ADR-001
- ADR-002
- ADR-007
- ADR-008