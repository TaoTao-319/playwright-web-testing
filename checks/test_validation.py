import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_results import verify_expected_failure


def make_result(**changes):
    result = {"tests": 1, "failures": 1, "errors": 0, "skipped": 0,
              "cases": [{"message": "Expected Wrong Products Title; Actual value: Products"}]}
    result.update(changes)
    return result


def test_accepts_only_planned_assertion_failure():
    verify_expected_failure(make_result())


@pytest.mark.parametrize("changes", [
    {"tests": 0, "failures": 0},
    {"failures": 0, "errors": 1},
    {"failures": 0, "skipped": 1},
    {"tests": 2, "failures": 2},
    {"cases": [{"message": "Timeout waiting for login page"}]},
    {"cases": [{"message": "Wrong Products Title; Actual value: Login"}]},
])
def test_rejects_unrelated_or_incomplete_failure(changes):
    with pytest.raises(ValueError):
        verify_expected_failure(make_result(**changes))
