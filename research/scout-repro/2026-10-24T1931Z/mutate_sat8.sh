#!/usr/bin/env bash
# Receipt: the constraint-theory-rust-python saturation floor is off by one,
# and the repo's own suite PINS the error (it goes RED when you fix it).
#
#   bash mutate_sat8.sh /path/to/constraint-theory-rust-python
#
# Requires a python3 with the repo's pure-Python fallback importable
# (no Rust toolchain needed — that is the point: the fallback is what CI
# step "Pure Python fallback tests" exercises).
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)          # absolute, BEFORE any cd
PYTEST="${PYTEST:-$HERE/../../../tools/pytest_shim/run_tests.py}"
REPO="${1:?usage: mutate_sat8.sh <path-to-repo>}"
[ -f "$PYTEST" ] || PYTEST="${PYTEST_ALT:-}"
cd "$REPO" || exit 1
F=python/flux_constraint/__init__.py
BLOB=$(git show HEAD:"$F" | md5sum | cut -d' ' -f1)
run() { find . -name '__pycache__' -not -path './.git/*' -exec rm -rf {} + 2>/dev/null
        for t in tests/test_python.py tests/test_edge_cases.py tests/test_presets.py; do
          printf "    %-24s " "$(basename "$t")"
          python3 "$PYTEST" "$t" 2>&1 | tail -1
        done; }
echo "    (runner: $PYTEST)"
echo "[1] BASELINE (pristine from git)"; run
echo; echo "[2] MUTATED: INT8_MIN -127 -> -128  (the TRUE int8 floor)"
sed -i 's/INT8_MIN, INT8_MAX = -127, 127/INT8_MIN, INT8_MAX = -128, 127/' "$F"
grep -c 'INT8_MIN, INT8_MAX = -128, 127' "$F" | xargs echo "    mutation present (count):"
run
echo; echo "[3] RESTORED from git"
git checkout -- "$F"
echo "    md5=$(md5sum "$F" | cut -d' ' -f1)  gitblob=$BLOB"
[ "$(md5sum "$F" | cut -d' ' -f1)" = "$BLOB" ] && echo "    RESTORE VERIFIED byte-identical to git blob" || echo "    !!! RESTORE MISMATCH"
run
