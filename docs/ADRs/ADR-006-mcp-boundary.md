# ADR-006: MCP Integration Boundary

## Status
Accepted

## Context

AgentOS must interact with external tools, services, and data sources to execute agent workflows.

The platform may integrate with MCP servers to discover and invoke tools through a standardized protocol.

Directly embedding external tool implementations into agent workflows would increase coupling, reduce interoperability, and make tool integration and maintenance more difficult.

External tools may introduce security, reliability, data exposure, and execution risks.

AgentOS therefore requires a controlled tool integration boundary that separates tool discovery and communication from governance and execution authorization.

## Decision

AgentOS will integrate Model Context Protocol (MCP) through a dedicated tool integration boundary.

MCP integrations will encapsulate protocol communication, tool discovery, tool metadata handling, request construction, and response processing.

Discovered MCP tools will be represented internally using normalized tool metadata and execution interfaces where appropriate.

Tool discovery will not automatically grant execution permission.

Tool invocation requests must pass through the AgentOS governance and execution controls before an external tool is invoked.

The MCP integration boundary will support configurable server connections and controlled tool exposure.

External MCP server availability, capabilities, and responses must not be trusted without appropriate validation.

## Alternatives Considered

### Direct Integration of Every External Tool

Implement separate custom integrations for every external service.

Rejected as the primary integration strategy because it would increase integration maintenance, create inconsistent tool interfaces, and reduce interoperability.

Custom integrations may still be appropriate when MCP is unavailable or when a specialized integration is justified.

### MCP Without a Governance Boundary

Allow agents to discover and invoke MCP tools directly without centralized policy enforcement.

Rejected because tool discovery and protocol interoperability do not provide sufficient authorization, approval, tenant isolation, or execution safety.

### MCP with a Dedicated AgentOS Integration Boundary

Integrate MCP through a dedicated boundary while retaining centralized governance and execution controls.

Selected because it provides interoperability and a controlled integration architecture.

## Rationale

- Standardized external tool integration.
- Reduced integration coupling.
- Centralized tool discovery.
- Normalized tool metadata.
- Easier integration testing.
- Separation between tool connectivity and governance.
- Supports extensible external tool ecosystems.
- Enables controlled tool exposure to agent workflows.

## Consequences

### Positive

- Standardized tool integration boundary.
- Reduced dependence on individual tool implementations.
- Easier addition of compatible MCP servers.
- Centralized protocol handling.
- Separation of discovery and execution authorization.
- Improved integration testability.

### Negative

- Introduces MCP protocol and integration complexity.
- External server compatibility may vary.
- External server failures affect dependent workflows.
- Tool metadata may require normalization.
- Protocol integration does not eliminate external security risks.
- Additional validation and monitoring are required.

### Constraints

MCP tool discovery must not automatically authorize execution.

All tool invocation requests must pass through appropriate governance controls.

External tool inputs and outputs must be validated.

MCP server configuration, credentials, and connection permissions must be managed securely.

Tenant isolation must be enforced when tool connections or tool execution involve tenant-specific resources.

External MCP servers must be treated as potentially untrusted dependencies.

MCP must remain an integration protocol boundary rather than a replacement for AgentOS governance, workflow orchestration, or persistence architecture.

## Related Requirements

- FR-003
- FR-004
- FR-005
- FR-012
- NFR-003
- NFR-005
- NFR-007

## Related ADRs

- ADR-002
- ADR-005
- ADR-007
- ADR-009