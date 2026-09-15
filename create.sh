#!/usr/bin/env bash
# 一鍵產出可直接跑的 agent 專案。實作在 scripts/create_project.py。
#
#   ./create.sh bot  my-bot  --wheel ./ark_bot_agent-1.0.16-py3-none-any.whl
#   ./create.sh team my-team --preset gamedev
#   ./create.sh bot  my-bot  --dry-run
#
# preset：general（預設）· gamedev（workshop 貫穿案例）· minimal
set -euo pipefail
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts/create_project.py" "$@"
