-- 005_fix_pending_assigned.sql: 修正已有 assignee 但狀態仍為 pending 的任務
-- 將有指派對象的 pending 任務改為 assigned
UPDATE issues
SET status = 'assigned', updated_at = datetime('now')
WHERE status = 'pending' AND assignee IS NOT NULL AND assignee != '';
