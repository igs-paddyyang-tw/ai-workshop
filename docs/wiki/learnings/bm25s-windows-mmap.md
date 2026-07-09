---
title: "踩坑：bm25s Windows mmap 鎖定"
type: article
tags: [bm25s, windows, mmap, bug]
created: 2026-07-09
updated: 2026-07-09
---

# 踩坑：bm25s Windows mmap 鎖定

## 問題

bm25s save 時用 numpy `.npy` 格式存檔。Windows 上如果舊索引被 mmap 鎖定（另一個 process 正在讀），`save()` 會拋 `OSError: [Errno 22] Invalid argument`。

## 症狀

- 第一次 rebuild 正常
- 第二次 rebuild（ingest 觸發）失敗
- Linux 上不會發生（mmap 行為不同）

## 解法

```python
# rebuild 前先清空舊目錄
if bm25_dir.exists():
    import shutil
    try:
        shutil.rmtree(bm25_dir)
    except OSError:
        pass

# save 加 try/except（索引仍在記憶體可用）
try:
    retriever.save(str(bm25_dir))
except OSError as e:
    log.warning("bm25s save failed: %s", e)
```

## 教訓

- bm25s 的持久化在 Windows 上不可靠，但記憶體索引仍可用
- 用 `.resolve()` 確保絕對路徑，避免相對路徑在不同 cwd 下失敗
