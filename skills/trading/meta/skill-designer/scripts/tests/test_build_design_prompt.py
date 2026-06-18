"""Tests for build_design_prompt.py."""

from __future__ import annotations

from build_design_prompt import REFERENCES_DIR, build_prompt, load_references


def _make_idea(title: str = "test-skill", description: str = "A test skill") -> dict:
    return {"title": title, "description": description, "category": "testing"}


def test_build_prompt_uses_skill_name():
    """Prompt uses the --skill-name value for directory and frontmatter name."""
    refs = load_references(REFERENCES_DIR)
    prompt = build_prompt(_make_idea(), "my-custom-name", refs, [])

    assert "skills/my-custom-name/" in prompt
    assert "`my-custom-name`" in prompt
    assert "name:` field MUST be exactly `my-custom-name`" in prompt


def test_build_prompt_includes_refs():
    """All three reference file contents are embedded in the prompt."""
    refs = load_references(REFERENCES_DIR)

    # All 3 references should be loaded
    assert len(refs) == 3
    assert "skill-structure-guide.md" in refs
    assert "quality-checklist.md" in refs
    assert "skill-template.md" in refs

    prompt = build_prompt(_make_idea(), "test-skill", refs, [])

    # Each reference content should appear in the prompt
    assert "--- BEGIN skill-structure-guide.md ---" in prompt
    assert "--- BEGIN quality-checklist.md ---" in prompt
    assert "--- BEGIN skill-template.md ---" in prompt


def test_build_prompt_frontmatter_name_matches():
    """Prompt instructs Claude to set name: matching the skill_name."""
    refs = load_references(REFERENCES_DIR)
    prompt = build_prompt(_make_idea(), "exact-name-here", refs, ["existing-a", "existing-b"])

    # Should instruct the frontmatter name to match
    assert "exact-name-here" in prompt
    # Should list existing skills for deduplication
    assert "existing-a" in prompt
    assert "existing-b" in prompt
