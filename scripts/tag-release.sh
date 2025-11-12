#!/usr/bin/env bash

set -euo pipefail

ensure_git_clean() {
  if [[ -n $(git status --porcelain) ]]; then
    echo "Error: Git working directory is not clean. Please commit or stash your changes."
    exit 1
  fi
}

tag() {
  local tag

  actual_tag=$(git describe --tags --exact-match 2>/dev/null || true)
  if [[ "$actual_tag" != "${expected_tag}" ]]; then
    echo "Error: Current git tag is '$actual_tag', expected 'v$expected_tag'."
    exit 1
  fi
}

main() {
  local tag

  ensure_git_clean
  tag=$(poetry version -s)
  git tag "${tag}" -m "Create release version ${tag}"

  echo "✅ Git tag ${tag} created successfully."
}

main "$@"
