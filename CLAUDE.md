# PulseScope Project Governance

> Rules first, work second. Any agent touching this project must read this file first.

## Project Overview

**PulseScope** is an event-driven supply-chain risk inference engine for commodity/chemical enterprises. It monitors global geopolitical, shipping, and price events, then outputs structured risk reports via MCP Skill, REST API, and a web frontend.

## Directory Structure

```
pulsescope/
├── src/pulsescope/          # Python source code
│   ├── ingestion/           # Data ingestion (news, announcements)
│   ├── extraction/          # LLM-based event extraction
│   ├── knowledge/           # Knowledge graph (NetworkX + seeds)
│   ├── inference/           # Risk inference engine
│   ├── output/              # MCP Skill / output adapters
│   └── api/                 # FastAPI REST server
├── tests/                   # pytest suite (mirror src/ structure)
├── frontend/                # Next.js 14 + Tailwind web UI
├── data/seeds/              # Seed data (companies.json, etc.)
├── reports/                 # Generated demo reports (HTML)
├── docs/                    # Human-readable docs
├── scripts/                 # Build / utility scripts
└── tmp/                     # Transient files (gitignored, clean monthly)
```

## Naming Conventions

- **Python modules**: `snake_case.py`
- **React components**: `PascalCase.tsx`
- **Config / docs**: `kebab-case.md`
- **Date-prefixed artifacts**: `YYYY-MM-DD-description.ext`

## Git & Branching

- `main` — production-ready, tests must pass.
- `feature/*` — isolated work via git worktrees when possible.
- Untracked code is not allowed beyond a single session; commit or `.gitignore` it.

## Cleanup Policy

- `tmp/` and `__pycache__` are auto-deletable.
- `.DS_Store` should not be committed.
- Archive old design docs to `docs/archives/` quarterly.

## Dependencies

- **Backend**: Python 3.9+, `requirements.txt` managed.
- **Frontend**: Node.js 18+, `frontend/package.json` managed.
- When adding runtime deps, update the relevant manifest immediately.

## Agent Checklist (before every task)

1. Read this file.
2. Check `git status`.
3. Run tests in the correct environment (`.venv` or system Python with deps).
4. Document structural changes here **before** applying them.
