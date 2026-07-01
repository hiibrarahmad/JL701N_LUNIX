---
tags: [fix, lp-touch, ch3, long-press, hold, ctmu]
date: 2026-04-27
status: COMPLETE & DEPLOYED
severity: FUNCTIONAL BUG (long/hold dropped)
---

# FIX-008 — CH3 Long/Hold Suppressed By Long-By-Res Gate

## Summary

CH3 long/hold events were detected but frequently returned early with debug line:

- `long event return ! diff: X < cfg2/2: Y`

This prevented long/hold actions from executing.

## Root Cause

`lp_touch_key_check_long_click_by_ctmu_res()` enforced a strict filter under hardcoded `CTMU_CHECK_LONG_CLICK_BY_RES = 1`, causing valid long/hold sequences to be rejected.

## Fix Applied

1. Replaced hardcoded compile switch with board-controlled macro:
   - `TCFG_LP_TOUCH_CHECK_LONG_BY_RES_ENABLE`
2. Mapped driver gate to macro.
3. Disabled long-by-res suppression on JL7016G hybrid:
   - `#define TCFG_LP_TOUCH_CHECK_LONG_BY_RES_ENABLE 0`

## Files Changed

- `cpu/br28/lp_touch_key.c`
- `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

## Verification

- Build success after patch.
- CH3 long/hold path no longer exits early through `diff < cfg2/2` suppression on this board profile.
