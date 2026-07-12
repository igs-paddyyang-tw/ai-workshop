-- 003_memory.sql: Memory 子系統（情節記憶 + FTS5 全文索引）

CREATE TABLE IF NOT EXISTS memory_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent       TEXT NOT NULL,
    source      TEXT NOT NULL DEFAULT 'daily',
    date        TEXT NOT NULL,
    title       TEXT NOT NULL DEFAULT '',
    body        TEXT NOT NULL,
    tags        TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_memory_agent ON memory_entries(agent);
CREATE INDEX IF NOT EXISTS idx_memory_date ON memory_entries(date);

-- FTS5 虛擬表（全文搜尋）
CREATE VIRTUAL TABLE IF NOT EXISTS mem_fts USING fts5(
    agent, source, date, title, body, tags,
    content=memory_entries,
    content_rowid=id
);

-- 同步觸發器：INSERT
CREATE TRIGGER IF NOT EXISTS mem_fts_insert AFTER INSERT ON memory_entries BEGIN
    INSERT INTO mem_fts(rowid, agent, source, date, title, body, tags)
    VALUES (new.id, new.agent, new.source, new.date, new.title, new.body, new.tags);
END;

-- 同步觸發器：DELETE
CREATE TRIGGER IF NOT EXISTS mem_fts_delete BEFORE DELETE ON memory_entries BEGIN
    INSERT INTO mem_fts(mem_fts, rowid, agent, source, date, title, body, tags)
    VALUES ('delete', old.id, old.agent, old.source, old.date, old.title, old.body, old.tags);
END;

-- 同步觸發器：UPDATE
CREATE TRIGGER IF NOT EXISTS mem_fts_update AFTER UPDATE ON memory_entries BEGIN
    INSERT INTO mem_fts(mem_fts, rowid, agent, source, date, title, body, tags)
    VALUES ('delete', old.id, old.agent, old.source, old.date, old.title, old.body, old.tags);
    INSERT INTO mem_fts(rowid, agent, source, date, title, body, tags)
    VALUES (new.id, new.agent, new.source, new.date, new.title, new.body, new.tags);
END;
