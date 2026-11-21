# ADR-007: Deterministic Policy Enforcement Outside the LLM

## Status
Accepted

## Context

AgentOS executes AI-driven workflows that may interact with external tools, enterprise data, APIs, and sensitive operations.

LLMs are probabilistic systems and may produce incorrect, manipulated, inconsistent, or unsafe decisions.

Prompt instructions alone cannot reliably enforce authorization, tenant isolation, tool permissions, approval requirements, execution limits, or security policies.

AgentOS requires a security enforcement architecture that does not depend on an LLM correctly interpreting or following security instructions.

## Decision

AgentOS will implement deterministic governance and policy enforcement outside the LLM decision-making process.

The governance layer will independently evaluate execution requests against defined policies before protected operations are authorized.

Governance controls will include, as applicable:

- Tool authorization.
- Tenant isolation.
- Permission validation.
- Approval requirements.
- Execution constraints.
- Policy-based access control.
- Input validation.
- Risk-based execution restrictions.
- Policy enforcement for protected operations.

LLMs may propose actions, tools, arguments, or workflow decisions.

However, LLM-generated decisions will not independently authorize protected execution.

The governance layer will evaluate the execution request using trusted policy inputs, validated identity and tenant context, and defined enforcement rules.

Unauthorized or invalid execution requests will be rejected.

Human approval requirements will be enforced independently of LLM-generated claims about approval status.

## Alternatives Considered

### Prompt-Based Security

Enforce security requirements primarily through system prompts and model instructions.

Rejected because prompt instructions alone cannot provide deterministic authorization or reliable security enforcement.

### LLM-Based Security Decisions

Allow the LLM to independently decide whether its proposed actions are authorized.

Rejected because probabilistic model outputs cannot serve as the authoritative enforcement mechanism for access control and security policy.

### Deterministic Governance Layer

Enforce authorization, permissions, execution constraints, and approval requirements through independent policy enforcement components.

Selected because protected operations require enforceable and testable security boundaries independent of model behavior.

## Rationale

- Security enforcement independent of LLM behavior.
- Deterministic authorization decisions.
- Reduced risk of prompt injection bypass.
- Centralized governance.
- Enforceable tool permissions.
- Supports tenant isolation.
- Enforces human approval requirements.
- Enables security testing through deterministic scenarios.
- Separates agent reasoning from execution authorization.

## Consequences

### Positive

- Independent security enforcement.
- Predictable authorization behavior.
- Improved resistance to prompt-based authorization bypass.
- Centralized policy evaluation.
- Easier security testing.
- Clear separation between agent reasoning and protected execution.
- Better auditability of policy decisions.

### Negative

- Additional governance implementation complexity.
- Policy management requires careful design.
- Policy evaluation may introduce execution latency.
- Incorrect policies may block legitimate operations.
- Governance interfaces and policy rules require ongoing maintenance.

### Constraints

LLM outputs must never be treated as authoritative permission grants.

Protected tool execution must require independent authorization.

Authorization decisions must use trusted identity and tenant context rather than model-generated claims.

Human approval requirements must be enforced independently of the LLM.

Prompt injection must not be able to bypass governance controls.

Governance enforcement must fail closed for protected operations when required authorization information is unavailable or invalid.

Policy enforcement must be testable independently of agent orchestration and model behavior.

Security-critical policy decisions must not depend solely on cached or unvalidated data.

## Related Requirements

- FR-004
- FR-005
- FR-012
- FR-013
- NFR-003
- NFR-005
- NFR-007
- NFR-008

## Related ADRs

- ADR-002
- ADR-003
- ADR-004
- ADR-006
- ADR-009