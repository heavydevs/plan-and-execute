#!/usr/bin/env python3
"""Regression: twice executing identical checks must be idempotent on Linux."""
from __future__ import annotations
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
module_path = ROOT / "run_task_checks.py"
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("pae_run_task_checks", module_path)
assert spec is not None and spec.loader is not None
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


def test_repeated_identical_result_is_idempotent():
    with TemporaryDirectory() as temp:
        repo = Path(temp)
        test = repo / "check.py"
        test.write_text("print('real successful check')\n", encoding="utf-8")
        entry = {"required_checks": [["python", "check.py"]]}
        with patch.object(checks.gate, "catalog", return_value={"015": entry}), \
             patch.object(checks.gate, "code_fingerprint", return_value="unchanged-code"), \
             patch.object(checks.dt, "datetime") as mocked_datetime:
            # The clock is frozen: both calls share the same second and PID.
            mocked_datetime.now.return_value = datetime(2026, 11, 22, 20, 0, tzinfo=timezone.utc)
            assert checks.run(repo, "015") == 0
            result = repo / checks.gate.OUTPUT / "015-checks.json"
            first_bytes = result.read_bytes()
            first = json.loads(first_bytes)
            assert first["checks"][0]["exit_code"] == 0
            assert (repo / first["checks"][0]["log"]).read_text().strip() == "real successful check"
            assert checks.run(repo, "015") == 0
            assert result.read_bytes() == first_bytes
            assert len(list((repo / checks.gate.OUTPUT / "logs" / "015").iterdir())) == 1
    print("Task checks replay/idempotence regression passed")


if __name__ == "__main__":
    test_repeated_identical_result_is_idempotent()
