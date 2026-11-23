# AI Usage Log

This file tracks AI tools and language models used during the CoU AI Hackathon 2026, as required by competition rule 9 and rule 10.

## 2026-11-24 — Phase 1 & Phase 2 (Member C: Rules, Data, Evaluation)

- **AI Tools / Models:** Claude 3.7 / Claude 3.5 Sonnet / Copilot SDK
- **Member:** Member C (Athikul Islam)
- **Task Scope:**
  - Designed and drafted 15 deterministic red-flag rules in `catalog.yaml` and pure functions in `checks.py`.
  - Structured data files: `licensed_agencies.json`, `salary_benchmarks.json`, `fee_caps.json`, `high_risk_patterns.json`, `helplines.json`.
  - Curated 33 knowledge base passages in `backend/app/rag/kb/` with citations to ILO, BMET, and official government circulars.
  - Built synthetic evaluation dataset of 20 documents (8 legitimate, 12 scam offers) in English and Bangla.
  - Implemented evaluation runner (`eval/run_eval.py`) and data validation script (`scripts/validate_data.py`).
  - Authored unit test suites (`tests/test_rules.py`, `tests/test_rule_checks.py`).
- **Human Verification:** All logic, salary benchmark ranges, official citations in `SOURCES.md`, rule weights, and evaluation labels were manually verified and reviewed by team members.
