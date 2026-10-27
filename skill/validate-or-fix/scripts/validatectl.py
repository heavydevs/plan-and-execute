#!/usr/bin/env python3
"""Delegate to the canonical runtime (bundled for independent installations)."""
import runpy
import sys
from pathlib import Path

sys.dont_write_bytecode = True
skill = Path(__file__).resolve().parents[1]
locations = (skill / '_runtime' / 'scripts', skill.parent / 'plan-and-execute' / 'scripts')
runtime = next((p for p in locations if (p / 'validatectl.py').is_file()), None)
if runtime is None:
    raise SystemExit('Runtime missing: install with pae --skill validate-or-fix or use the complete skill.zip.')
sys.path.insert(0, str(runtime))
runpy.run_path(str(runtime / 'validatectl.py'), run_name='__main__')
