-- Hermes Registry initial schema.
-- Applied once by scripts/migrate.ts (tracked in schema_migrations).

CREATE TABLE IF NOT EXISTS entries (
  type            text NOT NULL,
  id              text NOT NULL,
  name            text NOT NULL,
  version         text NOT NULL,
  description     text NOT NULL DEFAULT '',
  category        text,
  tags            text[] NOT NULL DEFAULT '{}',
  author          text NOT NULL DEFAULT '',
  license         text,
  source          text,
  platforms       text[],
  path            text NOT NULL,
  icon            text,
  checksum        text,
  compatibility   jsonb,
  accepts_funding boolean NOT NULL DEFAULT false,
  downloads       integer NOT NULL DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  -- Weighted full-text vector (name > tags/category > description), maintained
  -- by a trigger. A STORED generated column can't be used here because the
  -- expression isn't considered immutable by Postgres.
  search_tsv tsvector,
  CONSTRAINT entries_pkey PRIMARY KEY (type, id)
);

CREATE OR REPLACE FUNCTION entries_tsv_update() RETURNS trigger AS $$
BEGIN
  NEW.search_tsv :=
    setweight(to_tsvector('english', coalesce(NEW.name, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.category, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.description, '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS entries_tsv_trg ON entries;
CREATE TRIGGER entries_tsv_trg BEFORE INSERT OR UPDATE ON entries
  FOR EACH ROW EXECUTE FUNCTION entries_tsv_update();

CREATE INDEX IF NOT EXISTS entries_type_idx   ON entries (type);
CREATE INDEX IF NOT EXISTS entries_name_idx   ON entries (name);
CREATE INDEX IF NOT EXISTS entries_search_idx ON entries USING gin (search_tsv);
CREATE INDEX IF NOT EXISTS entries_tags_idx   ON entries USING gin (tags);

CREATE TABLE IF NOT EXISTS entry_content (
  type        text NOT NULL,
  id          text NOT NULL,
  manifest    jsonb,
  markdown    text,
  frontmatter jsonb,
  workflow    jsonb,
  readme      text,
  icon_b64    text,
  icon_mime   text,
  CONSTRAINT entry_content_pkey PRIMARY KEY (type, id),
  CONSTRAINT entry_content_entry_fk FOREIGN KEY (type, id)
    REFERENCES entries (type, id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS providers (
  id          text PRIMARY KEY,
  name        text NOT NULL,
  homepage    text,
  description text,
  docs        text,
  api_base    text,
  env_key     text,
  models      jsonb NOT NULL DEFAULT '[]',
  sort_order  integer NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS download_events (
  id         bigserial PRIMARY KEY,
  entry_type text NOT NULL,
  entry_id   text NOT NULL,
  source     text NOT NULL DEFAULT 'cli',
  version    text,
  ip_hash    text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS download_events_entry_idx
  ON download_events (entry_type, entry_id, created_at);
