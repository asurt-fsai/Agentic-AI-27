# Agentic-AI-27

Agentic AI software stack for the Formula Student AI (FSAI) team at ASU Racing. It automates engineering maintenance tasks (CI failures, version control hygiene, log analysis, documentation, and so on) with LLM agents that work alongside the team's developers.

The design is described in the FS-AI Agentic AI Research Report: [link to the report].

## Status

Early development. First use case: [module name]. Modules start at Level 0 (read-only, report-only) and only gain more autonomy once they pass their evaluation cases.

## Repository layout

```
src/fsai_agents/
  core/            shared infrastructure used by every module
    llm/             model-agnostic LLM interface
    memory/          persistent state and retrieval
    observability/   audit logging and tracing
    orchestrator/    agent graph, state, human-approval points
    policy/          autonomy levels, permissions, redaction
    tools/           typed tool interface (read vs write, provenance)
  integrations/    thin adapters for external systems (GitHub, Notion, rosbag2, ...)
  modules/         one package per use case (see below)
docs/              architecture notes and decision records
evals/             evaluation cases per module
tests/             unit tests, mirroring src/
deploy/            Docker and CI configuration
notebooks/         exploration only, not production code
scripts/           helper scripts
```

## Modules

| Module | Purpose | Owner | Status |
|---|---|---|---|
| github_automation | PR summaries, branch hygiene, conflict help | [name] | [not started / in progress] |
| ros2_ci | Triage failed ROS 2 CI runs and propose fixes | [name] | [ ] |
| simulation_testing | Scenario generation and regression sweeps | [name] | [ ] |
| log_monitoring | Rosbag and telemetry analysis, health reports | [name] | [ ] |
| notion_automation | Keep Notion tasks and docs in sync | [name] | [ ] |
| rag_chatbot | Cited answers from rulebooks, SOPs and docs | [name] | [ ] |

## Setup

Requires Python 3.10 or newer.

```
git clone git@github.com:asurt-fsai/Agentic-AI-27.git
cd Agentic-AI-27
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS
pip install -e .
cp .env.example .env            # then fill in your own values
```

Check the install:

```
python -c "import fsai_agents; print('ok')"
```

## Secrets

This repository is public. Never commit API keys, tokens or passwords.

- Real values go in `.env`, which is git-ignored.
- `.env.example` lists the variable names with placeholder values only.
- If a secret is ever committed by mistake, revoke it immediately. Deleting it in a later commit does not remove it from history.

## Contributing

1. Nobody pushes directly to `main`. It is protected by a ruleset.
2. Start from an up-to-date `main`:
   ```
   git checkout main
   git pull
   git checkout -b feature/<short-description>
   ```
3. Branch names: `feature/...`, `fix/...`, `docs/...`, `setup/...`.
4. Commit small and often, with clear messages.
5. Push your branch and open a pull request. At least one teammate must approve before it can be merged.
6. Keep PRs small enough to review in one sitting.
7. Delete the branch after merging.

Rules of thumb:
- Modules import from `core` and `integrations`, never from each other. If two modules need the same code, it moves into `core`.
- Every module ships with evaluation cases in `evals/`.
- No model weights, rosbags or large data files in the repo.
- Agents may not merge, release, change CI permissions, or touch anything that affects the vehicle.

## Adding a new dependency

Add it to `dependencies` in `pyproject.toml` in your PR, then everyone re-runs `pip install -e .`.



- [Name]: core and orchestrator
- [Name]: [modules]
- [Name]: [modules]
