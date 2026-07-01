---
tags: [fix, lp-touch, pb4, algo, range, invalid-touch]
date: 2026-04-27
status: COMPLETE & DEPLOYED
severity: FUNCTIONAL BUG (valid touches rejected)
---

# FIX-009 — PB4 Touch Range Rejected By Low Algorithm Max

## Summary

PB4 produced repeated `invalid touch value` while real touch gestures were present.

## Root Cause

Touch algorithm range acceptance used low defaults (`TOUCH_RANGE_MAX = 500`) while PB4 long/hold values were much higher (around 3k-4k in logs).

## Fix Applied

1. Made touch range thresholds board-overridable in `cpu/br28/lp_touch_key.c`:
   - `TCFG_LP_TOUCH_ALOG_RANGE_MIN`
   - `TCFG_LP_TOUCH_ALOG_RANGE_MAX`
2. Set JL7016G hybrid values:
   - `TCFG_LP_TOUCH_ALOG_RANGE_MIN = 50`
   - `TCFG_LP_TOUCH_ALOG_RANGE_MAX = 5000`

## Files Changed

- `cpu/br28/lp_touch_key.c`
- `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

## Verification

- Build success after patch.
- PB4 long/hold ranges are now within accepted algorithm window for this board.
