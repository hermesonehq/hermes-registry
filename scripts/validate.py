#!/usr/bin/env python3
"""Validate every registry entry.

Skills  -> agentskills.io SKILL.md frontmatter rules.
MCP/Agent/Workflow -> JSON Schema in schemas/.

Exit code is non-zero if any ERROR is found. WARNINGs never fail the build.

Usage:  python scripts/validate.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    ICON_MAX_BYTES,
    ICONIFY_RE,
    SCHEMA_DIR,
    find_icon,
    folder_checksum,  # noqa: F401  (kept for symmetry / future use)
    hermes_meta,
    iter_manifest_files,
    iter_model_files,
    iter_skill_files,
    load_manifest,
    parse_frontmatter,
    png_dimensions,
    REPO_ROOT,
)

import jsonschema
from referencing import Registry, Resource

ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+([.-].+)?$")

errors: list[str] = []
warnings: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"ERROR  {where}: {msg}")


def warn(where: str, msg: str) -> None:
    warnings.append(f"WARN   {where}: {msg}")


# --------------------------------------------------------------------------- #
# Schema registry (resolves $ref between schema files by $id)
# --------------------------------------------------------------------------- #
def build_registry() -> tuple[Registry, dict]:
    resources = []
    by_type = {}
    for schema_path in SCHEMA_DIR.glob("*.json"):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
        if schema_path.name in ("mcp.schema.json", "agent.schema.json", "workflow.schema.json"):
            by_type[schema_path.stem.split(".")[0]] = schema
    return Registry().with_resources(resources), by_type


# --------------------------------------------------------------------------- #
# Icon checks (shared)
# --------------------------------------------------------------------------- #
def check_icon(where: str, folder: Path, declared: str | None) -> None:
    if declared and not (folder / declared).exists():
        err(where, f"icon '{declared}' declared but file not found")
        return
    icon = find_icon(folder, declared)
    if icon is None:
        return  # icons are optional
    ext = icon.suffix.lower()
    if ext not in ICON_MAX_BYTES:
        err(where, f"icon must be .svg or .png, got '{ext}'")
        return
    size = icon.stat().st_size
    if size > ICON_MAX_BYTES[ext]:
        err(where, f"icon {icon.name} is {size} bytes (> {ICON_MAX_BYTES[ext]} cap)")
    if ext == ".png":
        dims = png_dimensions(icon)
        if dims and (dims[0] != dims[1] or dims[0] < 256):
            warn(where, f"PNG icon should be square >=256x256, got {dims[0]}x{dims[1]}")


# --------------------------------------------------------------------------- #
# Skills
# --------------------------------------------------------------------------- #
def validate_skills() -> int:
    count = 0
    for skill_md in iter_skill_files():
        count += 1
        folder = skill_md.parent
        where = str(skill_md.relative_to(REPO_ROOT))
        try:
            fm = parse_frontmatter(skill_md)
        except ValueError as e:
            err(where, str(e))
            continue

        # Hard requirements
        for field in ("name", "description"):
            if not fm.get(field):
                err(where, f"missing required frontmatter field '{field}'")
        # Recommended
        for field in ("version", "author", "license", "platforms"):
            if not fm.get(field):
                warn(where, f"missing recommended field '{field}'")
        if fm.get("version") and not SEMVER_RE.match(str(fm["version"])):
            warn(where, f"version '{fm['version']}' is not semver")

        meta = hermes_meta(fm)
        # Registry extensions, if present, must be well-formed
        funding = meta.get("funding")
        if funding is not None:
            if not isinstance(funding, dict) or not funding.get("address"):
                err(where, "metadata.hermes.funding must have an 'address'")
            elif not ADDR_RE.match(str(funding["address"])):
                err(where, f"funding.address '{funding['address']}' is not a 0x..40-hex address")
        compat = meta.get("compatibility")
        if compat is not None:
            if not isinstance(compat, dict) or "hermes" not in compat or "desktop" not in compat:
                err(where, "metadata.hermes.compatibility must include 'hermes' and 'desktop'")
        icon_id = meta.get("icon")
        if icon_id is not None and not (
            isinstance(icon_id, str) and ICONIFY_RE.match(icon_id)
        ):
            err(where, f"metadata.hermes.icon '{icon_id}' is not a valid Iconify id "
                       "(expected 'prefix:name', e.g. 'lucide:git-branch')")

        icon_name = None
        for cand in ("icon.svg", "icon.png"):
            if (folder / cand).exists():
                icon_name = cand
        check_icon(where, folder, icon_name)
    return count


# --------------------------------------------------------------------------- #
# Manifest-based types
# --------------------------------------------------------------------------- #
def validate_manifests(registry: Registry, by_type: dict) -> int:
    count = 0
    validators = {
        t: jsonschema.Draft202012Validator(schema, registry=registry)
        for t, schema in by_type.items()
    }
    for type_name, manifest_path in iter_manifest_files():
        count += 1
        folder = manifest_path.parent
        where = str(manifest_path.relative_to(REPO_ROOT))
        try:
            data = load_manifest(manifest_path)
        except json.JSONDecodeError as e:
            err(where, f"invalid JSON: {e}")
            continue

        if data.get("type") != type_name:
            err(where, f"type '{data.get('type')}' does not match folder ({type_name})")

        validator = validators.get(type_name)
        if validator:
            for e in sorted(validator.iter_errors(data), key=lambda e: e.path):
                loc = "/".join(str(p) for p in e.path) or "(root)"
                err(where, f"{loc}: {e.message}")

        # entry file must exist
        entry = data.get("entry")
        if entry and not (folder / entry).exists():
            err(where, f"entry file '{entry}' not found")
        if type_name == "mcp" and data.get("transport") == "stdio":
            # command should resolve to something in the folder if it's a path
            pass

        check_icon(where, folder, data.get("icon"))
    return count


# --------------------------------------------------------------------------- #
# Model-provider catalogs (models/<provider>.json)
# --------------------------------------------------------------------------- #
def validate_models(registry: Registry) -> int:
    schema_path = SCHEMA_DIR / "models.schema.json"
    if not schema_path.exists():
        return 0
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, registry=registry)

    count = 0
    for provider_path in iter_model_files():
        count += 1
        where = str(provider_path.relative_to(REPO_ROOT))
        try:
            data = load_manifest(provider_path)
        except json.JSONDecodeError as e:
            err(where, f"invalid JSON: {e}")
            continue

        for e in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
            loc = "/".join(str(p) for p in e.path) or "(root)"
            err(where, f"{loc}: {e.message}")

        # id must match the filename stem (openai -> openai.json)
        stem = provider_path.stem
        if data.get("id") and data["id"] != stem:
            err(where, f"id '{data['id']}' does not match filename '{stem}'")

        # model names must be unique within a provider
        seen: set[str] = set()
        for m in data.get("models", []):
            mid = m.get("name")
            if mid in seen:
                err(where, f"duplicate model name '{mid}'")
            elif mid:
                seen.add(mid)

        check_icon(where, provider_path.parent, data.get("icon"))
    return count


def main() -> int:
    registry, by_type = build_registry()
    n_skills = validate_skills()
    n_manifests = validate_manifests(registry, by_type)
    n_models = validate_models(registry)

    for line in warnings:
        print(line)
    for line in errors:
        print(line)

    print()
    print(f"Validated {n_skills} skills + {n_manifests} manifests "
          f"+ {n_models} model providers "
          f"-> {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
