-- Iconify icon id for entries that use a named icon (e.g. skills declaring
-- `metadata.hermes.icon: "lucide:square-kanban"`) rather than a committed
-- icon.svg/png file. Distinct from `icon` (a repo-relative image path).
ALTER TABLE entries ADD COLUMN IF NOT EXISTS iconify text;
