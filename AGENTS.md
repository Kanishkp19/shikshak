# Engineering Coordination System (ECC) — Agent Instructions

This workspace is configured with the **Engineering Coordination System (ECC)** targeted for **Google Antigravity**.

---

## 0. Mandatory Prompt Middleware Protocol (ECC Interceptor)

> [!IMPORTANT]
> **EVERY prompt, request, question, or instruction submitted by the user MUST pass through the ECC Middleware Gateway before any action is executed or code is generated.**

When any user prompt arrives, the agent operates as the **ECC Orchestrator**, executing this mandatory lifecycle:

### Phase 1: Ingestion & Intent Classification
Analyze the intent of the prompt and classify it into its domain:
- **Feature Request / Major Enhancement** → Route to [`planner`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/planner.md)
- **Architecture / System Boundaries / Scaling** → Route to [`architect`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/architect.md)
- **Bug Fix / Logic Defect** → Route to [`tdd-guide`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/tdd-guide.md) & [`tdd-workflow`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/skills/tdd-workflow/SKILL.md)
- **Code Modification / Refactoring** → Route to [`code-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/code-reviewer.md)
- **Auth / Secrets / Database / Public API** → Route to [`security-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/security-reviewer.md) & [`database-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/database-reviewer.md)
- **Build / Compile / Type Failure** → Route to [`build-error-resolver`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/build-error-resolver.md)
- **Frontend / Next.js / React Component** → Route to [`typescript-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/typescript-reviewer.md)
- **Backend / FastAPI / Celery** → Route to [`python-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/python-reviewer.md)
- **Exploration / Codebase Research** → Route to [`search-first`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/skills/search-first/SKILL.md) & [`graphify`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/rules/graphify.md)

### Phase 2: Grounding & Context Pre-Flight
- Never guess code or edit files blindly. Run [`search-first`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/skills/search-first/SKILL.md) to inspect existing symbols, imports, and schemas.
- Bind relevant language rules (`common-*`, `typescript-*`, `python-*`).

### Phase 3: Gated Execution Standards
- For non-trivial modifications, plan before executing and present an implementation plan for approval.
- Enforce immutability (always create new immutable structures, never mutate existing ones).
- Enforce strict input validation (Zod on web client, Pydantic on FastAPI backend).

### Phase 4: Quality & Security Gate
- Validate all changes against [`code-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/code-reviewer.md) and [`security-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/security-reviewer.md) standards prior to completion.

### Response Transparency
Every assistant response MUST explicitly indicate its ECC dispatch routing:
`[ECC Gateway: Active | Dispatch: <subagent> | Domain: <domain>]`

---

## 1. Core Principles

1. **Agent-First Delegation** — Delegate domain-specific tasks to specialized subagents.
2. **Test-Driven Development** — Mandate test coverage before implementation using `tdd-workflow`.
3. **Security & Validation First** — Never compromise on security (`security-review`), enforce input validation and secret safety.
4. **Search-First Grounding** — Investigate codebase architecture and external references (`search-first`, `graphify`) before modifying files.
5. **Plan Before Execute** — Plan complex features, major refactorings, or migrations before making code changes (`planner`).

---

## 2. Subagents & Delegation Matrix

The following subagents are configured under [`.agents/agents/`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/) and can be delegated to:

| Subagent | Role & Scope | Trigger / Delegation When |
|---|---|---|
| [`planner`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/planner.md) | Implementation planning & breakdown | Complex features, architectural initiatives, refactorings |
| [`architect`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/architect.md) | High-level system design & scalability | System architecture decisions, module boundary definitions |
| [`code-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/code-reviewer.md) | Code quality, readability, maintainability | After creating or editing code, before finalizing changes |
| [`security-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/security-reviewer.md) | Vulnerability detection & security audit | Auth flows, database access, public APIs, input handling |
| [`build-error-resolver`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/build-error-resolver.md) | Build, compile, and type failure diagnosis | TypeScript/Python build errors, dependency mismatches |
| [`database-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/database-reviewer.md) | Supabase & PostgreSQL schema review | Migrations, RLS policies, query performance |
| [`typescript-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/typescript-reviewer.md) | Frontend TypeScript & Next.js review | Web app features (`apps/web`), React components |
| [`python-reviewer`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/agents/python-reviewer.md) | Backend Python & FastAPI review | API endpoints (`apps/api`), Celery tasks |

### Proactive Delegation Guidelines
- **Feature Requests / Non-trivial Refactoring:** Engage **`planner`** first to analyze scope and create an implementation plan.
- **System Architecture & Data Contracts:** Delegate to **`architect`** and **`database-reviewer`**.
- **Post-Implementation Review:** Trigger **`code-reviewer`** and **`security-reviewer`** prior to task completion.
- **Build / Type Breakages:** Hand off immediately to **`build-error-resolver`**.

---

## 3. Project Tech Stack & Structure

- **Frontend (`apps/web`)**: Next.js 15 (App Router), React 18, TypeScript, Tailwind CSS, Supabase SSR client (`@supabase/ssr`).
- **Backend (`apps/api`)**: Python 3, FastAPI, Celery, Pytest.
- **Database & Auth (`supabase/`)**: Supabase PostgreSQL with Row Level Security (RLS).
- **Knowledge Graph (`graphify-out/`)**: Graphify structural codebase graph.

---

## 4. Active Skills & Rules

### Core Skills ([`.agents/skills/`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/skills/))
- **`tdd-workflow`**: Test-driven development loop (RED -> GREEN -> REFACTOR).
- **`search-first`**: Grounded AST/code exploration and research before authoring.
- **`security-review`**: Security auditing, vulnerability scanning, and defense baseline checks.
- **`supabase` & `supabase-postgres-best-practices`**: Database operations, migrations, and RLS policies.

### Active Rules ([`.agents/rules/`](file:///Users/kanishk_pandey/Desktop/shikshak-ai/.agents/rules/))
- **Common Standards:** `common-agents.md`, `common-code-review.md`, `common-coding-style.md`, `common-development-workflow.md`, `common-git-workflow.md`, `common-patterns.md`, `common-performance.md`, `common-security.md`, `common-testing.md`.
- **TypeScript & Web:** `typescript-*.md`, `react-*.md`, `web-*.md`.
- **Python & FastAPI:** `python-*.md`.
- **Workspace Custom:** `agent_behavior.md`, `claude-design.md`, `graphify.md`, `studio_video_visuals.md`.

---

## 5. Development & Delivery Standards

1. **Immutability:** Do not mutate shared state or complex objects directly; return fresh immutable structures.
2. **Input Validation:** Enforce strict boundary validation using Zod on web clients and Pydantic on FastAPI backend.
3. **Error Handling:** Never swallow exceptions silently. Log server context and return structured client error messages.
4. **No Secrets in Code:** Use environment variables (`.env`). Never commit private keys, service role tokens, or passwords.
