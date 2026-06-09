# Models

A **model** entry is a catalog of the models a provider serves — their context
windows, modalities, and capabilities — so Hermes can populate model pickers
without crawling each vendor's API at runtime.

## Folder layout

Unlike the other registry types, models are **one flat file per provider** — no
per-entry folder and no `manifest.json`. The file `id` must match the filename.

```
models/
└── <provider>.json     # provider + model catalog (validated against schemas/models.schema.json)
```

`scripts/build_index.py` rolls every `models/<provider>.json` up into a single
**generated** `models.json` at the repo root (with `path` + `checksum` added per
provider), so clients fetch one catalog file. Never hand-edit `models.json`.

## <provider>.json

```json
{
  "schemaVersion": "1",
  "type": "model-provider",
  "id": "openai",
  "name": "OpenAI",
  "version": "1.0.0",
  "homepage": "https://openai.com",
  "description": "GPT and o-series reasoning models from OpenAI.",
  "docs": "https://platform.openai.com/docs/models",
  "apiBase": "https://api.openai.com/v1",
  "envKey": "OPENAI_API_KEY",

  "models": [
    {
      "name": "gpt-4o",
      "label": "GPT-4o",
      "description": "Flagship multimodal model for everyday tasks.",
      "context": 128000,
      "maxOutput": 16384,
      "modalities": { "input": ["text", "image"], "output": ["text"] },
      "capabilities": [
        "tools",
        "vision",
        "streaming",
        "json_mode",
        "structured_outputs"
      ]
    },
    {
      "name": "o4-mini",
      "label": "o4-mini",
      "context": 200000,
      "maxOutput": 100000,
      "modalities": { "input": ["text", "image"], "output": ["text"] },
      "capabilities": ["tools", "reasoning", "vision", "structured_outputs"]
    }
  ]
}
```

### Provider fields

- `id` — lowercase slug, **must equal the filename** (`openai` → `models/openai.json`).
- `name`, `version`, `homepage` — required. `version` is semver; bump it when the model list changes.
- `description`, `docs`, `apiBase`, `icon` — optional.
- `envKey` — conventional env var for the API key (e.g. `OPENAI_API_KEY`). Only the _name_ is stored, never the key.
- `models` — non-empty array of model objects.

### Model fields

- `name` — identifier sent to the API (e.g. `gpt-4o`, `anthropic/claude-3.5-sonnet`). **Required.**
- `label` — display name (e.g. `GPT-4o`). **Required.**
- `context` — context window in tokens. **Required.**
- `maxOutput` — max output tokens per response.
- `modalities` — `{ "input": [...], "output": [...] }` from `text | image | audio | video | pdf | file`.
- `capabilities` — subset of `tools`, `vision`, `reasoning`, `streaming`, `json_mode`, `structured_outputs`, `prompt_caching`, `web_search`, `code_execution`, `fine_tuning`, `batch`, `audio`.
- `pricing`, `releaseDate`, `deprecated`, `aliases` — all optional. **Pricing is volatile** — confirm against the provider before relying on it.

## Checklist

- [ ] Filename matches `id` (e.g. `mistral` → `models/mistral.json`)
- [ ] `version` bumped (semver) when the model list changes
- [ ] File validates (`python scripts/validate.py`)
- [ ] Every model has `name`, `label`, and `context`
- [ ] `capabilities` values come from the allowed set
- [ ] No API keys or secrets committed
