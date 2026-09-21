"""Run the deterministic offline evaluation manifest."""
from __future__ import annotations
import json
try:
    from evals.benchmark import run_static_checks
except ModuleNotFoundError:
    from benchmark import run_static_checks

if __name__ == '__main__':
    print(json.dumps(run_static_checks(), indent=2))
