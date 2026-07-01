---
tags: [fix, in-ear, remap, event-filter, lp-touch]
date: 2026-04-27
status: COMPLETE & DEPLOYED
severity: EVENT-ROUTING BUG
---

# FIX-010 — In-Ear Remap Hook Active While Ear-Detect Disabled

## Summary

LP touch key events could still be intercepted by in-ear remap logic even when ear-detect feature was disabled for the board.

## Root Cause

In `apps/common/device/in_ear_detect/in_ear_detect.c`, remap hook compilation gate used only:

- `TCFG_EAR_DETECT_CTL_KEY`

It did not also require:

- `TCFG_EAR_DETECT_ENABLE`

## Fix Applied

Changed compile guard from:

- `#if TCFG_EAR_DETECT_CTL_KEY`

To:

- `#if (TCFG_EAR_DETECT_ENABLE && TCFG_EAR_DETECT_CTL_KEY)`

Also disabled board key gating for this profile:

- `TCFG_EAR_DETECT_CTL_KEY = 0`

## Files Changed

- `apps/common/device/in_ear_detect/in_ear_detect.c`
- `apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h`

## Verification

- Build success after patch.
- Remap interception no longer remains active when ear-detect is disabled.
