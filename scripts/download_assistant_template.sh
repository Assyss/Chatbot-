#!/usr/bin/env bash
set -euo pipefail

curl -L \
  -o assistente-modelo.zip \
  https://github.com/esensato/icl-2026-01/raw/main/assistente-modelo.zip

echo "Template downloaded to assistente-modelo.zip"
