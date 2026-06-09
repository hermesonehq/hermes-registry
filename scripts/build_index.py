#!/usr/bin/env python3
"""Generate index.json, categories.json, and models.json from the registry.

Skills are read from SKILL.md frontmatter; MCP/agent/workflow entries from
their manifest.json; model providers from models/<provider>.json. Output is
deterministic (sorted) so diffs stay clean.

Usage:  python scripts/build_index.py
Env:    GENERATED_AT  ISO timestamp to stamp (defaults to now, UTC)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    MODELS_DIR,
    REPO_ROOT,
    SKILLS_DIR,
    find_icon,
    folder_checksum,
    hermes_meta,
    iter_manifest_files,
    iter_model_files,
    iter_skill_files,
    load_manifest,
    parse_frontmatter,
)

SCHEMA_VERSION = "1"


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def author_name(value) -> str | None:
    if isinstance(value, dict):
        return value.get("name")
    return value


def file_checksum(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def model_provider_entry(provider_path: Path) -> dict | None:
    """Load a models/<provider>.json file and enrich it for the catalog."""
    try:
        data = load_manifest(provider_path)
    except json.JSONDecodeError:
        return None
    icon = data.get("icon")
    entry = dict(data)
    entry["icon"] = rel(MODELS_DIR / icon) if icon else None
    entry["path"] = rel(provider_path)
    entry["checksum"] = file_checksum(provider_path)
    return entry


def skill_entry(skill_md: Path) -> dict | None:
    folder = skill_md.parent
    try:
        fm = parse_frontmatter(skill_md)
    except ValueError:
        return None
    meta = hermes_meta(fm)
    # Category = the first folder segment under skills/ (folder is the source of
    # truth, so nested skills like mlops/evaluation/* roll up to "mlops").
    parts = folder.relative_to(SKILLS_DIR).parts
    category = parts[0] if parts else folder.name
    icon = find_icon(folder)
    funding = meta.get("funding") or {}
    return {
        "id": fm.get("name") or folder.name,
        "type": "skill",
        "category": category,
        "name": fm.get("name") or folder.name,
        "version": str(fm.get("version")) if fm.get("version") else None,
        "description": fm.get("description", ""),
        "tags": meta.get("tags") or [],
        "author": author_name(fm.get("author")),
        "license": fm.get("license"),
        "source": meta.get("source") or fm.get("source"),
        "platforms": fm.get("platforms") or [],
        "path": rel(folder),
        "icon": rel(icon) if icon else None,
        "checksum": folder_checksum(folder),
        "compatibility": meta.get("compatibility"),
        "acceptsFunding": bool(funding.get("address")),
    }


def manifest_entry(type_name: str, manifest_path: Path) -> dict | None:
    folder = manifest_path.parent
    try:
        data = load_manifest(manifest_path)
    except json.JSONDecodeError:
        return None
    icon = find_icon(folder, data.get("icon"))
    funding = data.get("funding") or {}
    return {
        "id": data.get("id") or folder.name,
        "type": type_name,
        "category": None,
        "name": data.get("name") or folder.name,
        "version": data.get("version"),
        "description": data.get("description", ""),
        "tags": data.get("tags") or [],
        "author": author_name(data.get("author")),
        "license": data.get("license"),
        "source": data.get("source"),
        "path": rel(folder),
        "icon": rel(icon) if icon else None,
        "checksum": folder_checksum(folder),
        "compatibility": data.get("compatibility"),
        "acceptsFunding": bool(funding.get("address")),
    }


def main() -> int:
    entries: list[dict] = []

    for skill_md in iter_skill_files():
        e = skill_entry(skill_md)
        if e:
            entries.append(e)
    for type_name, manifest_path in iter_manifest_files():
        e = manifest_entry(type_name, manifest_path)
        if e:
            entries.append(e)

    entries.sort(key=lambda e: (e["type"], e["category"], e["id"]))

    generated = os.environ.get("GENERATED_AT") or datetime.now(timezone.utc).isoformat()

    index = {
        "schemaVersion": SCHEMA_VERSION,
        "generated": generated,
        "count": len(entries),
        "entries": entries,
    }

    # categories.json — taxonomy for the desktop gallery, grouped BY TYPE so a
    # count is never ambiguous. Only skills have sub-categories (their folder);
    # mcp/agent/workflow are flat (categories: []).
    type_counter = Counter(e["type"] for e in entries)
    types_block = []
    for type_name in sorted(type_counter):
        cats = Counter(
            e["category"] for e in entries if e["type"] == type_name and e.get("category")
        ) if type_name == "skill" else Counter()
        types_block.append({
            "type": type_name,
            "count": type_counter[type_name],
            "categories": [
                {"name": name, "count": count}
                for name, count in sorted(cats.items())
            ],
        })
    categories = {
        "schemaVersion": SCHEMA_VERSION,
        "generated": generated,
        "types": types_block,
    }

    # models.json — a dedicated catalog of model providers and the models they
    # serve, so clients fetch one file instead of crawling every provider file.
    providers = [p for p in (model_provider_entry(mp) for mp in iter_model_files()) if p]
    providers.sort(key=lambda p: p.get("id", ""))
    model_count = sum(len(p.get("models", [])) for p in providers)
    models = {
        "schemaVersion": SCHEMA_VERSION,
        "generated": generated,
        "providerCount": len(providers),
        "modelCount": model_count,
        "providers": providers,
    }

    (REPO_ROOT / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (REPO_ROOT / "categories.json").write_text(
        json.dumps(categories, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (REPO_ROOT / "models.json").write_text(
        json.dumps(models, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    by_type = ", ".join(f"{t}={n}" for t, n in sorted(type_counter.items()))
    n_skill_cats = sum(len(b["categories"]) for b in types_block)
    print(f"Wrote index.json ({len(entries)} entries: {by_type or 'none'})")
    print(f"Wrote categories.json ({n_skill_cats} skill categories)")
    print(f"Wrote models.json ({len(providers)} providers, {model_count} models)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
