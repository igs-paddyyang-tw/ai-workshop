-- 006_rename_pm_to_leader.sql: pm-agent → leader-agent
UPDATE agents
SET id = 'leader-agent', name = 'leader-agent',
    working_dir = 'agents/leader-agent', updated_at = datetime('now')
WHERE id = 'pm-agent';

UPDATE issues
SET assignee = 'leader-agent', updated_at = datetime('now')
WHERE assignee = 'pm-agent' AND status IN ('pending', 'assigned');
