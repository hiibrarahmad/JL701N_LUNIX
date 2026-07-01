---
title: PB4 Touch and In-Ear Behavior (JL7016G Hybrid)
tags: [jl7016g, touch, inear, pb4, sdk]
---

# PB4 Touch and In-Ear Behavior

## Scope
This note documents the implemented behavior for:
- LP touch in-ear polarity correction
- PB4 gesture actions (single, double, triple, hold)
- UART debug verification setup and expected logs
- Touch feedback/event-routing fixes required for PB4 to work while PB4 is eartch reference

## Files Updated
- apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h
- apps/earphone/board/br28/board_jl7016g_hybrid.c
- cpu/br28/lp_touch_key.c

## In-Ear Polarity Fix
A board-level switch is used to invert LP in-ear logical mapping when hardware reports opposite behavior.

Macro:
- TCFG_LP_EARTCH_LOGIC_INVERT

Values:
- 0: normal mapping
- 1: invert IN/OUT mapping

Current setting:
- TCFG_LP_EARTCH_LOGIC_INVERT = 0

This setting keeps normal mapping for current hardware behavior.

## PB4 Event-Routing Fix Chain (Critical)
The key reason PB4 gestures did not work was event filtering in the LP touch routing path while PB4 was also used as eartch reference channel.

Applied fixes:
- `TCFG_LP_TOUCH_ALOG_RANGE_MAX = 5000`
   - Prevents valid PB4 long/hold touch ranges from being rejected by touch algorithm range gate.
- `TCFG_LP_TOUCH_CHECK_LONG_BY_RES_ENABLE = 0`
   - Disables long-by-res suppression that dropped valid CH3 LONG/HOLD (`diff < cfg2/2`) events.
- `TCFG_EAR_DETECT_CTL_KEY = 0`
   - Disables in-ear key gating path that could drop LP touch key events in app flow.
- `TCFG_LP_EARTCH_REF_KEY_EVENT_ENABLE = 1`
   - Allows PB4 key events even though PB4 is configured as `eartch_ref_ch`.
- `in_ear_detect.c` guard hardening
   - `lp_touch_key_event_remap` now compiles only when `(TCFG_EAR_DETECT_ENABLE && TCFG_EAR_DETECT_CTL_KEY)`.

## PB4 Gesture Mapping
PB4 is LP touch channel 3 with key_value = 2 (KEY_2 row in key table).

Implemented mapping:
- Single tap: KEY_MUSIC_PP
  - Context behavior: answer incoming call, hang up active/outgoing call, otherwise play
- Double tap: KEY_MUSIC_NEXT
- Triple tap: KEY_OPEN_SIRI
- Hold: KEY_VOL_UP (continuous increase while hold events repeat)
- Long: KEY_VOL_UP

## Key Table Row
The active row for PB4 is KEY_2 in:
- apps/earphone/board/br28/board_jl7016g_hybrid.c

## UART Fix And Verification
UART was part of bring-up and validation.

Required terminal settings:
- `115200 8N1`
- no flow control

Expected tags:
- `[LP_KEY]` for CH3 transitions (`FALLING`, `RAISING`, `LONG`, `HOLD`)
- `key_event:` from app key handler for mapped actions

Important note:
- Mixed readable logs with random characters (for example `uuu`) usually indicates terminal framing/config issue, not total firmware UART failure.

## Quick Verify Checklist
1. Touch and hold PB4:
   - volume should increase repeatedly
2. Single tap PB4:
   - music play/pause in music scenario
   - call answer/hangup in call scenario
3. Double tap PB4:
   - next track
4. Triple tap PB4:
   - voice assistant trigger
5. In-ear logs and behavior:
   - with current invert setting (`0`), touch/release should align with physical expectation
6. UART key action confirmation:
   - verify `key_event:` lines are printed when PB4 gestures are performed

## If Polarity Looks Wrong Again
Toggle macro in:
- apps/earphone/board/br28/board_jl7016g_hybrid_cfg.h

Change:
- TCFG_LP_EARTCH_LOGIC_INVERT from 1 to 0 (or 0 to 1)

Then rebuild and retest.

## Current Working Macro Snapshot
- `TCFG_LP_EARTCH_LOGIC_INVERT = 0`
- `TCFG_LP_TOUCH_ALOG_RANGE_MIN = 50`
- `TCFG_LP_TOUCH_ALOG_RANGE_MAX = 5000`
- `TCFG_LP_TOUCH_CHECK_LONG_BY_RES_ENABLE = 0`
- `TCFG_EAR_DETECT_CTL_KEY = 0`
- `TCFG_LP_EARTCH_REF_KEY_EVENT_ENABLE = 1`
