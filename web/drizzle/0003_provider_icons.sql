-- Provider logos. `icon` is the catalog-relative path (e.g. models/openai.svg);
-- the bytes are stored inline (base64) so the registry-icon route can serve them
-- the same way it serves entry icons, without exposing the filesystem.
ALTER TABLE providers ADD COLUMN IF NOT EXISTS icon text;
ALTER TABLE providers ADD COLUMN IF NOT EXISTS icon_b64 text;
ALTER TABLE providers ADD COLUMN IF NOT EXISTS icon_mime text;
