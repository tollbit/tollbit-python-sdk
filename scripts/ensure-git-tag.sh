#!/usr/bin/env bash

set -euo pipefail

ensure_git_clean() {
  if [[ -n $(git status --porcelain) ]]; then
    echo "Error: Git working directory is not clean. Please commit or stash your changes."
    exit 1
  fi
}

ensure_git_tag() {
  local expected_tag="${1}"
  local actual_tag

  actual_tag=$(git describe --tags --exact-match 2>/dev/null || true)
  if [[ "$actual_tag" != "${expected_tag}" ]]; then
    echo "Error: Current git tag is '$actual_tag', expected 'v$expected_tag'."
    exit 1
  fi
}

main() {
  local expected_tag="${1}"

  ensure_git_clean
  ensure_git_tag "${expected_tag}"

  echo "✅ Git tag ${expected_tag} exists and working directory is clean."
}

main "$@"
