# TQQQ / QQQ Exposure Policy

## Why TQQQ Needs A Different Policy

TQQQ targets 3x daily returns of the Nasdaq-100. Two structural facts make it more dangerous in distribution clusters than QQQ:

1. **Daily compounding decay.** In choppy or trending-down markets, 3x daily reset compounds losses geometrically. A -1% / -1% Nasdaq sequence translates to roughly -5.91% TQQQ, not -6%.
2. **Larger drawdowns from the same correction.** A 10% Nasdaq pullback typically produces a 25-35% TQQQ drawdown depending on path.

The IBD distribution day signal warns of institutional selling pressure that is not yet captured by trend/MA filters alone. When that signal fires, exposure should be cut faster on TQQQ than on QQQ.

## Policy Mapping

### TQQQ
| Risk | Recommended Action | Target Exposure | Trailing Stop Cap |
|------|--------------------|-----------------|-------------------|
| NORMAL | HOLD_OR_FOLLOW_BASE_STRATEGY | 100% | base |
| CAUTION | AVOID_NEW_ADDS | 75% | min(base, 7%) |
| HIGH | REDUCE_EXPOSURE | 50% | min(base, 5%) |
| SEVERE | CLOSE_TQQQ_OR_HEDGE | 25% | min(base, 3%) |

Alternative actions surfaced for TQQQ:
- HIGH → `SWITCH_PARTIAL_TO_QQQ`
- SEVERE → `SWITCH_TO_QQQ_OR_CASH`

### QQQ
| Risk | Recommended Action | Target Exposure | Trailing Stop Cap |
|------|--------------------|-----------------|-------------------|
| NORMAL | HOLD_OR_FOLLOW_BASE_STRATEGY | 100% | base |
| CAUTION | AVOID_NEW_ADDS | 100% (no cut) | min(base, 8%) |
| HIGH | REDUCE_EXPOSURE | 75% | min(base, 6%) |
| SEVERE | REDUCE_EXPOSURE_OR_HEDGE | 50% | min(base, 5%) |

QQQ does not need to drop to 25-50% at SEVERE because daily compounding hurts it less than TQQQ.

## Trailing Stop Cap Rule
The skill always uses **the tighter of** the user's `base_trailing_stop_pct` and the policy cap. It never widens the trailing stop. If the user provides a base stop already tighter than the policy cap (e.g. base 4%, policy cap 5% at HIGH), the user's value wins.

## What's Out Of Scope
- Position sizing in shares: use `position-sizer`.
- Tax-aware lot selection: not addressed by this skill.
- Hedge instrument selection: the action is named (`CLOSE_TQQQ_OR_HEDGE`) but instrument choice is up to the operator.

## Operator Notes
- The policy is deterministic. Adjust `risk_thresholds` in `config/default.yaml` to change the bands; changing exposure targets requires editing `exposure_policy.py` (deliberate, since the bands are calibrated to TQQQ leverage characteristics).
- The recommendation is just that — a recommendation. The skill never executes orders.
