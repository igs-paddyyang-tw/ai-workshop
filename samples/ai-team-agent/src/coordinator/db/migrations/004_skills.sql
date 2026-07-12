-- 004_skills.sql: Skills 呼叫統計表

CREATE TABLE IF NOT EXISTS skill_calls (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id    TEXT NOT NULL,
    agent       TEXT NOT NULL DEFAULT 'system',
    success     INTEGER NOT NULL DEFAULT 1,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    params_hash TEXT DEFAULT '',
    called_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_skill_calls_skill ON skill_calls(skill_id);
CREATE INDEX IF NOT EXISTS idx_skill_calls_agent ON skill_calls(agent);
