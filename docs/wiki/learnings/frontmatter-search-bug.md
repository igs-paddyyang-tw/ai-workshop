---
title: "踩坑：搜尋抓到 frontmatter 當摘要"
type: article
tags: [wiki, search, frontmatter, bug]
created: 2026-07-09
updated: 2026-07-09
---

# 踩坑：搜尋抓到 frontmatter 當摘要

## 問題

Wiki 搜尋結果的 summary 顯示 `title: "Ocean King 捕魚機系列競品分析"` 而不是正文內容。

## 根因

`_extract_snippet()` 取「第一個包含關鍵字的行」，但 frontmatter 的 title 行也包含關鍵字。YAML frontmatter 被當正文搜尋了。

## 解法

```python
def _strip_frontmatter(content: str) -> str:
    if not content.startswith("---"):
        return content
    end = content.find("---", 3)
    return content[end + 3:].strip() if end != -1 else content
```

搜尋和摘要擷取都必須先呼叫 `_strip_frontmatter()` 再處理。

## 額外改進

- 擷取單位從「單行」改為「段落」（連續非空行）
- 選擇包含最多關鍵字的段落（而非第一行）
- 過濾中文停用詞（的、是、什麼）

## 教訓

- SKILL.md 規格要明確寫「跳過 frontmatter」
- 「從正文擷取」不能假設開發者知道要跳 YAML
- 規格越精確，實作越不容易跑偏
