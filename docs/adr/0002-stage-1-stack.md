# ADR 0002: Stage 1 stack

**Status:** Proposed · 2026-11-03 · Source: *Brave Clinical System - Stage 1 Technical Decisions*

## Decision

- **API:** Python FastAPI modular monolith, managed with uv. Module boundaries enforced by import-linter.
- **Data access:** SQLAlchemy 2 (plain PostgreSQL) and Pydantic v2.
- **Web:** React + TypeScript (Vite), Tailwind CSS; React Aria for accessible widgets.
- **Worker:** separate process for reports, messages, rescoring and audit export (job library still to choose).
- **CI:** GitHub Actions (tests, lint, types, migrations on an empty database), gitleaks, Semgrep, Trivy, Dependabot.

## Consequences

One backend runtime and one deployable unit for a small team. Scoring stays pure Python
with no I/O, so it is deterministic and testable.
