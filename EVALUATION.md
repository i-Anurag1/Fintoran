# Evaluation

`evals/benchmark.py` contains curated benchmark categories for transaction totals, budgets, anomalies, recurring payments, forecasts, market data, RAG, and adversarial prompts.

Target metrics:

- tool-selection correctness
- deterministic numerical correctness
- citation/source presence
- unsupported-value prevention
- user isolation
- retrieval relevance
- final-answer quality

The fixture file defines the benchmark cases. It does not claim benchmark scores until a benchmark runner executes them against a configured model and fixture dataset.

## Release audit

Run `python scripts/master_prompt_audit.py` before packaging. It checks required repository artifacts, Python syntax, CI markers, RAG re-index integrity, and secret patterns. It prints `MASTER_PROMPT_AUDIT: 100% STATIC REQUIREMENT COVERAGE` when the deterministic release checks pass.

The audit does not invent external-provider, model, browser, or Docker results. Those checks execute in CI when the required dependencies and container runtime are available.
