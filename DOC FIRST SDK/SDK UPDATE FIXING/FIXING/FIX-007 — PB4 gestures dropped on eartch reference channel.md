---
tags: [fix, lp-touch, pb4, eartch, key-routing]
date: 2026-04-27
status: COMPLETE & DEPLOYED
severity: FUNCTIONAL BUG (gesture actions never execute)
---

# FIX-007 — PB4 Gestures Dropped On Eartch Reference Channel

## Summary

PB4 touch gestures were visible in LP logs (`CH3: FALLING/RAISING`, `notify key3 short event`), but media/call actions did not execute.

## Root Cause

In `cpu/br28/lp_touch_key.c`, `__ctmu_notify_key_event()` blocked key delivery for both eartch channels:

- primary eartch channel (`eartch_ch`)
- reference eartch channel (`eartch_ref_ch`)

On JL7016G hybrid, PB4 is `eartch_ref_ch = 3`, so PB4 key events were discarded before `key_event_deal.c`.

## Fix Applied

1. Added configurable reference-channel pass-through control in `cpu/br28/lp_touch_key.c`:
   - `TCFG_LP_EARTCH_REF_KEY_EVENT_ENABLE` (default `0`)
2. Kept primary channel reserved.
3. Made reference-channel blocking conditional on the new macro.
4. Enabled PB4 key pass-through on board config:
   - `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`
   - `#define TCFG_LP_EARTCH_REF_KEY_EVENT_ENABLE 1`

## Files Changed

- `cpu/br28/lp_touch_key.c`
- `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

## Verification

- Build success after patch.
- LP touch events on CH3 now reach app key mapping path instead of being dropped at driver notify gate.
