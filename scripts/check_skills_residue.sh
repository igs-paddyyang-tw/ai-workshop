#!/usr/bin/env bash
# 檢查「上游已移除的 skill」是否還有複本殘留在本 repo。
#
# 為什麼需要：上游 ark-agent-skills 移除或改名 skill 之後，本 repo 的
# .kiro/skills/ 複本不會自己消失，agent 每次啟動照樣讀到它。
# 最典型的是 ark-news-daily（ark-daily-news 的舊單檔版）—— 兩者搶同一組
# 觸發詞，而沒有任何東西會報錯。2026-09-14 全庫實測有 241 處這種殘留。
#
# 判別「殘留」與「本 repo 自建」用上游 git 歷史，不是看名字猜：
#   路徑曾在上游出現過 = 殘留（可清，內容留在上游歷史）
#   從來沒出現過       = 自建（這裡是唯一一份，不可動）
#
# 用法：./scripts/check_skills_residue.sh      （唯讀，不改任何東西）
# Exit：有殘留回 1；上游庫沒 clone 時明說跳過並回 0。
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UPSTREAM="${ARK_SKILLS_UPSTREAM:-$HOME/kiro-cli/.kiro/skills}"
CHECKER="$UPSTREAM/scripts/check_consumers.py"

if [[ ! -f "$CHECKER" ]]; then
  echo "⏭  找不到 $CHECKER（上游 skill 庫未 clone？）→ 跳過，不視為通過"
  exit 0
fi
exec python3 "$CHECKER" --repo "$UPSTREAM" --consumers "$ROOT"
