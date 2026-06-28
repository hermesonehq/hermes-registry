"""Shared helpers for the Hermes Registry tooling."""
from __future__ import annotations

import hashlib
import json
import os
import re
import struct
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas"

# Manifest-based types: folder layout is {type_dir}/{name}/manifest.json
MANIFEST_TYPES = {
    "mcp": "mcp",
    "agent": "agents",
    "workflow": "workflows",
}
SKILLS_DIR = REPO_ROOT / "skills"
MODELS_DIR = REPO_ROOT / "models"

ICON_MAX_BYTES = {".svg": 50 * 1024, ".png": 256 * 1024}

# Iconify icon id, e.g. "lucide:git-branch" or "mdi:robot-happy-outline".
# prefix:name, both lowercase alphanumeric segments joined by single hyphens.
ICONIFY_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*$")


def iconify_id(meta: dict) -> str | None:
    """Return a validated Iconify id from metadata.hermes.icon, else None."""
    icon = meta.get("icon")
    if isinstance(icon, str) and ICONIFY_RE.match(icon):
        return icon
    return None


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #
def iter_skill_files():
    """Yield every skills/<category>/<name>/SKILL.md path."""
    if not SKILLS_DIR.is_dir():
        return
    for skill_md in sorted(SKILLS_DIR.rglob("SKILL.md")):
        yield skill_md


def iter_manifest_files():
    """Yield (type, manifest_path) for every mcp/agent/workflow manifest."""
    for type_name, dir_name in MANIFEST_TYPES.items():
        base = REPO_ROOT / dir_name
        if not base.is_dir():
            continue
        for manifest in sorted(base.glob("*/manifest.json")):
            yield type_name, manifest


def iter_model_files():
    """Yield every models/<provider>.json path (flat, one file per provider)."""
    if not MODELS_DIR.is_dir():
        return
    for provider in sorted(MODELS_DIR.glob("*.json")):
        yield provider


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a SKILL.md file. Raises ValueError if absent."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("missing YAML frontmatter (file must start with '---')")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("unterminated frontmatter (need a closing '---')")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def hermes_meta(frontmatter: dict) -> dict:
    md = frontmatter.get("metadata") or {}
    if not isinstance(md, dict):
        return {}
    h = md.get("hermes") or {}
    return h if isinstance(h, dict) else {}


# --------------------------------------------------------------------------- #
# Checksums
# --------------------------------------------------------------------------- #
def folder_checksum(folder: Path) -> str:
    """Deterministic sha256 over all files in a folder (path + bytes)."""
    h = hashlib.sha256()
    for f in sorted(p for p in folder.rglob("*") if p.is_file()):
        rel = f.relative_to(folder).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(f.read_bytes())
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


# --------------------------------------------------------------------------- #
# Icons
# --------------------------------------------------------------------------- #
def find_icon(folder: Path, declared: str | None = None) -> Path | None:
    if declared:
        p = folder / declared
        return p if p.exists() else None
    for name in ("icon.svg", "icon.png"):
        p = folder / name
        if p.exists():
            return p
    return None


def png_dimensions(path: Path) -> tuple[int, int] | None:
    """Read (width, height) from a PNG IHDR chunk without external deps."""
    try:
        with path.open("rb") as fh:
            header = fh.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        width, height = struct.unpack(">II", header[16:24])
        return width, height
    except Exception:
        return None
