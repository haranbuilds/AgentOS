# AgentOS

**Enterprise Agent Execution and Governance Platform**

AgentOS is a platform for building, orchestrating, governing, and evaluating AI agent workflows.

The platform focuses on controlled tool execution, policy enforcement, durable workflow execution, human approvals, observability, and reproducible evaluation.

## Architecture Principles

- Modular monolith initially.
- Explicit module boundaries.
- Stateful agent orchestration.
- Deterministic policy enforcement outside the LLM.
- PostgreSQL as the authoritative persistence layer.
- Redis for selected ephemeral and cache use cases.
- MCP as a controlled external tool integration boundary.
- Durable workflow execution.
- Frozen benchmark evaluation.
- Containerized deployment.

## Technology Stack

- Python 3.11+
- uv
- LangGraph
- FastAPI
- PostgreSQL
- Redis
- MCP
- Docker
- Docker Compose
- Ruff
- mypy
- pytest

## Project Structure

The platform is organized around logical modules for orchestration, governance, tools, storage, runtime execution, observability, and evaluation.

## Development Setup

### Prerequisites

- Python 3.11+
- uv
- Git
- Docker
- Docker Compose

### Setup

Clone the repository and enter the project directory.

Install project dependencies:

```bash
uv sync
```

Activate the virtual environment if desired:

```bash
.venv\Scripts\Activate.ps1
```

Create your local environment configuration:

```powershell
Copy-Item .env.example .env
```

### Quality Checks

Run Ruff linting:

```bash
uv run ruff check .
```

Run Ruff formatting check:

```bash
uv run ruff format --check .
```

Run strict type checking:

```bash
uv run mypy --strict src
```

Run tests:

```bash
uv run pytest
```

## Logging Conventions

AgentOS uses structured application logging.

Logs should provide operational context without unnecessarily exposing secrets, credentials, sensitive user data, or protected enterprise information.

Log levels:

- DEBUG: Detailed diagnostic information for development and troubleshooting.
- INFO: Normal lifecycle events and significant operational events.
- WARNING: Unexpected conditions that do not prevent continued execution.
- ERROR: Failed operations requiring investigation.
- CRITICAL: Severe failures affecting essential platform functionality.

Logging requirements:

- Use Python's standard logging framework.
- Use module-level loggers.
- Prefer structured fields or consistent contextual messages.
- Include execution identifiers where available.
- Include tenant identifiers only where safe and necessary.
- Avoid logging credentials, tokens, API keys, and sensitive payloads.
- Avoid using print statements for application logging.
- Keep logging behavior consistent across modules.

## Configuration

Configuration must be supplied through environment variables or other controlled configuration mechanisms.

Secrets must not be committed to source control.

`.env.example` contains placeholders and documentation for local configuration.

## Testing

AgentOS testing will be organized into:

- Unit tests.
- Integration tests.
- Security tests.
- Chaos tests.
- Evaluation tests.

Testing must validate correctness, governance enforcement, execution reliability, and failure behavior.

## Architecture Documentation

Architecture decisions are documented in `docs/ADRs/`.

System architecture, security considerations, evaluation methodology, and operational procedures are documented under `docs/`.

## Status

AgentOS is under active development.

The initial implementation focuses on establishing the engineering foundation before implementing platform capabilities.
