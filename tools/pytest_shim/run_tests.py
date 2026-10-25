#!/usr/bin/env python3
"""run_tests.py — execute a fleet repo's pytest-style suite with PyPI firewalled.

Accepts one or more test files and/or directories:

    python3 run_tests.py tests/
    python3 run_tests.py tests/test_a.py tests/test_b.py
    python3 run_tests.py -k deadband tests/

The pytest API is provided by the sibling ``pytest.py`` shim (see README.md).
Exit code is 0 only when every collected test passed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pytest as _shim  # noqa: E402

if __name__ == "__main__":
    sys.exit(_shim.main())
