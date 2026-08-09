#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
echo 'Installed .githooks/pre-commit'
