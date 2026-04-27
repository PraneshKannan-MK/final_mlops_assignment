## Test Report

Run date: 2024-08-20
Command: `pytest tests/ -v --cov=src --cov=backend`

| ID | Test | Result |
|---|---|---|
| TC-001 | Missing sales_qty filled | PASS |
| TC-002 | Outlier capping applied | PASS |
| TC-003 | Sorted by date | PASS |
| TC-004 | Temporal features created | PASS |
| TC-005 | Lag features created | PASS |
| TC-006 | Schema validation rejects bad input | PASS |
| TC-007 | Valid predict returns 200 | PASS |
| TC-008 | Negative price returns 422 | PASS |
| TC-009 | Missing field returns 422 | PASS |
| TC-010 | /health returns 200 | PASS |
| TC-011 | /ready when model not loaded | PASS |
| TC-012 | /pipeline/status returns list | PASS |

**Total: 12 | Passed: 12 | Failed: 0**

## Acceptance Criteria — MET ✅

| Criteria | Target | Actual |
|---|---|---|
| All unit tests pass | 100% | 100% |
| Inference latency | < 200ms | ~7ms |
| API availability | /health returns 200 | ✅ |
| Model predicts positive demand | ≥ 0 | ✅ |