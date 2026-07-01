---
tags: [fix, tws, key-event, channel, volume, next-prev, lr-diff, single-firmware, channel-aware, KEY_2]
date: 2026-05-04
status: COMPLETE & DEPLOYED
severity: FEATURE — Per-bud vol/track dispatch via runtime TWS channel detection; single firmware for both buds
files_changed: [apps/earphone/key_event_deal.c, apps/earphone/board/br28/board_jl7016g_hybrid.c]
related: [FIX-020, FIX-021]
---

# FIX-022 — Right Bud Vol Up / Left Bud Vol Down via Channel-Aware Dispatch

**Status:** COMPLETE & DEPLOYED  
**Build:** SUCCESS (0 errors, ota.bin generated)  
**Date:** May 4, 2026  
**Chip:** AC701N (BR28 core)  
**Board:** JL7016G Hybrid  

---

## Goal

| Physical touch | Desired action |
|----------------|----------------|
| Right bud HOLD KEY_2 | Volume Up |
| Left bud HOLD KEY_2 | Volume Down |
| Right bud DOUBLE-TAP KEY_2 | Next Track |
| Left bud DOUBLE-TAP KEY_2 | Previous Track |
| Either bud SHORT KEY_2 | Play / Pause / Answer / Hang Up |
| Either bud TRIPLE KEY_2 | Voice Assistant |

**Constraint:** Single firmware image flashed to both buds. No per-bud build required.

---

## Background

KEY_2 maps to PB4 (CH3, LP touch key, `key_value = 2`). After FIX-018 and FIX-019, PB1 (CH1) is GPIO-only; PB4 carries all music/volume controls.

As documented in FIX-021, `#if TCFG_RIGHT_BUD` splits in `key_table[]` are ineffective in TWS because the master evaluates its own table for all events including forwarded slave touches.

---

## Root Cause of "Both Do Same Thing"

Before this fix, the key table KEY_2 row mapped HOLD → `KEY_VOL_UP` unconditionally. When the left bud was touched and the event was forwarded to the master (right bud), the master looked up its own table and ran `volume_up()`. The physical origin of the touch — which bud generated it — was ignored.

### Why the compile-time approach failed (recap from FIX-021)

Attempting `#if TCFG_RIGHT_BUD` key table splits to route right bud → `KEY_VOL_UP` and left bud → `KEY_VOL_DOWN` failed completely: the master's table is used for all events, including forwarded slave touches. A left-bud touch forwarded to the right-bud master always hits the right bud's (master's) table.

### What the SDK provides for exactly this case

The SDK contains `key_tws_lr_diff_deal()` → `lr_diff_otp_deal()` — a runtime mechanism that resolves which physical bud was touched by combining two pieces of information:

1. **`tws_api_get_local_channel()`** — returns `'L'` or `'R'` depending on which channel the **currently-running master** is configured as
2. **`(u32)event->arg == KEY_EVENT_FROM_TWS`** — was this event forwarded from the peer, or generated locally?

Combining these two facts gives the physical origin of the touch:

```
If master is 'L':
    event->arg == KEY_EVENT_FROM_TWS  →  touch came from Right bud  (peer forwarded)
    event->arg != KEY_EVENT_FROM_TWS  →  touch came from Left bud   (local, master itself)

If master is 'R':
    event->arg == KEY_EVENT_FROM_TWS  →  touch came from Left bud   (peer forwarded)
    event->arg != KEY_EVENT_FROM_TWS  →  touch came from Right bud  (local, master itself)
```

This logic is **role-agnostic**: it gives the correct physical bud identity regardless of which bud won master election this session. This is critical because master/slave roles can flip between connection cycles on some SDK versions.

### Why the `lr_diff_otp_deal()` mapping was also inverted

The existing `lr_diff_otp_deal()` code had the R/L mapping backwards: `L=up, R=down` for volume and `L=next, R=prev` for track. This meant even calling `key_tws_lr_diff_deal()` would have produced the wrong result. The mapping was corrected as part of this fix.

---

## Fix Applied

### 1. `lr_diff_otp_deal()` — correct R/L → action mapping

**File:** `apps/earphone/key_event_deal.c`

```c
// BEFORE (L=up, R=down — inverted):
case ONE_KEY_CTL_VOL_UP_DOWN:
    if (channel == 'L') { volume_up(1); }
    else if (channel == 'R') { volume_down(1); }

// AFTER (R=up, L=down — correct):
case ONE_KEY_CTL_VOL_UP_DOWN:
    if (channel == 'R') { volume_up(1); }
    else if (channel == 'L') { volume_down(1); }
    else { volume_up(1); }   // fallback if standalone (no TWS)

// BEFORE (L=next, R=prev — inverted):
case ONE_KEY_CTL_NEXT_PREV:
    if (channel == 'L') { USER_CTRL_AVCTP_OPID_NEXT }
    else if (channel == 'R') { USER_CTRL_AVCTP_OPID_PREV }

// AFTER (R=next, L=prev — correct):
case ONE_KEY_CTL_NEXT_PREV:
    if (channel == 'R') { USER_CTRL_AVCTP_OPID_NEXT }
    else if (channel == 'L') { USER_CTRL_AVCTP_OPID_PREV }
    else { USER_CTRL_AVCTP_OPID_NEXT }   // fallback
```

### 2. `KEY_VOL_UP` handler — channel-aware for KEY_2 in TWS

```c
case KEY_VOL_UP:
#if TCFG_USER_TWS_ENABLE
    if (key->value == 2 && get_bt_tws_connect_status()) {
        key_tws_lr_diff_deal(event, ONE_KEY_CTL_VOL_UP_DOWN);  // R=up, L=down
    } else
#endif
    {
        volume_up(1);   // standalone or non-KEY_2 keys: always up
    }
    break;
```

The condition `key->value == 2` ensures only PB4 (KEY_2) gets this treatment. KEY_0 and KEY_1 LONG/HOLD events still call `volume_up()` directly.

### 3. `KEY_MUSIC_NEXT` handler — channel-aware for KEY_2 in TWS

```c
case KEY_MUSIC_NEXT:
#if TCFG_USER_TWS_ENABLE
    if (key->value == 2 && get_bt_tws_connect_status()) {
        key_tws_lr_diff_deal(event, ONE_KEY_CTL_NEXT_PREV);  // R=next, L=prev
        break;
    }
#endif
    // ... existing NEXT logic for all other keys ...
```

### 4. Key table KEY_2 row — single neutral row

```c
// Single row — no #if TCFG_RIGHT_BUD split needed:
{KEY_MUSIC_PP, KEY_VOL_UP, KEY_VOL_UP, KEY_NULL, KEY_MUSIC_NEXT, KEY_OPEN_SIRI},  //KEY_2
```

The handler differentiates by channel at runtime.

---

## Behaviour After Fix

| Physical touch | Action |
|----------------|--------|
| RIGHT bud HOLD | Volume Up (dispatched to `volume_up()`) |
| LEFT bud HOLD | Volume Down (dispatched to `volume_down()`) |
| RIGHT bud DOUBLE-TAP | Next Track |
| LEFT bud DOUBLE-TAP | Previous Track |
| Either bud SHORT | Play / Pause / Answer / Hang Up (context-aware, same as before) |
| Either bud TRIPLE | Voice Assistant (KEY_OPEN_SIRI) |
| Standalone (no TWS) | Right = HOLD → Vol Up (fallback) |

---

## Files Changed

| File | Change |
|------|--------|
| `apps/earphone/key_event_deal.c` | Fixed `lr_diff_otp_deal()` R/L mapping; added channel-aware dispatch to `KEY_VOL_UP` and `KEY_MUSIC_NEXT` handlers for `key->value == 2` |
| `apps/earphone/board/br28/board_jl7016g_hybrid.c` | Restored single neutral KEY_2 row (removed `#if TCFG_RIGHT_BUD` split) |

---

## Design Principle

> **Never use compile-time per-bud key table splits in a TWS system.** The master evaluates its own table for all events including slave-forwarded touches. Use `key_tws_lr_diff_deal()` for runtime L/R differentiation — it knows exactly which physical bud was touched regardless of master/slave role assignment.

---

## Volume Oscillation — Why `bt_tws_sync_volume()` Was Removed From `volume_up/down()`

During testing, adding `bt_tws_sync_volume()` inside `volume_up()` and `volume_down()` — alongside the existing `USER_CTRL_CMD_SYNC_VOL_INC/DEC` AVRCP path — caused **audible volume oscillation** during HOLD repeat events:

```
HOLD repeat fires every ~500 ms:
  volume_up() runs:
    1. app_audio_volume_up()           ← local DAC goes to N+1
    2. bt_tws_sync_volume()            ← pushes N+1 to peer via TWS data channel
    3. USER_CTRL_CMD_SYNC_VOL_INC ← sends AVRCP "volume up" to phone
       phone receives, increments phone vol from M to M+1
       phone sends AbsoluteVolume(M+1) back to BOTH buds
       each bud sets DAC to M+1  ← may differ from N+1 if phone and bud were not in sync

Result: each HOLD repeat produces two competing set-volume events,
one from the TWS data push and one from the phone's AbsoluteVolume response.
If M+1 ≠ N+1, the buds oscillate between the two levels on alternate repeats.
```

**Resolution:** `bt_tws_sync_volume()` calls were removed from `volume_up()` / `volume_down()`. The AVRCP path (`USER_CTRL_CMD_SYNC_VOL_INC/DEC`) is the only path active during key-press repeats. The TWS data-channel push via `bt_tws_sync_volume()` is still called at connection events and A2DP stream start — these are one-shot events where there is no competing AVRCP round-trip, so no oscillation occurs.

---

## Verification

Build: ✅ SUCCESS (0 errors)  
`ONE_KEY_CTL_DIFF_FUNC` must be enabled (set to 1) in the build config for `lr_diff_otp_deal()` to compile — verified enabled in this SDK.

---

## Related Documents

- [FIX-020 — TWS Volume Desync Between Buds](./FIX-020%20—%20TWS%20Volume%20Desync%20Between%20Buds.md) — `bt_tws_sync_volume()` made bidirectional
- [FIX-021 — Per-Bud Key Table Split Does Not Work in TWS](./FIX-021%20—%20Per-Bud%20Key%20Table%20Split%20Does%20Not%20Work%20in%20TWS.md) — why compile-time splits fail
