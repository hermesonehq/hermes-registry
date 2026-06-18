#!/usr/bin/env python3
"""
Pattern Classifier - Categorizes VCP candidates by pattern type.

Separates structural quality (what kind of pattern is this?) from
execution state (can I enter now?). The two axes together give a
complete picture of each candidate.

Pattern Types (priority order, first match wins):
  Damaged         - Invalid/Damaged execution state; setup not viable
  Extended Leader - Valid VCP structure but already extended (>5% above pivot)
  Post-breakout   - Breaking out or just broke out (0-5% above pivot + volume)
  Textbook VCP    - Ideal pre-breakout setup (3+ contractions, tight, dry volume)
  VCP-adjacent    - Some VCP characteristics but not fully textbook-quality
"""

from typing import Optional


def classify_pattern(
    valid_vcp: bool,
    num_contractions: int,
    final_contraction_depth: Optional[float],
    execution_state: str,
    dry_up_ratio: Optional[float],
    wide_and_loose: bool = False,
) -> str:
    """
    Classify the pattern type for a VCP candidate.

    Decision tree (evaluated top-to-bottom, first match wins):
    1. execution_state in (Invalid, Damaged)           → Damaged
    2. valid_vcp + execution_state in (Overextended,
       Extended, Early-post-breakout, Breakout)        → Extended Leader / Post-breakout
    3. not valid_vcp + extended states                 → VCP-adjacent
    4. Pre-breakout + valid + textbook criteria        → Textbook VCP
    5. Pre-breakout + valid (not textbook)             → VCP-adjacent
    6. All other valid patterns                        → VCP-adjacent

    Textbook VCP criteria (ALL must be met):
    - valid_vcp is True
    - not wide_and_loose
    - num_contractions >= 3
    - final_contraction_depth <= 10.0%
    - dry_up_ratio <= 0.7 (significant volume dry-up)
    - execution_state == "Pre-breakout"

    Args:
        valid_vcp: Whether VCP contraction ratios passed validation
        num_contractions: Number of detected contractions
        final_contraction_depth: Depth (%) of the last contraction
        execution_state: Output of compute_execution_state() — e.g. "Pre-breakout"
        dry_up_ratio: Volume dry-up ratio (lower = more dry-up)
        wide_and_loose: True if final contraction is wide/deep (Phase 3 flag)

    Returns:
        Pattern type string: "Textbook VCP" | "VCP-adjacent" |
                             "Post-breakout" | "Extended Leader" | "Damaged"
    """
    # Rule 1: Damaged execution states — setup not viable
    if execution_state in ("Invalid", "Damaged"):
        return "Damaged"

    # Rules 2-3: Extended / post-breakout states
    if execution_state in ("Overextended", "Extended"):
        return "Extended Leader" if valid_vcp else "VCP-adjacent"

    if execution_state in ("Early-post-breakout", "Breakout"):
        return "Post-breakout" if valid_vcp else "VCP-adjacent"

    # Rules 4-6: Pre-breakout (or no-pivot) states
    if not valid_vcp or wide_and_loose:
        return "VCP-adjacent"

    # Check Textbook VCP criteria
    textbook = (
        num_contractions >= 3
        and (final_contraction_depth is None or final_contraction_depth <= 10.0)
        and (dry_up_ratio is not None and dry_up_ratio <= 0.7)
        and execution_state == "Pre-breakout"
    )

    return "Textbook VCP" if textbook else "VCP-adjacent"
