#!/bin/bash
# CORRECTED duplicate detector for the SuperInstance fleet.
#
# WHY THIS FILE EXISTS: the detector recorded in prior rounds —
#   GET /repos/{o}/{r}/git/trees/{branch}  ->  group repos by `.sha`
# — CAN NEVER FIRE. For a BRANCH ref, that endpoint's `.sha` is the COMMIT
# sha (unique per repo), not the tree sha (the content hash). Grouping by it
# returns "all repos are unique" every time, which reads as "no duplicates"
# but is actually a false negative.
#
# The content hash is `git rev-parse HEAD^{tree}` — over the git protocol,
# which costs ZERO api.github.com quota.
#
# usage: ./dupes_by_tree_sha.sh repo-a repo-b ...   (all SuperInstance/<name>)
set -u
for r in "$@"; do
  d=$(mktemp -d)
  if git clone --depth 1 --single-branch --quiet "https://github.com/SuperInstance/$r.git" "$d" 2>/dev/null; then
    printf "%-44s TREE=%s  files=%s\n" "$r" "$(git -C "$d" rev-parse HEAD^{tree})" \
      "$(git -C "$d" ls-tree -r --name-only HEAD | wc -l)"
  else
    printf "%-44s CLONE_FAIL\n" "$r"
  fi
  rm -rf "$d"
done
