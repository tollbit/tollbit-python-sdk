#! /usr/bin/env bash

set -euo pipefail

CHANGELOG_FILE="CHANGELOG.md"

ensure_version_in_change_log() {
  local expected_version="${1}"

  if ! grep -Eq "^##[[:space:]]*(\[)?${expected_version}(\])?" "${CHANGELOG_FILE}"; then
    echo "Error: ${CHANGELOG_FILE} does not contain an entry for version '$expected_version'."
    exit 1
  fi
}

main() {
  local expected_version="${1}"

  ensure_version_in_change_log "${expected_version}"

  echo "✅ Change log contains entry for version ${expected_version}."
}

main "$@"
