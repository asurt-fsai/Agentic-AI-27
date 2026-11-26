# ADR-001: Knowledge Ingestion, Sensitivity Tagging, and Chunking Architecture (T18–T20)

- **Status:** Proposed (P1 Foundation — T18)
- **Date:** 2026-11-26
- **Owner:** Data & Retrieval Lane (Amir)
- **References:** `RESEARCH DOC.md` §§7.4, 9.1–9.10; `Tasks.pdf` (`T18`, `T19`, `T20`, `T27`)

---

## 1. Context

The FS-AI Agentic AI stack (`fsai_agents`) requires a shared ingestion and retrieval backbone (`core/memory/` + `core/policy/`) to index:
1. **FS-AI Competition Rules** (`FS-AI 2026 Rules v1`, future `FS2027`).
2. **GitHub Repositories** (code, launch files, configs, `README.md`, PRs/issues).
3. **Read-Only Notion Exports** (design docs, onboarding pages, meeting notes).

At the same time, the system must enforce strict privacy, competition compliance, and cost controls:
- **No silent cloud egress (`R15`, `R16`, `R20`):** `local-only` and `excluded` content must never be sent to external cloud parsers or LLM APIs.
- **Hard exclusions (`T19`, `R16`):** Secrets (`.env`, API keys, tokens), raw subteam survey spreadsheets, and Slide-51 alumni personal phone numbers must never enter the index.
- **Model gateway isolation (`§7.4`):** Any LLM calls (e.g., contextual enrichment or query-time generation) must route exclusively through `fsai_agents.core.llm.models.get_model`, never direct vendor SDK imports.

---

## 2. Decisions

### 2.1 Parser Policy (`Docling` Local Default, `LlamaParse` `api-ok` Only)
- **Default parser:** Local `Docling` (for PDFs/DOCX/complex layouts) and native local text/AST readers (for `.md`, `.txt`, `.py`).
- **Cloud parser (`LlamaParse`):** Permitted **only** when a source is explicitly tagged `api-ok` in the source manifest. Calling `LlamaParse` on `local-only` or `excluded` sources raises `PermissionError`.

### 2.2 Sensitivity & Access Tagging (`T19`)
Every source in `configs/sources.json` carries:
- `sensitivity`: `"api-ok"` | `"local-only"` | `"excluded"`
- `acl`: `"public"` | `"team-internal"` | `"maintainer-only"`
- `source_id`, `source_type` (`"rulebook"` | `"repo"` | `"notion"`), `version` / `edition`, and `subteam` / `namespace`.

Path-level and content-level guards automatically block `.env*`, `*secret*`, `*credential*`, `*survey*`, and `*alumni*contact*` files, and flag/block raw phone-number or token patterns before indexing.

### 2.3 Structure-Aware Chunking (`T20` / `T27`)
1. **Markdown & Notion exports:** Split by heading hierarchy, attaching the full heading breadcrumb (`Doc > Section > Subsection`) as a situating header while keeping **Markdown tables** and **fenced code blocks** whole.
2. **FS-AI Rulebook:** Split by clause/rule ID (e.g., `IN2.2.2`, `D1.3.1`, `T4.5.1`) and store `edition` (e.g., `FS2026-v1`) and `clause_id` in chunk metadata.
3. **Python code (`cAST` pattern):** Split by top-level `class`, `def`, and `async def` AST nodes with module path and symbol name metadata, falling back to bounded line chunks if a file has syntax errors.

### 2.4 Storage & Portability
- **Target production store:** PostgreSQL + `pgvector` 0.8 (with `sensitivity`, `acl`, `edition`, and `source_id` columns for pre-retrieval filtering / RLS).
- **P1 offline / CI store:** `JsonlChunkStore` in `core/memory/store.py` implements the same `ChunkStore` protocol with idempotent upserts and sensitivity/ACL filtering, allowing deterministic CI tests and local dry-runs without requiring Docker or PostgreSQL.

---

## 3. Consequences

- **Positive:** Modules (`rag_chatbot`, `ros2_ci`, `github_automation`) share one policy-enforced ingestion backbone in `core/memory/` and `core/policy/`; CI stays fast and free of heavy ML/DB downloads.
- **Deferred to P2 (`T26`–`T28`):** Dense embedding generation (`BAAI/bge-m3`), BM25 + RRF hybrid search, `bge-reranker-v2-m3`, and live PostgreSQL + `pgvector` 0.8 deployment.
